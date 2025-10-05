"""
Database seeding script - populates the database with sample data.
This script is fully self-contained:
- Downloads latest GTFS data from Krakow transport
- Removes old database if it exists
- Creates new database with proper structure
- Initializes vehicle types
- Populates with sample data
- Cleans up downloaded GTFS files

Run this script:
    python seed_database.py              # Downloads and cleans up GTFS data
    python seed_database.py --keep-gtfs  # Keep GTFS data after seeding
"""

import csv
import os
import shutil
import sqlite3
import sys
import zipfile
from datetime import datetime, time, timedelta
from random import choice, randint, uniform
from urllib.request import urlretrieve

import pandas as pd
from database import SessionLocal, init_db
from db_models import (
    JourneyData,
    Report,
    Route,
    RouteSegment,
    RouteStop,
    ShapePoint,
    Stop,
    Ticket,
    User,
    UserJourney,
    UserJourneyStop,
    Vehicle,
    VehicleTrip,
    VehicleType,
)
from init_data import VEHICLE_TYPES
from tqdm import tqdm

# ============================================================================
# GTFS DATA HELPERS
# ============================================================================


def parse_gtfs_time(time_str):
    """
    Convert GTFS time string to datetime object.

    GTFS times can exceed 24:00:00 for trips that continue after midnight.
    For example, '25:30:00' means 1:30 AM the next day.

    Args:
        time_str: Time string in format 'HH:MM:SS'

    Returns:
        datetime object or None if input is invalid
    """
    if not time_str or pd.isna(time_str):
        return None

    # Parse time components
    parts = time_str.strip().split(":")
    hours = int(parts[0])
    minutes = int(parts[1])
    seconds = int(parts[2])

    # Handle times that exceed 24 hours (next day service)
    days = hours // 24
    hours = hours % 24

    # Create datetime using today as base reference
    base_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    result = base_date + timedelta(
        days=days, hours=hours, minutes=minutes, seconds=seconds
    )

    return result


def get_vehicle_type_mapping(vehicle_types):
    """
    Create a mapping of vehicle type codes to vehicle type objects.

    Returns:
        dict: Mapping of folder names to (folder_path, vehicle_type) tuples
    """
    bus_type = next(vt for vt in vehicle_types if vt.code == "BUS")
    tram_type = next(vt for vt in vehicle_types if vt.code == "TRAM")
    train_type = next(vt for vt in vehicle_types if vt.code == "TRAIN")

    return [
        ("GTFS_KRK_A", bus_type),  # Buses
        ("GTFS_KRK_T", tram_type),  # Trams
        ("GTFS_KRK_M", train_type),  # Metro/Train
    ]


# ============================================================================
# GTFS DATA DOWNLOAD & CLEANUP
# ============================================================================

# URLs for GTFS data feeds
GTFS_URLS = [
    ("https://gtfs.ztp.krakow.pl/GTFS_KRK_A.zip", "GTFS_KRK_A"),  # Buses
    ("https://gtfs.ztp.krakow.pl/GTFS_KRK_M.zip", "GTFS_KRK_M"),  # Metro/Train
    ("https://gtfs.ztp.krakow.pl/GTFS_KRK_T.zip", "GTFS_KRK_T"),  # Trams
]


def download_gtfs_data():
    """
    Download and extract GTFS data from Krakow transport authority.

    Downloads ZIP files and extracts them to local folders.
    Skips download if folder already exists.
    """
    print("\n📥 Downloading GTFS data...")

    for url, folder_name in GTFS_URLS:
        if os.path.exists(folder_name):
            print(f"   • {folder_name} already exists, skipping download")
            continue

        zip_filename = f"{folder_name}.zip"

        try:
            print(f"   • Downloading {folder_name}...")
            urlretrieve(url, zip_filename)

            print(f"   • Extracting {folder_name}...")
            with zipfile.ZipFile(zip_filename, "r") as zip_ref:
                zip_ref.extractall(folder_name)

            # Remove ZIP file after extraction
            os.remove(zip_filename)
            print(f"   ✓ {folder_name} ready")

        except Exception as e:
            print(f"   ❌ Failed to download {folder_name}: {e}")
            # Clean up partial downloads
            if os.path.exists(zip_filename):
                os.remove(zip_filename)
            if os.path.exists(folder_name):
                shutil.rmtree(folder_name)
            raise

    print("   ✓ All GTFS data downloaded and extracted")


def cleanup_gtfs_data():
    """
    Remove downloaded GTFS data folders.

    Called after database seeding is complete to clean up disk space.
    """
    print("\n🧹 Cleaning up GTFS data...")

    for _, folder_name in GTFS_URLS:
        if os.path.exists(folder_name):
            try:
                shutil.rmtree(folder_name)
                print(f"   • Removed {folder_name}")
            except Exception as e:
                print(f"   ⚠️  Failed to remove {folder_name}: {e}")

    print("   ✓ GTFS data cleanup complete")


# ============================================================================
# DATABASE SETUP
# ============================================================================


def remove_old_database():
    """Remove old database file if it exists."""
    db_file = "transportation.db"
    if os.path.exists(db_file):
        print(f"🗑️  Removing old database: {db_file}")
        os.remove(db_file)
        print("   ✓ Old database removed")
    else:
        print("   ℹ️  No existing database found")


def create_vehicle_types(db):
    """Create system vehicle types."""
    print("\n🚗 Creating vehicle types...")

    vehicle_types = []
    for vt_data in VEHICLE_TYPES:
        vt = VehicleType(**vt_data)
        db.add(vt)
        vehicle_types.append(vt)

    db.commit()
    print(f"   ✓ Created {len(vehicle_types)} vehicle types")
    return vehicle_types


def create_stops(db, vehicle_types):
    """Create stops (bus/tram/train) from GTFS stops.txt files."""
    print("\n🚏 Creating stops from GTFS...")

    # Find vehicle types by code
    bus_type = next(vt for vt in vehicle_types if vt.code == "BUS")
    tram_type = next(vt for vt in vehicle_types if vt.code == "TRAM")
    train_type = next(vt for vt in vehicle_types if vt.code == "TRAIN")

    # Map folder to vehicle type
    feeds = [
        ("GTFS_KRK_A", bus_type),
        ("GTFS_KRK_T", tram_type),
        ("GTFS_KRK_M", train_type),
    ]

    stops = []
    total = 0

    for folder, vtype in feeds:
        path = os.path.join(folder, "stops.txt")
        if not os.path.isfile(path):
            print(f"   • Skipping {folder}: no stops.txt found")
            continue

        print(f"   • Loading stops from {folder}...")
        with open(path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                stop_id = row.get("stop_id")
                stop_name = f"{row.get('stop_name')} {row.get('stop_desc', '')}".strip()
                lat = row.get("stop_lat")
                lon = row.get("stop_lon")

                # Skip incomplete records
                if not (stop_id and stop_name and lat and lon):
                    continue

                stop = Stop(
                    id=stop_id,
                    name=stop_name.strip(),
                    vehicle_type_id=vtype.id,
                    latitude=float(lat),
                    longitude=float(lon),
                    created_at=datetime.utcnow(),
                )
                db.add(stop)
                stops.append(stop)
                total += 1

    db.commit()
    print(f"   ✓ Created {len(stops)} stops (from {total} total rows read)")
    return stops


def create_users(db):
    """Create sample users with different roles."""
    print("\n👥 Creating users...")

    users_data = [
        {
            "name": "user1",
            "email": "user1@example.com",
            "hashed_password": "user1",
            "role": "PASSENGER",
            "verified": True,
            "reputation_points": 0,
            "badge": None,
            "verified_reports_count": 0,
            "is_disabled": False,
            "is_super_sporty": False,
        },
        {
            "name": "user2",
            "email": "user2@example.com",
            "hashed_password": "user2",
            "role": "PASSENGER",
            "verified": True,
            "reputation_points": 0,
            "badge": None,
            "verified_reports_count": 0,
            "is_disabled": True,
            "is_super_sporty": False,
        },
        {
            "name": "user3",
            "email": "user3@example.com",
            "hashed_password": "user3",
            "role": "PASSENGER",
            "verified": True,
            "reputation_points": 0,
            "badge": None,
            "verified_reports_count": 0,
            "is_disabled": False,
            "is_super_sporty": True,
        },
        {
            "name": "driv",
            "email": "driv@example.com",
            "hashed_password": "driv",
            "role": "DRIVER",
            "verified": True,
            "reputation_points": 0,
            "badge": None,
            "verified_reports_count": 0,
            "is_disabled": False,
            "is_super_sporty": False,
        },
        {
            "name": "disp",
            "email": "disp@example.com",
            "hashed_password": "disp",
            "role": "DISPATCHER",
            "verified": True,
            "reputation_points": 0,
            "badge": None,
            "verified_reports_count": 0,
            "is_disabled": False,
            "is_super_sporty": False,
        },
        {
            "name": "admin",
            "email": "admin@example.com",
            "hashed_password": "admin",
            "role": "ADMIN",
            "verified": True,
            "reputation_points": 0,
            "badge": None,
            "verified_reports_count": 0,
            "is_disabled": False,
            "is_super_sporty": False,
        },
    ]

    users = []
    for user_data in users_data:
        user = User(**user_data)
        db.add(user)
        users.append(user)

    db.commit()
    print(f"   ✓ Created {len(users)} users")
    return users


def create_vehicles(db, vehicle_types, users):
    """Create sample vehicles."""
    print("\n🚗 Creating vehicles...")

    # Find vehicle types by code
    bus_type = next(vt for vt in vehicle_types if vt.code == "BUS")
    tram_type = next(vt for vt in vehicle_types if vt.code == "TRAM")
    train_type = next(vt for vt in vehicle_types if vt.code == "TRAIN")

    # Find drivers
    drivers = [u for u in users if u.role == "DRIVER"]

    vehicles_data = [
        {
            "vehicle_type_id": bus_type.id,
            "registration_number": "BUS-101",
            "capacity": 80,
            "last_inspection_date": datetime.now() - timedelta(days=30),
            "issues": None,
            "current_driver_id": drivers[0].id,
        },
        {
            "vehicle_type_id": bus_type.id,
            "registration_number": "BUS-102",
            "capacity": 80,
            "last_inspection_date": datetime.now() - timedelta(days=15),
            "issues": "Minor brake wear",
            "current_driver_id": drivers[0].id,
        },
        {
            "vehicle_type_id": bus_type.id,
            "registration_number": "BUS-103",
            "capacity": 60,
            "last_inspection_date": datetime.now() - timedelta(days=45),
            "issues": "Tire pressure low, AC not working",
            "current_driver_id": None,
        },
        {
            "vehicle_type_id": tram_type.id,
            "registration_number": "TRAM-205",
            "capacity": 150,
            "last_inspection_date": datetime.now() - timedelta(days=20),
            "issues": None,
            "current_driver_id": drivers[0].id,
        },
        {
            "vehicle_type_id": tram_type.id,
            "registration_number": "TRAM-206",
            "capacity": 150,
            "last_inspection_date": datetime.now() - timedelta(days=10),
            "issues": None,
            "current_driver_id": drivers[0].id,
        },
        {
            "vehicle_type_id": tram_type.id,
            "registration_number": "TRAM-207",
            "capacity": 180,
            "last_inspection_date": datetime.now() - timedelta(days=5),
            "issues": "Door sensor malfunction",
            "current_driver_id": None,
        },
        {
            "vehicle_type_id": train_type.id,
            "registration_number": "TRAIN-S1",
            "capacity": 300,
            "last_inspection_date": datetime.now() - timedelta(days=7),
            "issues": None,
            "current_driver_id": None,
        },
        {
            "vehicle_type_id": train_type.id,
            "registration_number": "TRAIN-S2",
            "capacity": 300,
            "last_inspection_date": datetime.now() - timedelta(days=60),
            "issues": "Engine oil needs replacement, pantograph inspection due",
            "current_driver_id": None,
        },
    ]

    vehicles = []
    for vehicle_data in vehicles_data:
        vehicle = Vehicle(**vehicle_data)
        db.add(vehicle)
        vehicles.append(vehicle)

    db.commit()
    print(f"   ✓ Created {len(vehicles)} vehicles")
    return vehicles


def create_routes(db, stops, vehicle_types):
    """
    Create routes from GTFS trip data.

    A route represents a single trip with a start/end stop and scheduled times.
    Extracts trip information from GTFS stop_times.txt files.

    Returns:
        tuple: (routes list, route_trip_mapping dict)
            - routes: List of created Route objects
            - route_trip_mapping: Maps GTFS trip_id to Route object
    """
    print("\n🚌 Creating routes from GTFS data...")

    feeds = get_vehicle_type_mapping(vehicle_types)
    routes = []
    route_trip_mapping = {}
    total_created = 0

    for folder, vehicle_type in feeds:
        total_created += _process_routes_for_feed(
            db, folder, vehicle_type, routes, route_trip_mapping
        )

    # Commit routes so they get database IDs assigned
    db.commit()

    print(f"   ✓ Created {len(routes)} routes (from {total_created} GTFS trips)")
    return routes, route_trip_mapping


def _process_routes_for_feed(db, folder, vehicle_type, routes, route_trip_mapping):
    """
    Process routes from a single GTFS feed folder.

    Returns:
        int: Number of routes created
    """
    stop_times_path = os.path.join(folder, "stop_times.txt")

    if not os.path.isfile(stop_times_path):
        print(f"   • Skipping {folder}: stop_times.txt not found")
        return 0

    print(f"   • Processing routes from {folder}...")

    # Load and aggregate trip data
    stop_times_df = pd.read_csv(stop_times_path)
    trip_aggregates = (
        stop_times_df.sort_values(["trip_id", "stop_sequence"])
        .groupby("trip_id")
        .agg(
            starting_stop=("stop_id", "first"),
            ending_stop=("stop_id", "last"),
            scheduled_arrival=("arrival_time", "last"),
            scheduled_departure=("departure_time", "first"),
        )
        .reset_index()
    )

    # Filter for valid trips (both stops exist in our database for this vehicle type)
    valid_trips = _get_valid_trips(trip_aggregates, vehicle_type.id)

    # Create Route objects
    count = 0
    for trip_data in tqdm(valid_trips):
        trip_id, start_stop_id, end_stop_id, arrival_time, departure_time = trip_data

        route = Route(
            vehicle_id=vehicle_type.id,
            starting_stop_id=start_stop_id,
            ending_stop_id=end_stop_id,
            scheduled_arrival=parse_gtfs_time(arrival_time),
            scheduled_departure=parse_gtfs_time(departure_time),
            current_status="PLANNED",
        )

        db.add(route)
        routes.append(route)
        route_trip_mapping[trip_id] = route
        count += 1

    return count


def _get_valid_trips(trip_aggregates, vehicle_type_id):
    """
    Filter trips to only include those with valid stops in the database.

    Uses SQLite to efficiently join trip data with existing stops.

    Returns:
        list: List of tuples (trip_id, start_stop, end_stop, arrival, departure)
    """
    conn = sqlite3.connect("transportation.db")

    with conn:
        # Create temporary table
        trip_aggregates.to_sql(
            "temp_trip_stops", conn, if_exists="replace", index=False
        )

        # Query for trips where both start and end stops exist
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT 
                t.trip_id, 
                t.starting_stop, 
                t.ending_stop, 
                t.scheduled_arrival, 
                t.scheduled_departure
            FROM temp_trip_stops t
            INNER JOIN stops s1 ON t.starting_stop = s1.id
            INNER JOIN stops s2 ON t.ending_stop = s2.id
            WHERE s1.vehicle_type_id = ? 
              AND s2.vehicle_type_id = ?
        """,
            (vehicle_type_id, vehicle_type_id),
        )

        return cursor.fetchall()

    conn.close()


def create_route_stops(db, routes, stops, vehicle_types, route_trip_mapping):
    """
    Create route-stop associations from GTFS data.

    For each route, creates RouteStop entries representing each stop along the way
    with scheduled arrival/departure times and sequence order.

    Args:
        route_trip_mapping: Maps GTFS trip_id to Route objects (from create_routes)

    Returns:
        list: Created RouteStop objects
    """
    print("\n📍 Creating route stops from GTFS data...")

    feeds = get_vehicle_type_mapping(vehicle_types)
    route_stops = []
    total_created = 0

    for folder, vehicle_type in feeds:
        stops_created, trips_skipped = _process_route_stops_for_feed(
            db, folder, vehicle_type, route_trip_mapping, route_stops
        )
        total_created += stops_created

        if trips_skipped > 0:
            print(f"   ⚠️  Skipped {trips_skipped} trips with no matching route")

    db.commit()
    print(f"   ✓ Created {total_created} route stops")
    return route_stops


def _process_route_stops_for_feed(
    db, folder, vehicle_type, route_trip_mapping, route_stops
):
    """
    Process route stops from a single GTFS feed folder.

    Returns:
        tuple: (stops_created, trips_skipped)
    """
    stop_times_path = os.path.join(folder, "stop_times.txt")

    if not os.path.isfile(stop_times_path):
        print(f"   • Skipping {folder}: stop_times.txt not found")
        return 0, 0

    print(f"   • Processing route stops from {folder}...")

    # Load stop times data
    stop_times_df = pd.read_csv(stop_times_path)

    # Get valid stop times (stops that exist in our database)
    valid_stop_times = _get_valid_stop_times(stop_times_df, vehicle_type.id)

    # Create RouteStop objects
    stops_created = 0
    trips_skipped = set()
    current_trip_id = None
    current_route = None

    for stop_data in tqdm(valid_stop_times):
        trip_id, stop_id, arrival_time, departure_time, stop_sequence = stop_data

        # Check if we've moved to a new trip
        if trip_id != current_trip_id:
            current_trip_id = trip_id
            current_route = route_trip_mapping.get(trip_id)

            # Track trips that don't have a corresponding route
            if not current_route:
                trips_skipped.add(trip_id)

        # Only create route stop if we have a valid route
        if current_route:
            route_stop = RouteStop(
                route_id=current_route.id,
                stop_id=stop_id,
                scheduled_arrival=parse_gtfs_time(arrival_time),
                scheduled_departure=parse_gtfs_time(departure_time),
                stop_sequence=stop_sequence,
            )

            db.add(route_stop)
            route_stops.append(route_stop)
            stops_created += 1

    return stops_created, len(trips_skipped)


def _get_valid_stop_times(stop_times_df, vehicle_type_id):
    """
    Filter stop times to only include stops that exist in the database.

    Uses SQLite to efficiently join stop_times with existing stops.

    Returns:
        list: List of tuples (trip_id, stop_id, arrival_time, departure_time, stop_sequence)
    """
    conn = sqlite3.connect("transportation.db")

    with conn:
        # Create temporary table
        stop_times_df.to_sql("temp_stop_times", conn, if_exists="replace", index=False)

        # Query for stop times where the stop exists in our database
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT 
                st.trip_id, 
                st.stop_id, 
                st.arrival_time, 
                st.departure_time, 
                st.stop_sequence
            FROM temp_stop_times st
            INNER JOIN stops s ON st.stop_id = s.id
            WHERE s.vehicle_type_id = ?
            ORDER BY st.trip_id, st.stop_sequence
        """,
            (vehicle_type_id,),
        )

        return cursor.fetchall()

    conn.close()


def create_journeys(db, routes, users):
    """Create sample journeys."""
    print("\n🚀 Creating journeys...")

    drivers = [u for u in users if u.role == "DRIVER"]
    vehicle_trips = []

    trip_configs = [
        {
            "route": routes[0],
            "driver": drivers[0],
            "status": "IN_PROGRESS",
            "has_departure": True,
            "at_stop": True,
        },
        {
            "route": routes[1],
            "driver": drivers[0],
            "status": "PLANNED",
            "has_departure": False,
            "at_stop": False,
        },
        {
            "route": routes[2],
            "driver": drivers[0],
            "status": "DELAYED",
            "has_departure": True,
            "at_stop": True,
        },
        {
            "route": routes[3],
            "driver": None,
            "status": "PLANNED",
            "has_departure": False,
            "at_stop": False,
        },
        {
            "route": routes[4],
            "driver": drivers[0],
            "status": "COMPLETED",
            "has_departure": True,
            "at_stop": False,
        },
    ]

    now = datetime.now()

    for config in trip_configs:
        vehicle_trip = VehicleTrip(
            route_id=config["route"].id,
            driver_id=config["driver"].id if config["driver"] else None,
            actual_departure=(
                now - timedelta(minutes=30) if config["has_departure"] else None
            ),
            last_stop_arrival=(
                now - timedelta(minutes=10)
                if config["at_stop"] and config["status"] == "IN_PROGRESS"
                else (
                    now - timedelta(minutes=5)
                    if config["status"] == "COMPLETED"
                    else None
                )
            ),
            next_stop_departure=(
                now + timedelta(minutes=5)
                if config["at_stop"] and config["status"] == "IN_PROGRESS"
                else None
            ),
            current_status=config["status"],
        )
        db.add(vehicle_trip)
        vehicle_trips.append(vehicle_trip)

    db.commit()
    print(f"   ✓ Created {len(vehicle_trips)} vehicle trips")
    return vehicle_trips


def create_route_segments(db, stops):
    """Create route segments between consecutive stops with unique shape_ids."""
    print("\n🗺️  Creating route segments...")

    segments = []

    # Create segments between some stops (simulating actual routes)
    segment_configs = [
        # Bus route segments
        (stops[0], stops[2], "SHAPE_BUS_CENTRAL_UNI"),
        (stops[2], stops[3], "SHAPE_BUS_UNI_AIRPORT"),
        (stops[3], stops[5], "SHAPE_BUS_AIRPORT_MALL"),
        # Tram route segments
        (stops[1], stops[4], "SHAPE_TRAM_OLDTOWN_BUSINESS"),
        (stops[4], stops[6], "SHAPE_TRAM_BUSINESS_STADIUM"),
        (stops[6], stops[9], "SHAPE_TRAM_STADIUM_RIVERSIDE"),
        # Train route segments
        (stops[0], stops[3], "SHAPE_TRAIN_CENTRAL_AIRPORT"),
    ]

    for from_stop, to_stop, shape_id in segment_configs:
        segment = RouteSegment(
            from_stop_id=from_stop.id,
            to_stop_id=to_stop.id,
            shape_id=shape_id,
        )
        db.add(segment)
        segments.append(segment)

    db.commit()
    print(f"   ✓ Created {len(segments)} route segments")
    return segments


def create_shape_points(db, segments):
    """Create GPS points for each route segment."""
    print("\n📍 Creating shape points (GPS coordinates)...")

    all_points = []

    for segment in segments:
        # Generate 10-15 GPS points per segment
        num_points = randint(10, 15)

        # Get start and end stop coordinates (we'll simulate this)
        # In real scenario, these would come from actual stops
        start_lat = 52.2297 + uniform(-0.05, 0.05)
        start_lon = 21.0122 + uniform(-0.05, 0.05)
        end_lat = 52.2297 + uniform(-0.05, 0.05)
        end_lon = 21.0122 + uniform(-0.05, 0.05)

        # Calculate increments
        lat_inc = (end_lat - start_lat) / (num_points - 1)
        lon_inc = (end_lon - start_lon) / (num_points - 1)

        segment_distance = 0.0

        for i in range(num_points):
            # Add some randomness to make path more realistic
            random_offset_lat = uniform(-0.0005, 0.0005)
            random_offset_lon = uniform(-0.0005, 0.0005)

            point = ShapePoint(
                shape_id=segment.shape_id,
                shape_pt_lat=start_lat + (lat_inc * i) + random_offset_lat,
                shape_pt_lon=start_lon + (lon_inc * i) + random_offset_lon,
                shape_pt_sequence=i + 1,
                shape_dist_traveled=round(segment_distance, 3),
            )
            db.add(point)
            all_points.append(point)

            # Increment distance (roughly 100-200m between points)
            segment_distance += uniform(0.1, 0.2)

    db.commit()
    print(f"   ✓ Created {len(all_points)} shape points")
    return all_points


def create_journey_data(db, vehicle_trips, users):
    """Create sample sensor data for vehicle trips."""
    print("\n📊 Creating journey data (sensor readings)...")

    passengers = [u for u in users if u.role == "PASSENGER"]
    journey_data_list = []

    # Create sensor data for active vehicle trips
    active_trips = [
        vt for vt in vehicle_trips if vt.current_status in ["IN_PROGRESS", "DELAYED"]
    ]

    base_time = datetime.now() - timedelta(minutes=20)

    for vehicle_trip in active_trips:
        # Create 10 sensor readings per vehicle trip
        for i in range(10):
            data = JourneyData(
                vehicle_trip_id=vehicle_trip.id,
                user_id=choice(passengers).id if randint(0, 1) else None,
                timestamp=base_time + timedelta(minutes=i * 2),
                latitude=52.2297 + uniform(-0.05, 0.05),
                longitude=21.0122 + uniform(-0.05, 0.05),
                altitude=uniform(100, 150),
                speed=uniform(20, 60),
                bearing=uniform(0, 360),
                accuracy=uniform(5, 15),
                vertical_accuracy=uniform(10, 30),
                satellite_count=randint(6, 12),
                acceleration_x=uniform(-1, 1),
                acceleration_y=uniform(-1, 1),
                acceleration_z=uniform(9, 10),
                gyroscope_x=uniform(-0.5, 0.5),
                gyroscope_y=uniform(-0.5, 0.5),
                gyroscope_z=uniform(-0.5, 0.5),
                magnetic_x=uniform(-50, 50),
                magnetic_y=uniform(-50, 50),
                magnetic_z=uniform(-50, 50),
                light=uniform(100, 1000),
                pressure=uniform(990, 1020),
                temperature=uniform(15, 25),
                humidity=uniform(40, 70),
                source="VEHICLE_GPS" if i % 2 == 0 else "USER_APP",
                battery_level=uniform(20, 100),
                connectivity=choice(["WIFI", "LTE", "5G"]),
            )
            db.add(data)
            journey_data_list.append(data)

    db.commit()
    print(f"   ✓ Created {len(journey_data_list)} sensor readings")
    return journey_data_list


def create_tickets(db, users, vehicle_trips):
    """Create sample tickets for users."""
    print("\n🎟️  Creating tickets...")

    tickets = []
    passengers = [u for u in users if u.role == "PASSENGER"]
    drivers = [u for u in users if u.role == "DRIVER"]

    # Monthly ticket for passenger 1
    ticket1 = Ticket(
        user_id=passengers[0].id,
        ticket_type="MONTHLY",
        valid_from=datetime.now() - timedelta(days=10),
        valid_to=datetime.now() + timedelta(days=20),
        vehicle_trip_id=None,  # Time-based ticket, no specific trip
    )
    db.add(ticket1)
    tickets.append(ticket1)

    # Two-hour ticket for passenger 2
    ticket2 = Ticket(
        user_id=passengers[0].id,
        ticket_type="TWO_HOUR",
        valid_from=datetime.now() - timedelta(minutes=30),
        valid_to=datetime.now() + timedelta(minutes=90),
        vehicle_trip_id=None,  # Time-based ticket
    )
    db.add(ticket2)
    tickets.append(ticket2)

    # Train route ticket for driver (personal use) - linked to specific vehicle trip
    if len(vehicle_trips) > 0:
        ticket3 = Ticket(
            user_id=drivers[0].id,
            ticket_type="TRAIN_ROUTE",
            valid_from=datetime.now(),
            valid_to=datetime.now() + timedelta(hours=2),
            vehicle_trip_id=vehicle_trips[0].id,  # Linked to specific trip
        )
        db.add(ticket3)
        tickets.append(ticket3)

    # Daily ticket for passenger 1 (expired)
    ticket4 = Ticket(
        user_id=passengers[0].id,
        ticket_type="DAILY",
        valid_from=datetime.now() - timedelta(days=5),
        valid_to=datetime.now() - timedelta(days=4),
        vehicle_trip_id=None,  # Time-based ticket
    )
    db.add(ticket4)
    tickets.append(ticket4)

    db.commit()
    print(f"   ✓ Created {len(tickets)} tickets")
    return tickets


def create_user_journeys(db, users, stops):
    """Create user journeys (planned trips)."""
    print("\n🗺️  Creating user journeys...")

    user_journeys = []
    passengers = [u for u in users if u.role == "PASSENGER"]

    # Get some stops for creating journeys
    all_stops = stops[:8]  # Use first 8 stops

    if len(passengers) >= 2 and len(all_stops) >= 4:
        # Saved journey 1 for passenger 1: Home to Work (active)
        journey1 = UserJourney(
            user_id=passengers[0].id,
            name="Home → Work",
            is_saved=True,
            is_active=True,  # This is their current active journey
        )
        db.add(journey1)
        db.flush()  # Get ID for adding stops

        # Add stops for journey 1
        for idx, stop in enumerate([all_stops[0], all_stops[2], all_stops[4]]):
            journey_stop = UserJourneyStop(
                user_journey_id=journey1.id,
                stop_id=stop.id,
                stop_order=idx + 1,
            )
            db.add(journey_stop)

        user_journeys.append(journey1)

        # Saved journey 2 for passenger 1: Work to Home
        journey2 = UserJourney(
            user_id=passengers[0].id,
            name="Work → Home",
            is_saved=True,
            is_active=False,
        )
        db.add(journey2)
        db.flush()

        # Add stops for journey 2 (reverse)
        for idx, stop in enumerate([all_stops[4], all_stops[2], all_stops[0]]):
            journey_stop = UserJourneyStop(
                user_journey_id=journey2.id,
                stop_id=stop.id,
                stop_order=idx + 1,
            )
            db.add(journey_stop)

        user_journeys.append(journey2)

        # Saved journey 3 for passenger 2: Shopping trip
        journey3 = UserJourney(
            user_id=passengers[0].id,
            name="Home → Mall → Park",
            is_saved=True,
            is_active=False,
        )
        db.add(journey3)
        db.flush()

        # Add stops for journey 3
        for idx, stop in enumerate([all_stops[1], all_stops[5], all_stops[6]]):
            journey_stop = UserJourneyStop(
                user_journey_id=journey3.id,
                stop_id=stop.id,
                stop_order=idx + 1,
            )
            db.add(journey_stop)

        user_journeys.append(journey3)

    db.commit()
    print(f"   ✓ Created {len(user_journeys)} user journeys with stops")
    return user_journeys


def create_reports(db, vehicle_trips, vehicles, users):
    """Create sample reports/incidents."""
    print("\n🚨 Creating reports...")

    reports = []

    # Get users by role
    drivers = [u for u in users if u.role == "DRIVER"]
    passengers = [u for u in users if u.role == "PASSENGER"]
    dispatcher = next(u for u in users if u.role == "DISPATCHER")

    # Report from driver (confidence 100%)
    report1 = Report(
        vehicle_trip_id=vehicle_trips[0].id,
        vehicle_id=vehicles[0].id,
        user_id=drivers[0].id,
        category="TRAFFIC_JAM",
        confidence=100,
        description="Heavy traffic on main road, 15 minutes delay expected",
        latitude=52.2297,
        longitude=21.0122,
    )
    db.add(report1)
    reports.append(report1)

    # Report from passenger (confidence 50%)
    report2 = Report(
        vehicle_trip_id=vehicle_trips[0].id,
        vehicle_id=vehicles[0].id,
        user_id=passengers[0].id,
        category="OVERCROWDED",
        confidence=50,
        description="Bus is very crowded, hard to get on",
        latitude=52.2131,
        longitude=21.0244,
    )
    db.add(report2)
    reports.append(report2)

    # Report from dispatcher (confidence 100%)
    report3 = Report(
        vehicle_trip_id=vehicle_trips[2].id,
        vehicle_id=vehicles[1].id,
        user_id=dispatcher.id,
        category="VEHICLE_BREAKDOWN",
        confidence=100,
        description="Engine warning light on, vehicle needs inspection",
        latitude=52.2319,
        longitude=21.0067,
    )
    db.add(report3)
    reports.append(report3)

    # Report from passenger (confidence 50%)
    report4 = Report(
        vehicle_trip_id=vehicle_trips[1].id,
        vehicle_id=vehicles[3].id,
        user_id=passengers[0].id,
        category="DIRTY_VEHICLE",
        confidence=50,
        description="Tram interior needs cleaning",
        latitude=52.2496,
        longitude=21.0121,
    )
    db.add(report4)
    reports.append(report4)

    # Report from driver (confidence 100%) - resolved
    report5 = Report(
        vehicle_trip_id=vehicle_trips[4].id,
        vehicle_id=vehicles[4].id,
        user_id=drivers[0].id,
        category="ANIMAL",
        confidence=100,
        description="Dog on tracks, stopped for safety",
        latitude=52.2398,
        longitude=20.9224,
        resolved_at=datetime.now() - timedelta(minutes=20),
    )
    db.add(report5)
    reports.append(report5)

    db.commit()
    print(f"   ✓ Created {len(reports)} reports")
    return reports


def print_summary(
    vehicle_types,
    stops,
    users,
    vehicles,
    routes,
    route_stops,
    route_segments,
    shape_points,
    vehicle_trips,
    journey_data_list,
    user_journeys,
    tickets,
    reports,
):
    """Print summary of created data."""
    print("\n" + "=" * 50)
    print("📊 DATABASE SEEDING SUMMARY")
    print("=" * 50)
    print(f"🚗 Vehicle Types:    {len(vehicle_types)}")
    print(f"🚏 Stops:            {len(stops)}")
    print(f"👥 Users:            {len(users)}")
    print(f"   - Drivers:        {len([u for u in users if u.role == 'DRIVER'])}")
    print(f"   - Passengers:     {len([u for u in users if u.role == 'PASSENGER'])}")
    print(f"   - Dispatchers:    {len([u for u in users if u.role == 'DISPATCHER'])}")
    print(f"   - Admins:         {len([u for u in users if u.role == 'ADMIN'])}")
    print(f"🚙 Vehicles:         {len(vehicles)}")
    print(f"   - With Issues:    {len([v for v in vehicles if v.issues])}")
    print(f"   - With Driver:    {len([v for v in vehicles if v.current_driver_id])}")
    print(f"🚌 Routes:           {len(routes)}")
    print(f"📍 Route Stops:      {len(route_stops)}")
    print(f"🗺️  Route Segments:   {len(route_segments)}")
    print(f"📌 Shape Points:     {len(shape_points)}")
    print(
        f"   - Avg per Segment: {len(shape_points) // len(route_segments) if route_segments else 0}"
    )
    print(f"🚀 Vehicle Trips:    {len(vehicle_trips)}")
    print(
        f"   - In Progress:    {len([vt for vt in vehicle_trips if vt.current_status == 'IN_PROGRESS'])}"
    )
    print(
        f"   - Planned:        {len([vt for vt in vehicle_trips if vt.current_status == 'PLANNED'])}"
    )
    print(
        f"   - Completed:      {len([vt for vt in vehicle_trips if vt.current_status == 'COMPLETED'])}"
    )
    print(
        f"   - Delayed:        {len([vt for vt in vehicle_trips if vt.current_status == 'DELAYED'])}"
    )
    print(f"📊 Sensor Readings:  {len(journey_data_list)}")
    print(f"👤 User Journeys:    {len(user_journeys)}")
    print(f"   - Saved:          {len([uj for uj in user_journeys if uj.is_saved])}")
    print(f"   - Active:         {len([uj for uj in user_journeys if uj.is_active])}")
    print(f"🎟️  Tickets:          {len(tickets)}")
    active_tickets = [
        t for t in tickets if t.valid_from <= datetime.now() <= t.valid_to
    ]
    print(f"   - Active:         {len(active_tickets)}")
    print(
        f"   - Train Tickets:  {len([t for t in tickets if t.ticket_type == 'TRAIN_ROUTE'])}"
    )
    print(f"🚨 Reports:          {len(reports)}")
    print(f"   - High Conf:      {len([r for r in reports if r.confidence == 100])}")
    print(f"   - Low Conf:       {len([r for r in reports if r.confidence == 50])}")
    print(f"   - Resolved:       {len([r for r in reports if r.resolved_at])}")
    print("=" * 50)
    print("\n✅ Database seeded successfully!")
    print("🌐 You can now explore the API at: http://localhost:8000/docs")


def seed_database(keep_gtfs_data=False):
    """
    Main seeding function.

    Args:
        keep_gtfs_data: If True, don't delete GTFS folders after seeding
    """
    print("🌱 Starting database seeding...")
    print("=" * 50)

    try:
        # Download GTFS data
        download_gtfs_data()

        # Remove old database
        remove_old_database()

        print("\n📦 Creating new database...")
        # Initialize database structure
        init_db()
        print("   ✓ Database structure created")

        # Create session
        db = SessionLocal()

        try:
            # Create vehicle types
            vehicle_types = create_vehicle_types(db)

            # Create data
            stops = create_stops(db, vehicle_types)
            users = create_users(db)
            vehicles = create_vehicles(db, vehicle_types, users)
            routes, route_trip_mapping = create_routes(db, stops, vehicle_types)
            route_stops = create_route_stops(
                db, routes, stops, vehicle_types, route_trip_mapping
            )
            route_segments = []  # Not created in this seed script
            shape_points = []  # Not created in this seed script
            journeys = create_journeys(db, routes, users)
            journey_data_list = create_journey_data(db, journeys, users)
            user_journeys = []  # Not created in this seed script
            tickets = []  # Not created in this seed script
            reports = []  # Not created in this seed script

            # Print summary
            print_summary(
                vehicle_types,
                stops,
                users,
                vehicles,
                routes,
                route_stops,
                route_segments,
                shape_points,
                journeys,
                journey_data_list,
                user_journeys,
                tickets,
                reports,
            )

        except Exception as e:
            print(f"\n❌ Error seeding database: {e}")
            db.rollback()
            raise
        finally:
            db.close()

    finally:
        # Clean up GTFS data unless user wants to keep it
        if not keep_gtfs_data:
            cleanup_gtfs_data()
        else:
            print("\n📂 GTFS data kept in local folders")


if __name__ == "__main__":
    # Check for command-line arguments
    keep_gtfs = "--keep-gtfs" in sys.argv
    seed_database(keep_gtfs_data=keep_gtfs)
