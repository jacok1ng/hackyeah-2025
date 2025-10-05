from typing import List

import crud
from database import get_db
from dependencies import require_admin, require_admin_or_dispatcher
from fastapi import APIRouter, Depends, HTTPException, status
from models import Vehicle, VehicleCreate, VehicleUpdate
from sqlalchemy.orm import Session

router = APIRouter(prefix="/vehicles", tags=["vehicles"])


@router.post("/", response_model=Vehicle, status_code=status.HTTP_201_CREATED)
def create_vehicle(
    vehicle: VehicleCreate,
    db: Session = Depends(get_db),
    _=Depends(require_admin_or_dispatcher),
):
    """Create a new vehicle. Requires ADMIN or DISPATCHER role."""
    return crud.create_vehicle(db, vehicle)


@router.get("/", response_model=List[Vehicle])
def get_all_vehicles(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_vehicles(db, skip=skip, limit=limit)


@router.get("/{vehicle_id}", response_model=Vehicle)
def get_vehicle(vehicle_id: str, db: Session = Depends(get_db)):
    db_vehicle = crud.get_vehicle(db, vehicle_id)
    if not db_vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found"
        )
    return db_vehicle


@router.put("/{vehicle_id}", response_model=Vehicle)
def update_vehicle(
    vehicle_id: str,
    vehicle_update: VehicleUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_admin_or_dispatcher),
):
    """Update a vehicle. Requires ADMIN or DISPATCHER role."""
    db_vehicle = crud.update_vehicle(db, vehicle_id, vehicle_update)
    if not db_vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found"
        )
    return db_vehicle


@router.delete("/{vehicle_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_vehicle(
    vehicle_id: str, db: Session = Depends(get_db), _=Depends(require_admin)
):
    """Delete a vehicle. Requires ADMIN role."""
    success = crud.delete_vehicle(db, vehicle_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found"
        )
