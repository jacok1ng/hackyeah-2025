from typing import List

import crud
from database import get_db
from dependencies import require_admin_or_dispatcher
from fastapi import APIRouter, Depends, HTTPException, status
from models import RouteStop, RouteStopCreate, RouteStopUpdate
from sqlalchemy.orm import Session

router = APIRouter(prefix="/route-stops", tags=["route-stops"])


@router.post("/", response_model=RouteStop, status_code=status.HTTP_201_CREATED)
def create_route_stop(
    route_stop: RouteStopCreate,
    db: Session = Depends(get_db),
    _=Depends(require_admin_or_dispatcher),
):
    """Create a new route stop. Requires ADMIN or DISPATCHER role."""
    return crud.create_route_stop(db, route_stop)


@router.put("/{route_stop_id}", response_model=RouteStop)
def update_route_stop(
    route_stop_id: str,
    route_stop_update: RouteStopUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_admin_or_dispatcher),
):
    """Update a route stop. Requires ADMIN or DISPATCHER role."""
    db_route_stop = crud.update_route_stop(db, route_stop_id, route_stop_update)
    if not db_route_stop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="RouteStop not found"
        )
    return db_route_stop


@router.delete("/{route_stop_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_route_stop(
    route_stop_id: str,
    db: Session = Depends(get_db),
    _=Depends(require_admin_or_dispatcher),
):
    """Delete a route stop. Requires ADMIN or DISPATCHER role."""
    success = crud.delete_route_stop(db, route_stop_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="RouteStop not found"
        )
