import crud
from auth import create_access_token, verify_password
from database import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from models import LoginRequest, LoginResponse
from sqlalchemy.orm import Session

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    """
    Simple login with username and password.
    Returns user information on success.

    Test credentials:
    - user:user (PASSENGER)
    - user2:user2 (PASSENGER)
    - user3:user3 (PASSENGER)
    - driv:driv (DRIVER)
    - disp:disp (DISPATCHER)
    - admin:admin (ADMIN)
    """
    # Find user by username (stored in full_name field)
    users = crud.get_users(db)
    user = None

    for u in users:
        if str(u.name) == credentials.username:
            user = u
            break

    if not user:
        return LoginResponse(
            success=False, message="Incorrect username or password", user=None
        )

    # Verify password
    if not verify_password(credentials.password, user.hashed_password):
        return LoginResponse(
            success=False, message="Incorrect username or password", user=None
        )

    # Check if user is deleted
    if user.deleted_at is not None:
        return LoginResponse(
            success=False, message="Account has been deactivated", user=None
        )

    # Create JWT access token
    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "user_id": str(user.id),
            "username": user.name,
            "email": user.email,
            "role": user.role,
        }
    )

    return LoginResponse(
        success=True,
        message="Login successful",
        access_token=access_token,
        token_type="bearer",
        user={
            "id": str(user.id),
            "username": user.name,
            "email": user.email,
            "role": user.role,
            "badge": user.badge,
            "verified_reports_count": user.reputation_points,
        },
    )
