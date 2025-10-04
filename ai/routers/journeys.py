from typing import List

import crud
from database import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from models import Journey, JourneyCreate, JourneyUpdate
from sqlalchemy.orm import Session

router = APIRouter(prefix="/journeys", tags=["journeys"])


@router.post("/", response_model=Journey, status_code=status.HTTP_201_CREATED)
def create_journey(journey: JourneyCreate, db: Session = Depends(get_db)):
    return crud.create_journey(db, journey)


@router.get("/", response_model=List[Journey])
def get_all_journeys(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_journeys(db, skip=skip, limit=limit)


@router.get("/{journey_id}", response_model=Journey)
def get_journey(journey_id: str, db: Session = Depends(get_db)):
    db_journey = crud.get_journey(db, journey_id)
    if not db_journey:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Journey not found"
        )
    return db_journey


@router.put("/{journey_id}", response_model=Journey)
def update_journey(
    journey_id: str, journey_update: JourneyUpdate, db: Session = Depends(get_db)
):
    db_journey = crud.update_journey(db, journey_id, journey_update)
    if not db_journey:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Journey not found"
        )
    return db_journey


@router.delete("/{journey_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_journey(journey_id: str, db: Session = Depends(get_db)):
    success = crud.delete_journey(db, journey_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Journey not found"
        )
