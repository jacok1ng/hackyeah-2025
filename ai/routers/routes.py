from typing import List

import crud
from database import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from models import Route, RouteCreate, RouteUpdate
from sqlalchemy.orm import Session

router = APIRouter(prefix="/routes", tags=["routes"])


@router.post("/", response_model=Route, status_code=status.HTTP_201_CREATED)
def create_route(route: RouteCreate, db: Session = Depends(get_db)):
    return crud.create_route(db, route)


@router.get("/", response_model=List[Route])
def get_all_routes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_routes(db, skip=skip, limit=limit)


@router.get("/{route_id}", response_model=Route)
def get_route(route_id: str, db: Session = Depends(get_db)):
    db_route = crud.get_route(db, route_id)
    if not db_route:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Route not found"
        )
    return db_route


@router.put("/{route_id}", response_model=Route)
def update_route(
    route_id: str, route_update: RouteUpdate, db: Session = Depends(get_db)
):
    db_route = crud.update_route(db, route_id, route_update)
    if not db_route:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Route not found"
        )
    return db_route


@router.delete("/{route_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_route(route_id: str, db: Session = Depends(get_db)):
    success = crud.delete_route(db, route_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Route not found"
        )
