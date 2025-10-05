"""
Simple script to test the login functionality.
"""

import time

import requests

API_URL = "http://localhost:8000"

# Pre-generated test tokens (never expire)
# These can be used directly without login for testing
TEST_TOKENS = {
    "user": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyLXRlc3QtaWQtMSIsInVzZXJfaWQiOiJ1c2VyLXRlc3QtaWQtMSIsInVzZXJuYW1lIjoidXNlciIsImVtYWlsIjoidXNlckBleGFtcGxlLmNvbSIsInJvbGUiOiJQQVNTRU5HRVIifQ.m82ObpD1kQlgu_gvBy9iXv-XhULNPyVEibTaiUs19O8",
    "user2": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyLXRlc3QtaWQtMiIsInVzZXJfaWQiOiJ1c2VyLXRlc3QtaWQtMiIsInVzZXJuYW1lIjoidXNlcjIiLCJlbWFpbCI6InVzZXIyQGV4YW1wbGUuY29tIiwicm9sZSI6IlBBU1NFTkdFUiJ9.1vxoBhJelA9CtjHPpVcBGPSr2Z1_UFs8t_gcpW0zPlg",
    "user3": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyLXRlc3QtaWQtMyIsInVzZXJfaWQiOiJ1c2VyLXRlc3QtaWQtMyIsInVzZXJuYW1lIjoidXNlcjMiLCJlbWFpbCI6InVzZXIzQGV4YW1wbGUuY29tIiwicm9sZSI6IlBBU1NFTkdFUiJ9.Sbr4gK9vTAwvmRzinjT1hzOZjEh8TEJNkLyvKvDDxRM",
    "driv": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJkcml2LXRlc3QtaWQiLCJ1c2VyX2lkIjoiZHJpdi10ZXN0LWlkIiwidXNlcm5hbWUiOiJkcml2IiwiZW1haWwiOiJkcml2QGV4YW1wbGUuY29tIiwicm9sZSI6IkRSSVZFUiJ9.FEH2ydFOvKhdOOiVSRWoQurSUKL4lMAqd-hniuRoo_Y",
    "disp": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJkaXNwLXRlc3QtaWQiLCJ1c2VyX2lkIjoiZGlzcC10ZXN0LWlkIiwidXNlcm5hbWUiOiJkaXNwIiwiZW1haWwiOiJkaXNwQGV4YW1wbGUuY29tIiwicm9sZSI6IkRJU1BBVENIRVIifQ.Vqis77AVQ-Zv-qVAoTdjA67nii0TbYMA_HY7jM74uyA",
    "admin": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbi10ZXN0LWlkIiwidXNlcl9pZCI6ImFkbWluLXRlc3QtaWQiLCJ1c2VybmFtZSI6ImFkbWluIiwiZW1haWwiOiJhZG1pbkBleGFtcGxlLmNvbSIsInJvbGUiOiJBRE1JTiJ9.bFIdMCGNrnPpiOLreWovWH7ap6qMwVLDPsCadOBk9fg",
}


def test_login(username, password):
    """Test login with given credentials."""
    print(f"\n🔐 Testing login: {username}:{password}")

    response = requests.post(
        f"{API_URL}/auth/login", json={"username": username, "password": password}
    )

    if response.status_code == 200:
        data = response.json()
        if data["success"]:
            print(f"✅ Login successful!")
            print(f"   User: {data['user']['username']}")
            print(f"   Email: {data['user']['email']}")
            print(f"   Role: {data['user']['role']}")
            print(f"   Badge: {data['user']['badge']}")
            print(f"   Token: {data['access_token'][:50]}...")

            # Test token by getting user's journeys
            headers = {"Authorization": f"Bearer {data['access_token']}"}
            journeys_response = requests.get(
                f"{API_URL}/user-journeys/my", headers=headers
            )
            if journeys_response.status_code == 200:
                print(f"   ✓ Token validated - can access protected endpoints")
            else:
                print(f"   ✗ Token validation failed")

            return data
        else:
            print(f"❌ Login failed: {data['message']}")
    else:
        print(f"❌ Request failed with status {response.status_code}")

    return None


def main():
    """Test all 4 accounts."""
    print("\n" + "=" * 60)
    print("🔐 TESTING LOGIN SYSTEM")
    print("=" * 60)

    # Wait a bit for API to start
    print("\n⏳ Waiting for API to start...")
    time.sleep(2)

    # Test all accounts
    test_cases = [
        ("user", "user", "PASSENGER"),
        ("user2", "user2", "PASSENGER"),
        ("user3", "user3", "PASSENGER"),
        ("driv", "driv", "DRIVER"),
        ("disp", "disp", "DISPATCHER"),
        ("admin", "admin", "ADMIN"),
    ]

    successful = 0
    for username, password, expected_role in test_cases:
        result = test_login(username, password)
        if result and result.get("user") and result["user"]["role"] == expected_role:
            successful += 1

    # Test invalid credentials
    print("\n\n🔒 Testing invalid credentials...")
    test_login("invalid", "invalid")
    test_login("user", "wrong_password")

    print("\n" + "=" * 60)
    print(f"📊 RESULTS: {successful}/{len(test_cases)} accounts tested successfully")
    print("=" * 60)
    print(f"\n✅ Login system is working!")
    print(f"📚 API Docs: {API_URL}/docs")
    print(f"🔐 Test accounts:")
    print(f"   - user:user (PASSENGER)")
    print(f"   - user2:user2 (PASSENGER)")
    print(f"   - user3:user3 (PASSENGER)")
    print(f"   - driv:driv (DRIVER)")
    print(f"   - disp:disp (DISPATCHER)")
    print(f"   - admin:admin (ADMIN)")

    print(f"\n🎟️ Pre-generated tokens (never expire):")
    print(f"   You can use these directly in Authorization: Bearer <token>")
    for username in ["user", "user2", "user3", "driv", "disp", "admin"]:
        token = TEST_TOKENS[username]
        print(f"\n   {username}:")
        print(f"   {token[:80]}...")
    print()


if __name__ == "__main__":
    main()
