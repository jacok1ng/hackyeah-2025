from typing import List

import crud
from database import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from models import RouteSegment
from sqlalchemy.orm import Session

router = APIRouter(prefix="/route-segments", tags=["route-segments"])


@router.get("/", response_model=List[RouteSegment])
def get_all_route_segments(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    return crud.get_route_segments(db, skip=skip, limit=limit)


@router.get("/by-stops", response_model=RouteSegment)
def get_route_segment_by_stops(
    from_stop_id: str, to_stop_id: str, db: Session = Depends(get_db)
):
    """Get route segment between two specific stops."""
    db_segment = crud.get_route_segment_by_stops(db, from_stop_id, to_stop_id)
    if not db_segment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Route segment not found between these stops",
        )
    return db_segment


@router.get("/by-shape/{shape_id}", response_model=RouteSegment)
def get_route_segment_by_shape_id(shape_id: str, db: Session = Depends(get_db)):
    """Get route segment by its shape_id."""
    db_segment = crud.get_route_segment_by_shape_id(db, shape_id)
    if not db_segment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Route segment not found"
        )
    return db_segment


@router.get("/{segment_id}", response_model=RouteSegment)
def get_route_segment(segment_id: str, db: Session = Depends(get_db)):
    """Get route segment by ID."""
    db_segment = crud.get_route_segment(db, segment_id)
    if not db_segment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Route segment not found"
        )
    return db_segment
