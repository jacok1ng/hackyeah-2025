from datetime import datetime
from typing import List, Optional

import db_models
from models import VehicleCreate, VehicleUpdate
from sqlalchemy.orm import Session


def create_vehicle(db: Session, vehicle: VehicleCreate) -> db_models.Vehicle:
    db_vehicle = db_models.Vehicle(**vehicle.model_dump())
    db.add(db_vehicle)
    db.commit()
    db.refresh(db_vehicle)
    return db_vehicle


def get_vehicle(db: Session, vehicle_id: str) -> Optional[db_models.Vehicle]:
    return (
        db.query(db_models.Vehicle).filter(db_models.Vehicle.id == vehicle_id).first()
    )


def get_vehicles(
    db: Session, skip: int = 0, limit: int = 100
) -> List[db_models.Vehicle]:
    return db.query(db_models.Vehicle).offset(skip).limit(limit).all()


def update_vehicle(
    db: Session, vehicle_id: str, vehicle_update: VehicleUpdate
) -> Optional[db_models.Vehicle]:
    db_vehicle = get_vehicle(db, vehicle_id)
    if not db_vehicle:
        return None

    update_data = vehicle_update.model_dump(exclude_unset=True)

    if update_data:
        for field, value in update_data.items():
            setattr(db_vehicle, field, value)

        setattr(db_vehicle, "updated_at", datetime.now())

    db.commit()
    db.refresh(db_vehicle)
    return db_vehicle


def delete_vehicle(db: Session, vehicle_id: str) -> bool:
    db_vehicle = get_vehicle(db, vehicle_id)
    if not db_vehicle:
        return False
    db.delete(db_vehicle)
    db.commit()
    return True
