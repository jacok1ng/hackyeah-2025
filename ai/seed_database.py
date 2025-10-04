"""
Database seeding script - populates the database with sample data.
This script is fully self-contained:
- Removes old database if it exists
- Creates new database with proper structure
- Initializes vehicle types
- Populates with sample data

Run this script: python seed_database.py
"""

import os
from datetime import datetime, timedelta
from random import choice, randint, uniform

from database import SessionLocal, init_db
from db_models import (
    Journey,
    JourneyData,
    Report,
    Route,
    RouteStop,
    Stop,
    User,
    Vehicle,
    VehicleType,
)
from init_data import VEHICLE_TYPES


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
    """Create sample stops (bus/tram/train stations)."""
    print("\n🚏 Creating stops...")

    # Find vehicle types by code
    bus_type = next(vt for vt in vehicle_types if vt.code == "BUS")
    tram_type = next(vt for vt in vehicle_types if vt.code == "TRAM")
    train_type = next(vt for vt in vehicle_types if vt.code == "TRAIN")

    stops_data = [
        {
            "name": "Central Station",
            "vehicle_type_id": train_type.id,
            "latitude": 52.2297,
            "longitude": 21.0122,
        },
        {
            "name": "Old Town Square",
            "vehicle_type_id": tram_type.id,
            "latitude": 52.2496,
            "longitude": 21.0121,
        },
        {
            "name": "University Campus",
            "vehicle_type_id": bus_type.id,
            "latitude": 52.2131,
            "longitude": 21.0244,
        },
        {
            "name": "Airport Terminal 1",
            "vehicle_type_id": bus_type.id,
            "latitude": 52.1672,
            "longitude": 20.9679,
            "external_id": "AIRPORT_T1",
        },
        {
            "name": "Business District Center",
            "vehicle_type_id": tram_type.id,
            "latitude": 52.2319,
            "longitude": 21.0067,
        },
        {
            "name": "Shopping Mall Westfield",
            "vehicle_type_id": bus_type.id,
            "latitude": 52.1897,
            "longitude": 20.9825,
        },
        {
            "name": "Stadium North Gate",
            "vehicle_type_id": tram_type.id,
            "latitude": 52.2398,
            "longitude": 20.9224,
        },
        {
            "name": "Hospital Emergency",
            "vehicle_type_id": bus_type.id,
            "latitude": 52.2150,
            "longitude": 21.0500,
        },
        {
            "name": "Tech Park East",
            "vehicle_type_id": bus_type.id,
            "latitude": 52.2550,
            "longitude": 21.0850,
        },
        {
            "name": "Riverside Promenade",
            "vehicle_type_id": tram_type.id,
            "latitude": 52.2450,
            "longitude": 21.0300,
        },
    ]

    stops = []
    for stop_data in stops_data:
        stop = Stop(**stop_data)
        db.add(stop)
        stops.append(stop)

    db.commit()
    print(f"   ✓ Created {len(stops)} stops")
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


def create_routes(db, stops, vehicles):
    """Create sample routes."""
    print("\n🚌 Creating routes...")

    now = datetime.now()
    routes = []

    route_configs = [
        {
            "vehicle": vehicles[0],  # BUS-101
            "starting_stop": stops[2],  # University Campus
            "ending_stop": stops[8],  # Tech Park East
            "hours_offset": 1,
            "duration": 2,
            "status": "ON_TIME",
        },
        {
            "vehicle": vehicles[3],  # TRAM-205
            "starting_stop": stops[1],  # Old Town Square
            "ending_stop": stops[0],  # Central Station
            "hours_offset": 2,
            "duration": 1.5,
            "status": "ON_TIME",
        },
        {
            "vehicle": vehicles[1],  # BUS-102
            "starting_stop": stops[0],  # Central Station
            "ending_stop": stops[3],  # Airport Terminal 1
            "hours_offset": 3,
            "duration": 2.5,
            "status": "ON_TIME",
        },
        {
            "vehicle": vehicles[6],  # TRAIN-S1
            "starting_stop": stops[0],  # Central Station
            "ending_stop": stops[3],  # Airport Terminal 1
            "hours_offset": 4,
            "duration": 3,
            "status": "ON_TIME",
        },
        {
            "vehicle": vehicles[4],  # TRAM-206
            "starting_stop": stops[4],  # Business District Center
            "ending_stop": stops[3],  # Airport Terminal 1
            "hours_offset": 0.5,
            "duration": 1,
            "status": "DELAYED",
        },
    ]

    for config in route_configs:
        route = Route(
            vehicle_id=config["vehicle"].id,
            starting_stop_id=config["starting_stop"].id,
            ending_stop_id=config["ending_stop"].id,
            scheduled_departure=now + timedelta(hours=config["hours_offset"]),
            scheduled_arrival=(
                now + timedelta(hours=config["hours_offset"] + config["duration"])
            ),
            current_status=config["status"],
        )
        db.add(route)
        routes.append(route)

    db.commit()
    print(f"   ✓ Created {len(routes)} routes")
    return routes


def create_route_stops(db, routes, stops):
    """Create route-stop associations."""
    print("\n📍 Creating route stops...")

    route_stops = []

    # Route 1: BUS-101 (5 stops)
    route1_stops = [stops[2], stops[4], stops[5], stops[7], stops[8]]
    for i, stop in enumerate(route1_stops):
        base_time = datetime.now() + timedelta(hours=1, minutes=i * 15)
        rs = RouteStop(
            route_id=routes[0].id,
            stop_id=stop.id,
            scheduled_arrival=base_time,
            scheduled_departure=base_time + timedelta(minutes=2),
        )
        db.add(rs)
        route_stops.append(rs)

    # Route 2: TRAM-205 (4 stops)
    route2_stops = [stops[1], stops[6], stops[9], stops[0]]
    for i, stop in enumerate(route2_stops):
        base_time = datetime.now() + timedelta(hours=2, minutes=i * 10)
        rs = RouteStop(
            route_id=routes[1].id,
            stop_id=stop.id,
            scheduled_arrival=base_time,
            scheduled_departure=base_time + timedelta(minutes=1),
        )
        db.add(rs)
        route_stops.append(rs)

    # Route 3: BUS-102 (6 stops)
    route3_stops = [stops[0], stops[1], stops[2], stops[3], stops[7], stops[8]]
    for i, stop in enumerate(route3_stops):
        base_time = datetime.now() + timedelta(hours=3, minutes=i * 20)
        rs = RouteStop(
            route_id=routes[2].id,
            stop_id=stop.id,
            scheduled_arrival=base_time,
            scheduled_departure=base_time + timedelta(minutes=3),
        )
        db.add(rs)
        route_stops.append(rs)

    # Route 4: TRAIN-S1 (4 stops)
    route4_stops = [stops[0], stops[4], stops[5], stops[3]]
    for i, stop in enumerate(route4_stops):
        base_time = datetime.now() + timedelta(hours=4, minutes=i * 25)
        rs = RouteStop(
            route_id=routes[3].id,
            stop_id=stop.id,
            scheduled_arrival=base_time,
            scheduled_departure=base_time + timedelta(minutes=2),
        )
        db.add(rs)
        route_stops.append(rs)

    # Route 5: TRAM-206 (3 stops)
    route5_stops = [stops[4], stops[0], stops[3]]
    for i, stop in enumerate(route5_stops):
        base_time = datetime.now() + timedelta(hours=0.5, minutes=i * 8)
        rs = RouteStop(
            route_id=routes[4].id,
            stop_id=stop.id,
            scheduled_arrival=base_time,
            scheduled_departure=base_time + timedelta(minutes=1),
        )
        db.add(rs)
        route_stops.append(rs)

    db.commit()
    print(f"   ✓ Created {len(route_stops)} route stops")
    return route_stops


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


def create_reports(db, journeys, vehicles, users):
    """Create sample reports/incidents."""
    print("\n🚨 Creating reports...")

    reports = []

    # Get users by role
    drivers = [u for u in users if u.role == "DRIVER"]
    passengers = [u for u in users if u.role == "PASSENGER"]
    dispatcher = next(u for u in users if u.role == "DISPATCHER")

    # Report from driver (confidence 100%)
    report1 = Report(
        journey_id=journeys[0].id,
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
        journey_id=journeys[0].id,
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
        journey_id=journeys[2].id,
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
        journey_id=journeys[1].id,
        vehicle_id=vehicles[3].id,
        user_id=passengers[1].id,
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
        journey_id=journeys[4].id,
        vehicle_id=vehicles[4].id,
        user_id=drivers[1].id,
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
    journeys,
    journey_data_list,
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
    print(f"🚨 Reports:          {len(reports)}")
    print(f"   - High Conf:      {len([r for r in reports if r.confidence == 100])}")
    print(f"   - Low Conf:       {len([r for r in reports if r.confidence == 50])}")
    print(f"   - Resolved:       {len([r for r in reports if r.resolved_at])}")
    print("=" * 50)
    print("\n✅ Database seeded successfully!")
    print("🌐 You can now explore the API at: http://localhost:8000/docs")


def seed_database():
    """Main seeding function."""
    print("🌱 Starting database seeding...")
    print("=" * 50)

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
        routes = create_routes(db, stops, vehicles)
        route_stops = create_route_stops(db, routes, stops)
        journeys = create_journeys(db, routes, users)
        journey_data_list = create_journey_data(db, journeys, users)
        reports = create_reports(db, journeys, vehicles, users)

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
            reports,
        )

    except Exception as e:
        print(f"\n❌ Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
