from typing import List

import crud
from database import get_db
from dependencies import require_admin, require_admin_or_dispatcher
from fastapi import APIRouter, Depends, HTTPException, status
from models import Stop, StopCreate, StopUpdate
from sqlalchemy.orm import Session

router = APIRouter(prefix="/stops", tags=["stops"])


@router.post("/", response_model=Stop, status_code=status.HTTP_201_CREATED)
def create_stop(
    stop: StopCreate,
    db: Session = Depends(get_db),
    _=Depends(require_admin_or_dispatcher),
):
    """Create a new stop. Requires ADMIN or DISPATCHER role."""
    return crud.create_stop(db, stop)


@router.get("/", response_model=List[Stop])
def get_all_stops(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_stops(db, skip=skip, limit=limit)


@router.get("/{stop_id}", response_model=Stop)
def get_stop(stop_id: str, db: Session = Depends(get_db)):
    db_stop = crud.get_stop(db, stop_id)
    if not db_stop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Stop not found"
        )
    return db_stop


@router.put("/{stop_id}", response_model=Stop)
def update_stop(
    stop_id: str,
    stop_update: StopUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_admin_or_dispatcher),
):
    """Update a stop. Requires ADMIN or DISPATCHER role."""
    db_stop = crud.update_stop(db, stop_id, stop_update)
    if not db_stop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Stop not found"
        )
    return db_stop


@router.delete("/{stop_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_stop(stop_id: str, db: Session = Depends(get_db), _=Depends(require_admin)):
    """Delete a stop. Requires ADMIN role."""
    success = crud.delete_stop(db, stop_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Stop not found"
        )
