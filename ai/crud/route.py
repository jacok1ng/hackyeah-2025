from typing import List, Optional

import db_models
from models import RouteCreate, RouteUpdate
from sqlalchemy.orm import Session


def create_route(db: Session, route: RouteCreate) -> db_models.Route:
    db_route = db_models.Route(**route.model_dump())
    db.add(db_route)
    db.commit()
    db.refresh(db_route)
    return db_route


def get_route(db: Session, route_id: str) -> Optional[db_models.Route]:
    return db.query(db_models.Route).filter(db_models.Route.id == route_id).first()


def get_routes(db: Session, skip: int = 0, limit: int = 100) -> List[db_models.Route]:
    return db.query(db_models.Route).offset(skip).limit(limit).all()


def update_route(
    db: Session, route_id: str, route_update: RouteUpdate
) -> Optional[db_models.Route]:
    db_route = get_route(db, route_id)
    if not db_route:
        return None

    update_data = route_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_route, field, value)

    db.commit()
    db.refresh(db_route)
    return db_route


def delete_route(db: Session, route_id: str) -> bool:
    db_route = get_route(db, route_id)
    if not db_route:
        return False
    db.delete(db_route)
    db.commit()
    return True
