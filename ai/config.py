"""
Application configuration from environment variables.
"""

import os

from dotenv import load_dotenv

# Load .env file if it exists
load_dotenv()


class Settings:
    """Application settings."""

    # Google Maps API
    GOOGLE_MAPS_API_KEY: str = os.getenv("GOOGLE_MAPS_API_KEY", "")

    # JWT Configuration
    JWT_SECRET_KEY: str = os.getenv(
        "JWT_SECRET_KEY", "your-secret-key-change-in-production"
    )
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./transportation.db")

    @classmethod
    def validate(cls):
        """Validate required settings."""
        if not cls.GOOGLE_MAPS_API_KEY:
            print(
                "⚠️  WARNING: GOOGLE_MAPS_API_KEY not set. "
                "Google Maps API will not work."
            )


# Create singleton instance
settings = Settings()

# Validate on import
settings.validate()
