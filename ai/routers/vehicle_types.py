from typing import List

import crud
from database import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from models import VehicleType
from sqlalchemy.orm import Session

router = APIRouter(prefix="/vehicle-types", tags=["vehicle-types"])


@router.get("/", response_model=List[VehicleType])
def get_all_vehicle_types(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    """
    Get all vehicle types (read-only).
    Vehicle types are system-defined and cannot be created or modified by users.
    """
    return crud.get_vehicle_types(db, skip=skip, limit=limit)


@router.get("/{vehicle_type_id}", response_model=VehicleType)
def get_vehicle_type(vehicle_type_id: str, db: Session = Depends(get_db)):
    """
    Get a specific vehicle type by ID (read-only).
    Vehicle types are system-defined and cannot be created or modified by users.
    """
    db_vehicle_type = crud.get_vehicle_type(db, vehicle_type_id)
    if not db_vehicle_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="VehicleType not found"
        )
    return db_vehicle_type
