"""
Simple test script to demonstrate API usage.
Run the API server first: python main.py
Then run this script: python test_api.py
"""

from datetime import datetime, timedelta

import requests

BASE_URL = "http://localhost:8000"


def test_api():
    print("Testing Transportation Management API\n")

    # 1. Get vehicle types (read-only, system-defined)
    print("1. Getting vehicle types...")
    response = requests.get(f"{BASE_URL}/vehicle-types/")
    vehicle_types = response.json()
    print(f"   Found {len(vehicle_types)} vehicle types")

    # Get the TRAIN type for testing
    train_type = next((vt for vt in vehicle_types if vt["code"] == "TRAIN"), None)
    if not train_type:
        print("   ⚠️  TRAIN type not found, using first available type")
        train_type = vehicle_types[0]
    vehicle_type_id = train_type["id"]
    print(f"   Using vehicle type: {train_type['name']} (ID: {vehicle_type_id})")

    # 2. Create a stop
    print("\n2. Creating a stop...")
    stop_data = {
        "name": "Central Station",
        "vehicle_type_id": vehicle_type_id,
        "latitude": 52.2297,
        "longitude": 21.0122,
    }
    response = requests.post(f"{BASE_URL}/stops/", json=stop_data)
    stop = response.json()
    stop_id = stop["id"]
    print(f"   Created stop: {stop['name']} (ID: {stop_id})")

    # 3. Create another stop
    print("\n3. Creating another stop...")
    stop2_data = {
        "name": "Airport Terminal",
        "vehicle_type_id": vehicle_type_id,
        "latitude": 52.1672,
        "longitude": 20.9679,
    }
    response = requests.post(f"{BASE_URL}/stops/", json=stop2_data)
    stop2 = response.json()
    stop2_id = stop2["id"]
    print(f"   Created stop: {stop2['name']} (ID: {stop2_id})")

    # 4. Create a route
    print("\n4. Creating a route...")
    now = datetime.now()
    route_data = {
        "vehicle_id": "TRAIN-001",
        "vehicle_type_id": vehicle_type_id,
        "scheduled_departure": (now + timedelta(hours=1)).isoformat(),
        "scheduled_arrival": (now + timedelta(hours=2)).isoformat(),
        "current_status": "ON_TIME",
    }
    response = requests.post(f"{BASE_URL}/routes/", json=route_data)
    route = response.json()
    route_id = route["id"]
    print(f"   Created route: {route['vehicle_id']} (ID: {route_id})")

    # 5. Create a user
    print("\n5. Creating a user...")
    user_data = {
        "name": "John Doe",
        "email": "john.doe@example.com",
        "password": "secure_password",
        "role": "DRIVER",
        "verified": True,
    }
    response = requests.post(f"{BASE_URL}/users/", json=user_data)
    user = response.json()
    user_id = user["id"]
    print(f"   Created user: {user['name']} ({user['role']}, ID: {user_id})")

    # 6. Create a journey
    print("\n6. Creating a journey...")
    journey_data = {
        "route_id": route_id,
        "driver_id": user_id,
        "current_status": "PLANNED",
    }
    response = requests.post(f"{BASE_URL}/journeys/", json=journey_data)
    journey = response.json()
    journey_id = journey["id"]
    print(f"   Created journey (ID: {journey_id})")

    # 7. Get all stops
    print("\n7. Getting all stops...")
    response = requests.get(f"{BASE_URL}/stops/")
    stops = response.json()
    print(f"   Found {len(stops)} stops")

    # 8. Update a stop
    print("\n8. Updating stop...")
    update_data = {"name": "Central Railway Station"}
    response = requests.put(f"{BASE_URL}/stops/{stop_id}", json=update_data)
    updated_stop = response.json()
    print(f"   Updated stop name to: {updated_stop['name']}")

    # 9. Health check
    print("\n9. Checking API health...")
    response = requests.get(f"{BASE_URL}/health")
    health = response.json()
    print(f"   API status: {health['status']}")

    print("\n✅ All tests completed successfully!")


if __name__ == "__main__":
    try:
        test_api()
    except requests.exceptions.ConnectionError:
        print("❌ Error: Cannot connect to API. Make sure the server is running:")
        print("   python main.py")
    except Exception as e:
        print(f"❌ Error: {e}")
        print(f"❌ Error: {e}")
