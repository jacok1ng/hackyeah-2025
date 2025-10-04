from typing import List, Optional

import db_models
from models import RouteSegmentCreate, RouteSegmentUpdate
from sqlalchemy.orm import Session


def create_route_segment(
    db: Session, route_segment: RouteSegmentCreate
) -> db_models.RouteSegment:
    db_segment = db_models.RouteSegment(**route_segment.model_dump())
    db.add(db_segment)
    db.commit()
    db.refresh(db_segment)
    return db_segment


def get_route_segment(db: Session, segment_id: str) -> Optional[db_models.RouteSegment]:
    return (
        db.query(db_models.RouteSegment)
        .filter(db_models.RouteSegment.id == segment_id)
        .first()
    )


def get_route_segment_by_shape_id(
    db: Session, shape_id: str
) -> Optional[db_models.RouteSegment]:
    return (
        db.query(db_models.RouteSegment)
        .filter(db_models.RouteSegment.shape_id == shape_id)
        .first()
    )


def get_route_segment_by_stops(
    db: Session, from_stop_id: str, to_stop_id: str
) -> Optional[db_models.RouteSegment]:
    """Get route segment between two specific stops."""
    return (
        db.query(db_models.RouteSegment)
        .filter(
            db_models.RouteSegment.from_stop_id == from_stop_id,
            db_models.RouteSegment.to_stop_id == to_stop_id,
        )
        .first()
    )


def get_route_segments(
    db: Session, skip: int = 0, limit: int = 100
) -> List[db_models.RouteSegment]:
    return db.query(db_models.RouteSegment).offset(skip).limit(limit).all()


def update_route_segment(
    db: Session, segment_id: str, segment_update: RouteSegmentUpdate
) -> Optional[db_models.RouteSegment]:
    db_segment = get_route_segment(db, segment_id)
    if not db_segment:
        return None

    update_data = segment_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_segment, field, value)

    db.commit()
    db.refresh(db_segment)
    return db_segment


def delete_route_segment(db: Session, segment_id: str) -> bool:
    db_segment = get_route_segment(db, segment_id)
    if not db_segment:
        return False
    db.delete(db_segment)
    db.commit()
    return True
