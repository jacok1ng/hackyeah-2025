"""
CRUD operations for feedback/surveys.
Simplified to only CREATE and GET ALL operations.
"""

from typing import List

from db_models import Feedback
from models import FeedbackCreate
from sqlalchemy.orm import Session


def create_feedback(db: Session, feedback: FeedbackCreate, user_id: str) -> Feedback:
    """Create a new feedback entry."""
    db_feedback = Feedback(
        user_id=user_id,
        user_journey_id=str(feedback.user_journey_id),
        vehicle_trip_id=(
            str(feedback.vehicle_trip_id) if feedback.vehicle_trip_id else None
        ),
        overall_rating=feedback.overall_rating,
        cleanliness_rating=feedback.cleanliness_rating,
        punctuality_rating=feedback.punctuality_rating,
        driver_rating=feedback.driver_rating,
        comfort_rating=feedback.comfort_rating,
        comment=feedback.comment,
        improvements=feedback.improvements,
    )
    db.add(db_feedback)
    db.commit()
    db.refresh(db_feedback)
    return db_feedback


def get_all_feedbacks(db: Session, skip: int = 0, limit: int = 100) -> List[Feedback]:
    """Get all feedbacks (for admin/analytics)."""
    return db.query(Feedback).offset(skip).limit(limit).all()
