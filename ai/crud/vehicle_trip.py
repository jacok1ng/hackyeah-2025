from typing import List, Optional

import db_models
from models import VehicleTripCreate, VehicleTripUpdate
from sqlalchemy.orm import Session


def create_vehicle_trip(db: Session, vehicle_trip: VehicleTripCreate) -> db_models.VehicleTrip:
    db_vehicle_trip = db_models.VehicleTrip(**vehicle_trip.model_dump())
    db.add(db_vehicle_trip)
    db.commit()
    db.refresh(db_vehicle_trip)
    return db_vehicle_trip


def get_vehicle_trip(db: Session, vehicle_trip_id: str) -> Optional[db_models.VehicleTrip]:
    return (
        db.query(db_models.VehicleTrip).filter(db_models.VehicleTrip.id == vehicle_trip_id).first()
    )


def get_vehicle_trips(
    db: Session, skip: int = 0, limit: int = 100
) -> List[db_models.VehicleTrip]:
    return db.query(db_models.VehicleTrip).offset(skip).limit(limit).all()


def update_vehicle_trip(
    db: Session, vehicle_trip_id: str, vehicle_trip_update: VehicleTripUpdate
) -> Optional[db_models.VehicleTrip]:
    db_vehicle_trip = get_vehicle_trip(db, vehicle_trip_id)
    if not db_vehicle_trip:
        return None

    update_data = vehicle_trip_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_vehicle_trip, field, value)

    db.commit()
    db.refresh(db_vehicle_trip)
    return db_vehicle_trip


def delete_vehicle_trip(db: Session, vehicle_trip_id: str) -> bool:
    db_vehicle_trip = get_vehicle_trip(db, vehicle_trip_id)
    if not db_vehicle_trip:
        return False
    db.delete(db_vehicle_trip)
    db.commit()
    return True
