from typing import List, Optional

import db_models
from models import UserJourneyStopCreate, UserJourneyStopUpdate
from sqlalchemy.orm import Session


def create_user_journey_stop(
    db: Session, user_journey_id: str, stop: UserJourneyStopCreate
) -> db_models.UserJourneyStop:
    stop_data = stop.model_dump()
    stop_data["user_journey_id"] = user_journey_id
    db_stop = db_models.UserJourneyStop(**stop_data)
    db.add(db_stop)
    db.commit()
    db.refresh(db_stop)
    return db_stop


def get_user_journey_stop(
    db: Session, stop_id: str
) -> Optional[db_models.UserJourneyStop]:
    return (
        db.query(db_models.UserJourneyStop)
        .filter(db_models.UserJourneyStop.id == stop_id)
        .first()
    )


def get_user_journey_stops(
    db: Session, user_journey_id: str
) -> List[db_models.UserJourneyStop]:
    """Get all stops for a user journey, ordered by stop_order."""
    return (
        db.query(db_models.UserJourneyStop)
        .filter(db_models.UserJourneyStop.user_journey_id == user_journey_id)
        .order_by(db_models.UserJourneyStop.stop_order)
        .all()
    )


def update_user_journey_stop(
    db: Session, stop_id: str, stop_update: UserJourneyStopUpdate
) -> Optional[db_models.UserJourneyStop]:
    db_stop = get_user_journey_stop(db, stop_id)
    if not db_stop:
        return None

    update_data = stop_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_stop, field, value)

    db.commit()
    db.refresh(db_stop)
    return db_stop


def delete_user_journey_stop(db: Session, stop_id: str) -> bool:
    db_stop = get_user_journey_stop(db, stop_id)
    if not db_stop:
        return False
    db.delete(db_stop)
    db.commit()
    return True


def delete_all_user_journey_stops(db: Session, user_journey_id: str) -> int:
    """Delete all stops for a user journey. Returns number of deleted stops."""
    result = (
        db.query(db_models.UserJourneyStop)
        .filter(db_models.UserJourneyStop.user_journey_id == user_journey_id)
        .delete()
    )
    db.commit()
    return result
