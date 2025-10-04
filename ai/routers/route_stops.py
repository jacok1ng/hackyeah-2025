from typing import List

import crud
from database import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from models import RouteStop, RouteStopCreate, RouteStopUpdate
from sqlalchemy.orm import Session

router = APIRouter(prefix="/route-stops", tags=["route-stops"])


@router.post("/", response_model=RouteStop, status_code=status.HTTP_201_CREATED)
def create_route_stop(route_stop: RouteStopCreate, db: Session = Depends(get_db)):
    return crud.create_route_stop(db, route_stop)


@router.get("/", response_model=List[RouteStop])
def get_all_route_stops(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_route_stops(db, skip=skip, limit=limit)


@router.get("/{route_stop_id}", response_model=RouteStop)
def get_route_stop(route_stop_id: str, db: Session = Depends(get_db)):
    db_route_stop = crud.get_route_stop(db, route_stop_id)
    if not db_route_stop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="RouteStop not found"
        )
    return db_route_stop


@router.put("/{route_stop_id}", response_model=RouteStop)
def update_route_stop(
    route_stop_id: str,
    route_stop_update: RouteStopUpdate,
    db: Session = Depends(get_db),
):
    db_route_stop = crud.update_route_stop(db, route_stop_id, route_stop_update)
    if not db_route_stop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="RouteStop not found"
        )
    return db_route_stop


@router.delete("/{route_stop_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_route_stop(route_stop_id: str, db: Session = Depends(get_db)):
    success = crud.delete_route_stop(db, route_stop_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="RouteStop not found"
        )
