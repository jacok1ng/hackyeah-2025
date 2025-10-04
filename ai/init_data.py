"""
System initialization - creates hardcoded vehicle types.
This should be run on application startup to ensure vehicle types exist.
"""

from db_models import VehicleType
from sqlalchemy.orm import Session

VEHICLE_TYPES = [
    {
        "code": "BUS",
        "name": "Bus",
    },
    {
        "code": "TRAM",
        "name": "Tram",
    },
    {
        "code": "TRAIN",
        "name": "Train",
    },
]


def init_vehicle_types(db: Session) -> None:
    """
    Initialize vehicle types in the database.
    This function is idempotent - it will only create types that don't exist.
    """
    for vt_data in VEHICLE_TYPES:
        # Check if vehicle type already exists
        existing = (
            db.query(VehicleType).filter(VehicleType.code == vt_data["code"]).first()
        )

        if not existing:
            vehicle_type = VehicleType(**vt_data)
            db.add(vehicle_type)

    db.commit()
