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

import os
import sys
import shutil
import zipfile
from datetime import datetime, timedelta, time
from random import choice, randint, uniform
from urllib.request import urlretrieve
import csv
import pandas as pd
import sqlite3
from tqdm import tqdm

from database import SessionLocal, init_db
from db_models import (
    Journey,
    JourneyData,
    Route,
    RouteStop,
    Stop,
    User,
    Vehicle,
    VehicleType,
)
from init_data import VEHICLE_TYPES


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
    parts = time_str.strip().split(':')
    hours = int(parts[0])
    minutes = int(parts[1])
    seconds = int(parts[2])
    
    # Handle times that exceed 24 hours (next day service)
    days = hours // 24
    hours = hours % 24
    
    # Create datetime using today as base reference
    base_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    result = base_date + timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)
    
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
        ("GTFS_KRK_A", bus_type),   # Buses
        ("GTFS_KRK_T", tram_type),  # Trams
        ("GTFS_KRK_M", train_type), # Metro/Train
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
            with zipfile.ZipFile(zip_filename, 'r') as zip_ref:
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
                stop_name = f"{row.get("stop_name")} {row.get("stop_desc", "")}".strip()
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
            "name": "John Driver",
            "email": "john.driver@transport.com",
            "hashed_password": "hashed_password123",
            "role": "DRIVER",
            "verified": True,
            "reputation_points": 150,
            "badge": "🏅 Gold Driver",
        },
        {
            "name": "Maria Conductor",
            "email": "maria.conductor@transport.com",
            "hashed_password": "hashed_password456",
            "role": "DRIVER",
            "verified": True,
            "reputation_points": 200,
            "badge": "⭐ Premium Driver",
        },
        {
            "name": "Bob Dispatcher",
            "email": "bob.dispatcher@transport.com",
            "hashed_password": "hashed_password789",
            "role": "DISPATCHER",
            "verified": True,
            "reputation_points": 100,
            "badge": "📡 Senior Dispatcher",
        },
        {
            "name": "Alice Admin",
            "email": "alice.admin@transport.com",
            "hashed_password": "hashed_admin_pass",
            "role": "ADMIN",
            "verified": True,
            "reputation_points": 500,
            "badge": "👑 System Admin",
        },
        {
            "name": "Tom Passenger",
            "email": "tom.passenger@example.com",
            "hashed_password": "hashed_user_pass1",
            "role": "PASSENGER",
            "verified": True,
            "reputation_points": 50,
            "badge": "🌟 Trusted Commuter",
        },
        {
            "name": "Emma Rider",
            "email": "emma.rider@example.com",
            "hashed_password": "hashed_user_pass2",
            "role": "PASSENGER",
            "verified": False,
            "reputation_points": 10,
            "badge": None,
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
            "current_driver_id": drivers[1].id,
        },
        {
            "vehicle_type_id": tram_type.id,
            "registration_number": "TRAM-206",
            "capacity": 150,
            "last_inspection_date": datetime.now() - timedelta(days=10),
            "issues": None,
            "current_driver_id": drivers[1].id,
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
    trip_aggregates = stop_times_df.sort_values(['trip_id', 'stop_sequence']).groupby('trip_id').agg(
        starting_stop=('stop_id', 'first'),
        ending_stop=('stop_id', 'last'),
        scheduled_arrival=('arrival_time', 'last'),
        scheduled_departure=('departure_time', 'first'),
    ).reset_index()
    
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
    conn = sqlite3.connect('transportation.db')
    
    with conn:
        # Create temporary table
        trip_aggregates.to_sql('temp_trip_stops', conn, if_exists='replace', index=False)
        
        # Query for trips where both start and end stops exist
        cursor = conn.cursor()
        cursor.execute("""
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
        """, (vehicle_type_id, vehicle_type_id))
        
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


def _process_route_stops_for_feed(db, folder, vehicle_type, route_trip_mapping, route_stops):
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
    conn = sqlite3.connect('transportation.db')
    
    with conn:
        # Create temporary table
        stop_times_df.to_sql('temp_stop_times', conn, if_exists='replace', index=False)
        
        # Query for stop times where the stop exists in our database
        cursor = conn.cursor()
        cursor.execute("""
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
        """, (vehicle_type_id,))
        
        return cursor.fetchall()
    
    conn.close()


def create_journeys(db, routes, users):
    """Create sample journeys."""
    print("\n🚀 Creating journeys...")

    drivers = [u for u in users if u.role == "DRIVER"]
    journeys = []

    journey_configs = [
        {
            "route": routes[0],
            "driver": drivers[0],
            "status": "IN_PROGRESS",
            "has_departure": True,
            "at_stop": True,
        },
        {
            "route": routes[1],
            "driver": drivers[1],
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
            "driver": drivers[1],
            "status": "COMPLETED",
            "has_departure": True,
            "at_stop": False,
        },
    ]

    now = datetime.now()

    for config in journey_configs:
        journey = Journey(
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
        db.add(journey)
        journeys.append(journey)

    db.commit()
    print(f"   ✓ Created {len(journeys)} journeys")
    return journeys


def create_journey_data(db, journeys, users):
    """Create sample sensor data for journeys."""
    print("\n📊 Creating journey data (sensor readings)...")

    passengers = [u for u in users if u.role == "PASSENGER"]
    journey_data_list = []

    # Create sensor data for active journeys
    active_journeys = [
        j for j in journeys if j.current_status in ["IN_PROGRESS", "DELAYED"]
    ]

    base_time = datetime.now() - timedelta(minutes=20)

    for journey in active_journeys:
        # Create 10 sensor readings per journey
        for i in range(10):
            data = JourneyData(
                journey_id=journey.id,
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


def print_summary(
    vehicle_types,
    stops,
    users,
    vehicles,
    routes,
    route_stops,
    journeys,
    journey_data_list,
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
    print(f"🚀 Journeys:         {len(journeys)}")
    print(
        f"   - In Progress:    {len([j for j in journeys if j.current_status == 'IN_PROGRESS'])}"
    )
    print(
        f"   - Planned:        {len([j for j in journeys if j.current_status == 'PLANNED'])}"
    )
    print(
        f"   - Completed:      {len([j for j in journeys if j.current_status == 'COMPLETED'])}"
    )
    print(
        f"   - Delayed:        {len([j for j in journeys if j.current_status == 'DELAYED'])}"
    )
    print(f"📊 Sensor Readings:  {len(journey_data_list)}")
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
            route_stops = create_route_stops(db, routes, stops, vehicle_types, route_trip_mapping)
            journeys = create_journeys(db, routes, users)
            journey_data_list = create_journey_data(db, journeys, users)

            # Print summary
            print_summary(
                vehicle_types,
                stops,
                users,
                vehicles,
                routes,
                route_stops,
                journeys,
                journey_data_list,
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
