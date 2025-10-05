"""
Test authorization for various endpoints.
Tests if role-based access control works correctly.
"""

import time

import requests

BASE_URL = "http://localhost:8000"

# Wait for API to start
time.sleep(3)

# Test tokens (from generate_test_tokens.py)
TOKENS = {
    "user1": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIwZTc4M2ZjYS02MTE2LTQ1ZmEtOTVlNS1lNjA0NTBkMGM0NmYiLCJ1c2VyX2lkIjoiMGU3ODNmY2EtNjExNi00NWZhLTk1ZTUtZTYwNDUwZDBjNDZmIiwidXNlcm5hbWUiOiJ1c2VyMSIsImVtYWlsIjoidXNlcjFAZXhhbXBsZS5jb20iLCJyb2xlIjoiUEFTU0VOR0VSIn0.1Jm9HkXPGyUM_MVUnBMkPoRsgAEnvo5ifhio-Wod6Kg",
    "driv": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJiZTBmOWU5NS1hYmZiLTRiMDctYjgyZS1iYmYxZWUwZmZlMzIiLCJ1c2VyX2lkIjoiYmUwZjllOTUtYWJmYi00YjA3LWI4MmUtYmJmMWVlMGZmZTMyIiwidXNlcm5hbWUiOiJkcml2IiwiZW1haWwiOiJkcml2QGV4YW1wbGUuY29tIiwicm9sZSI6IkRSSVZFUiJ9.jmfybjVNNw9KR77fc_htjTNcawEwQF2lM6BgmkHgRVU",
    "disp": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzZmVlOGVhYi0zZjY3LTRmMzYtODQ2MC1kYTI4ODU2ZTZjNWUiLCJ1c2VyX2lkIjoiM2ZlZThlYWItM2Y2Ny00ZjM2LTg0NjAtZGEyODg1NmU2YzVlIiwidXNlcm5hbWUiOiJkaXNwIiwiZW1haWwiOiJkaXNwQGV4YW1wbGUuY29tIiwicm9sZSI6IkRJU1BBVENIRVIifQ.p_gws4UaQFgZztWYGItrybqsNe3njVSOCzwNx5Bha7U",
    "admin": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJjYjI1YzJlMC03Mzg5LTRlMDgtYjFlMC04MmE1YjZhY2I2ZmIiLCJ1c2VyX2lkIjoiY2IyNWMyZTAtNzM4OS00ZTA4LWIxZTAtODJhNWI2YWNiNmZiIiwidXNlcm5hbWUiOiJhZG1pbiIsImVtYWlsIjoiYWRtaW5AZXhhbXBsZS5jb20iLCJyb2xlIjoiQURNSU4ifQ.W7-UZNccakIbuOncNcXoknWvCTd4zG-LPcuHknFkd2Y",
}


def test_endpoint(name, method, url, token=None, expected_status=200):
    """Test an endpoint with optional authentication."""
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, headers=headers, json={})
        elif method == "PUT":
            response = requests.put(url, headers=headers, json={})
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)

        status_ok = response.status_code == expected_status
        icon = "✅" if status_ok else "❌"
        print(f"{icon} {name}: {response.status_code} (expected {expected_status})")
        return status_ok
    except Exception as e:
        print(f"❌ {name}: ERROR - {e}")
        return False


print("=" * 80)
print("TESTING AUTHORIZATION")
print("=" * 80)

# Test public endpoints (should work without token)
print("\n📖 Testing PUBLIC endpoints (no token required):")
test_endpoint("GET /stops", "GET", f"{BASE_URL}/stops", None, 200)
test_endpoint("GET /routes", "GET", f"{BASE_URL}/routes", None, 200)
test_endpoint("GET /vehicles", "GET", f"{BASE_URL}/vehicles", None, 200)
test_endpoint("GET /vehicle-types", "GET", f"{BASE_URL}/vehicle-types", None, 200)

# Test endpoints requiring authentication
print("\n🔐 Testing AUTHENTICATED endpoints:")
test_endpoint("GET /users/me (no token)", "GET", f"{BASE_URL}/users/me", None, 401)
test_endpoint(
    "GET /users/me (with token)", "GET", f"{BASE_URL}/users/me", TOKENS["user1"], 200
)

# Test PASSENGER trying to access admin endpoints
print("\n👤 Testing PASSENGER access (should be denied for admin endpoints):")
test_endpoint(
    "POST /stops (PASSENGER)", "POST", f"{BASE_URL}/stops", TOKENS["user1"], 403
)
test_endpoint(
    "POST /vehicles (PASSENGER)", "POST", f"{BASE_URL}/vehicles", TOKENS["user1"], 403
)
test_endpoint(
    "GET /reports (PASSENGER)", "GET", f"{BASE_URL}/reports", TOKENS["user1"], 403
)

# Test DISPATCHER access
print("\n🚦 Testing DISPATCHER access (should work for most admin endpoints):")
test_endpoint(
    "POST /stops (DISPATCHER)", "POST", f"{BASE_URL}/stops", TOKENS["disp"], 400
)  # 400 = validation error (missing data), but auth OK
test_endpoint(
    "POST /vehicles (DISPATCHER)", "POST", f"{BASE_URL}/vehicles", TOKENS["disp"], 422
)  # 422 = validation error, but auth OK
test_endpoint(
    "GET /reports (DISPATCHER)", "GET", f"{BASE_URL}/reports", TOKENS["disp"], 200
)

# Test DRIVER access
print("\n🚗 Testing DRIVER access:")
test_endpoint(
    "POST /vehicle-trips (DRIVER)",
    "POST",
    f"{BASE_URL}/vehicle-trips",
    TOKENS["driv"],
    422,
)  # 422 = validation error, but auth OK
test_endpoint(
    "POST /stops (DRIVER)", "POST", f"{BASE_URL}/stops", TOKENS["driv"], 403
)  # Forbidden

# Test ADMIN access
print("\n👑 Testing ADMIN access (should work for all):")
test_endpoint(
    "GET /reports (ADMIN)", "GET", f"{BASE_URL}/reports", TOKENS["admin"], 200
)
test_endpoint(
    "POST /stops (ADMIN)", "POST", f"{BASE_URL}/stops", TOKENS["admin"], 422
)  # 422 = validation error, but auth OK

# Test user profile access
print("\n👥 Testing USER PROFILE access:")
test_endpoint("GET /users/me", "GET", f"{BASE_URL}/users/me", TOKENS["user1"], 200)

print("\n" + "=" * 80)
print("✅ AUTHORIZATION TESTS COMPLETED")
print("=" * 80)
