"""
Generate JWT tokens for test users.
Run this once to generate tokens for test_login.py
"""

from auth import create_access_token

# Test users
test_users = [
    {
        "username": "user",
        "user_id": "user-1",
        "email": "user@example.com",
        "role": "PASSENGER",
    },
    {
        "username": "user2",
        "user_id": "user-2",
        "email": "user2@example.com",
        "role": "PASSENGER",
    },
    {
        "username": "user3",
        "user_id": "user-3",
        "email": "user3@example.com",
        "role": "PASSENGER",
    },
    {
        "username": "driv",
        "user_id": "driv",
        "email": "driv@example.com",
        "role": "DRIVER",
    },
    {
        "username": "disp",
        "user_id": "disp",
        "email": "disp@example.com",
        "role": "DISPATCHER",
    },
    {
        "username": "admin",
        "user_id": "admin",
        "email": "admin@example.com",
        "role": "ADMIN",
    },
]

print("=" * 80)
print("GENERATED TEST TOKENS (Never expire)")
print("=" * 80)
print("\nCopy these to test_login.py:\n")
print("TEST_TOKENS = {")

for user in test_users:
    token = create_access_token(
        data={
            "sub": user["user_id"],
            "user_id": user["user_id"],
            "username": user["username"],
            "email": user["email"],
            "role": user["role"],
        }
    )
    print(f'    "{user["username"]}": "{token}",')

print("}\n")
print("=" * 80)
