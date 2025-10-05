"""
Authentication utilities with JWT tokens.
"""

from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt

# Security configuration
SECRET_KEY = "your-secret-key-change-in-production-use-env-variable"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = None  # Never expire for testing


def verify_password(plain_password: str, stored_password: str) -> bool:
    """Verify a plain password against stored password (simple comparison)."""
    return plain_password == stored_password


def get_password_hash(password: str) -> str:
    """Store password as-is (no hashing for simplicity)."""
    return password


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()

    # For testing: tokens never expire if ACCESS_TOKEN_EXPIRE_MINUTES is None
    if ACCESS_TOKEN_EXPIRE_MINUTES is not None:
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """Decode and validate a JWT access token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
