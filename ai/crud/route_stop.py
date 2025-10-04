from typing import List, Optional

import db_models
from models import RouteStopCreate, RouteStopUpdate
from sqlalchemy.orm import Session


def create_route_stop(db: Session, route_stop: RouteStopCreate) -> db_models.RouteStop:
    db_route_stop = db_models.RouteStop(**route_stop.model_dump())
    db.add(db_route_stop)
    db.commit()
    db.refresh(db_route_stop)
    return db_route_stop


def get_route_stop(db: Session, route_stop_id: str) -> Optional[db_models.RouteStop]:
    return (
        db.query(db_models.RouteStop)
        .filter(db_models.RouteStop.id == route_stop_id)
        .first()
    )


def get_route_stops(
    db: Session, skip: int = 0, limit: int = 100
) -> List[db_models.RouteStop]:
    return db.query(db_models.RouteStop).offset(skip).limit(limit).all()


def update_route_stop(
    db: Session, route_stop_id: str, route_stop_update: RouteStopUpdate
) -> Optional[db_models.RouteStop]:
    db_route_stop = get_route_stop(db, route_stop_id)
    if not db_route_stop:
        return None

    update_data = route_stop_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_route_stop, field, value)

    db.commit()
    db.refresh(db_route_stop)
    return db_route_stop


def delete_route_stop(db: Session, route_stop_id: str) -> bool:
    db_route_stop = get_route_stop(db, route_stop_id)
    if not db_route_stop:
        return False
    db.delete(db_route_stop)
    db.commit()
    return True
