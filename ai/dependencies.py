"""
Authentication dependencies for FastAPI routes.
"""

from typing import Optional

import crud
from auth import decode_access_token
from database import get_db
from enums import UserRole
from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """
    Get current user from JWT token in Authorization header.
    Expects: Authorization: Bearer <token>
    """
    token = credentials.credentials

    # Decode JWT token
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Extract user_id from token
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Get user from database
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if user.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account has been deactivated",
        )

    return user


def get_current_user_optional(
    user_id: Optional[str] = Header(None, alias="X-User-ID"),
    db: Session = Depends(get_db),
):
    """
    Get current user from X-User-ID header (optional).
    Returns None if no user_id provided.
    """
    if not user_id:
        return None

    user = crud.get_user(db, user_id)
    if not user or user.deleted_at is not None:
        return None

    return user


def require_role(allowed_roles: list[str]):
    """
    Dependency to check if user has required role.
    Usage: dependencies=[Depends(require_role(["ADMIN", "DISPATCHER"]))]
    """

    def role_checker(current_user=Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {', '.join(allowed_roles)}",
            )
        return current_user

    return role_checker


# Predefined role dependencies for common cases
def require_admin(current_user=Depends(get_current_user)):
    """Require ADMIN role."""
    if current_user.role != UserRole.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Admin role required.",
        )
    return current_user


def require_admin_or_dispatcher(current_user=Depends(get_current_user)):
    """Require ADMIN or DISPATCHER role."""
    if current_user.role not in [UserRole.ADMIN.value, UserRole.DISPATCHER.value]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Admin or Dispatcher role required.",
        )
    return current_user


def require_driver_or_dispatcher(current_user=Depends(get_current_user)):
    """Require DRIVER or DISPATCHER role."""
    if current_user.role not in [UserRole.DRIVER.value, UserRole.DISPATCHER.value]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Driver or Dispatcher role required.",
        )
    return current_user
