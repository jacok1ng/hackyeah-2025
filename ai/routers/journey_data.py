from typing import List

import crud
from database import get_db
from dependencies import require_admin, require_admin_or_dispatcher
from fastapi import APIRouter, Depends, HTTPException, status
from models import JourneyData, JourneyDataCreate
from sqlalchemy.orm import Session

router = APIRouter(prefix="/journey-data", tags=["journey-data"])


@router.post("/", response_model=JourneyData, status_code=status.HTTP_201_CREATED)
def create_journey_data(journey_data: JourneyDataCreate, db: Session = Depends(get_db)):
    """
    Create sensor data for a vehicle trip.
    Can be added by all users but must be connected to a specific vehicle trip.
    """
    return crud.create_journey_data(db, journey_data)


@router.get("/", response_model=List[JourneyData])
def get_all_journey_data(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    _=Depends(require_admin_or_dispatcher),
):
    """Get all sensor data. Requires ADMIN or DISPATCHER role for analytics."""
    return crud.get_journey_data_list(db, skip=skip, limit=limit)


@router.get("/{journey_data_id}", response_model=JourneyData)
def get_journey_data(
    journey_data_id: str,
    db: Session = Depends(get_db),
    _=Depends(require_admin_or_dispatcher),
):
    """Get specific sensor data. Requires ADMIN or DISPATCHER role."""
    db_journey_data = crud.get_journey_data(db, journey_data_id)
    if not db_journey_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="JourneyData not found"
        )
    return db_journey_data
