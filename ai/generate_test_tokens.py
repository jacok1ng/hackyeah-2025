"""
Generate JWT tokens for test users.
Run this once to generate tokens for test_login.py
"""

from auth import create_access_token
from database import SessionLocal
from db_models import User

# Get real users from database
db = SessionLocal()

try:
    # Get all users
    users = db.query(User).all()

    print("=" * 80)
    print("GENERATED TEST TOKENS (Never expire)")
    print("=" * 80)
    print("\nCopy these to test_login.py or use directly:\n")
    print("TEST_TOKENS = {")

    for user in users:
        token = create_access_token(
            data={
                "sub": str(user.id),
                "user_id": str(user.id),
                "username": user.name,
                "email": user.email,
                "role": user.role,
            }
        )
        print(f'    "{user.name}": "{token}",')

    print("}\n")
    print("=" * 80)
    print("\n📝 Quick reference:")
    for user in users:
        print(f"   {user.name:10} - {user.role:12} - {user.email}")
    print("=" * 80)

finally:
    db.close()
