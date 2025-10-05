from typing import List, Optional

import db_models
from models import ShapePointCreate, ShapePointUpdate
from sqlalchemy.orm import Session


def create_shape_point(
    db: Session, shape_id: str, point: ShapePointCreate
) -> db_models.ShapePoint:
    point_data = point.model_dump()
    point_data["shape_id"] = shape_id
    db_point = db_models.ShapePoint(**point_data)
    db.add(db_point)
    db.commit()
    db.refresh(db_point)
    return db_point


def create_shape_points_batch(
    db: Session, shape_id: str, points: List[ShapePointCreate]
) -> List[db_models.ShapePoint]:
    """Create multiple shape points at once for better performance."""
    db_points = []
    for point in points:
        point_data = point.model_dump()
        point_data["shape_id"] = shape_id
        db_point = db_models.ShapePoint(**point_data)
        db_points.append(db_point)

    db.add_all(db_points)
    db.commit()
    for db_point in db_points:
        db.refresh(db_point)
    return db_points


def get_shape_point(db: Session, point_id: str) -> Optional[db_models.ShapePoint]:
    return (
        db.query(db_models.ShapePoint)
        .filter(db_models.ShapePoint.id == point_id)
        .first()
    )


def get_shape_points_by_shape_id(
    db: Session, shape_id: str
) -> List[db_models.ShapePoint]:
    """Get all points for a shape, ordered by sequence."""
    return (
        db.query(db_models.ShapePoint)
        .filter(db_models.ShapePoint.shape_id == shape_id)
        .order_by(db_models.ShapePoint.shape_pt_sequence)
        .all()
    )


def get_shape_points(
    db: Session, skip: int = 0, limit: int = 100
) -> List[db_models.ShapePoint]:
    return db.query(db_models.ShapePoint).offset(skip).limit(limit).all()


def update_shape_point(
    db: Session, point_id: str, point_update: ShapePointUpdate
) -> Optional[db_models.ShapePoint]:
    db_point = get_shape_point(db, point_id)
    if not db_point:
        return None

    update_data = point_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_point, field, value)

    db.commit()
    db.refresh(db_point)
    return db_point


def delete_shape_point(db: Session, point_id: str) -> bool:
    db_point = get_shape_point(db, point_id)
    if not db_point:
        return False
    db.delete(db_point)
    db.commit()
    return True


def delete_all_shape_points(db: Session, shape_id: str) -> int:
    """Delete all points for a shape. Returns number of deleted points."""
    result = (
        db.query(db_models.ShapePoint)
        .filter(db_models.ShapePoint.shape_id == shape_id)
        .delete()
    )
    db.commit()
    return result
