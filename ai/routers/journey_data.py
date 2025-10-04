from typing import List

import crud
from database import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from models import JourneyData, JourneyDataCreate, JourneyDataUpdate
from sqlalchemy.orm import Session

router = APIRouter(prefix="/journey-data", tags=["journey-data"])


@router.post("/", response_model=JourneyData, status_code=status.HTTP_201_CREATED)
def create_journey_data(journey_data: JourneyDataCreate, db: Session = Depends(get_db)):
    return crud.create_journey_data(db, journey_data)


@router.get("/", response_model=List[JourneyData])
def get_all_journey_data(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    return crud.get_journey_data_list(db, skip=skip, limit=limit)


@router.get("/{journey_data_id}", response_model=JourneyData)
def get_journey_data(journey_data_id: str, db: Session = Depends(get_db)):
    db_journey_data = crud.get_journey_data(db, journey_data_id)
    if not db_journey_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="JourneyData not found"
        )
    return db_journey_data


@router.put("/{journey_data_id}", response_model=JourneyData)
def update_journey_data(
    journey_data_id: str,
    journey_data_update: JourneyDataUpdate,
    db: Session = Depends(get_db),
):
    db_journey_data = crud.update_journey_data(db, journey_data_id, journey_data_update)
    if not db_journey_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="JourneyData not found"
        )
    return db_journey_data


@router.delete("/{journey_data_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_journey_data(journey_data_id: str, db: Session = Depends(get_db)):
    success = crud.delete_journey_data(db, journey_data_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="JourneyData not found"
        )
