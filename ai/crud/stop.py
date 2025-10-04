from typing import List, Optional

import db_models
from models import StopCreate, StopUpdate
from sqlalchemy.orm import Session


def create_stop(db: Session, stop: StopCreate) -> db_models.Stop:
    db_stop = db_models.Stop(**stop.model_dump())
    db.add(db_stop)
    db.commit()
    db.refresh(db_stop)
    return db_stop


def get_stop(db: Session, stop_id: str) -> Optional[db_models.Stop]:
    return db.query(db_models.Stop).filter(db_models.Stop.id == stop_id).first()


def get_stops(db: Session, skip: int = 0, limit: int = 100) -> List[db_models.Stop]:
    return db.query(db_models.Stop).offset(skip).limit(limit).all()


def update_stop(
    db: Session, stop_id: str, stop_update: StopUpdate
) -> Optional[db_models.Stop]:
    db_stop = get_stop(db, stop_id)
    if not db_stop:
        return None

    update_data = stop_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_stop, field, value)

    db.commit()
    db.refresh(db_stop)
    return db_stop


def delete_stop(db: Session, stop_id: str) -> bool:
    db_stop = get_stop(db, stop_id)
    if not db_stop:
        return False
    db.delete(db_stop)
    db.commit()
    return True
