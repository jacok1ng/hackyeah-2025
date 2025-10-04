from typing import List, Optional

import db_models
from models import VehicleTypeCreate
from sqlalchemy.orm import Session


def create_vehicle_type(
    db: Session, vehicle_type: VehicleTypeCreate
) -> db_models.VehicleType:
    db_vehicle_type = db_models.VehicleType(**vehicle_type.model_dump())
    db.add(db_vehicle_type)
    db.commit()
    db.refresh(db_vehicle_type)
    return db_vehicle_type


def get_vehicle_type(
    db: Session, vehicle_type_id: str
) -> Optional[db_models.VehicleType]:
    return (
        db.query(db_models.VehicleType)
        .filter(db_models.VehicleType.id == vehicle_type_id)
        .first()
    )


def get_vehicle_types(
    db: Session, skip: int = 0, limit: int = 100
) -> List[db_models.VehicleType]:
    return db.query(db_models.VehicleType).offset(skip).limit(limit).all()
