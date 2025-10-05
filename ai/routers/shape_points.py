from typing import List

import crud
from database import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from models import ShapePoint
from sqlalchemy.orm import Session

router = APIRouter(prefix="/shape-points", tags=["shape-points"])


@router.get("/", response_model=List[ShapePoint])
def get_all_shape_points(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    return crud.get_shape_points(db, skip=skip, limit=limit)


@router.get("/by-shape/{shape_id}", response_model=List[ShapePoint])
def get_shape_points_by_shape_id(shape_id: str, db: Session = Depends(get_db)):
    """
    Get all GPS points for a specific route segment, ordered by sequence.
    This returns the detailed path between two stops.
    """
    points = crud.get_shape_points_by_shape_id(db, shape_id)
    if not points:
        # Check if shape_id exists
        segment = crud.get_route_segment_by_shape_id(db, shape_id)
        if not segment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Route segment with shape_id '{shape_id}' not found",
            )
    return points


@router.get("/{point_id}", response_model=ShapePoint)
def get_shape_point(point_id: str, db: Session = Depends(get_db)):
    """Get a single GPS point by ID."""
    db_point = crud.get_shape_point(db, point_id)
    if not db_point:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Shape point not found"
        )
    return db_point
