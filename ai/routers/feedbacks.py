"""
API endpoints for feedback/surveys.
Simplified to only CREATE and GET ALL (for admin analytics).
"""

from typing import List

import crud
from crud import feedback as feedback_crud
from database import get_db
from dependencies import get_current_user, require_admin_or_dispatcher
from fastapi import APIRouter, Depends, HTTPException, status
from models import Feedback, FeedbackCreate
from sqlalchemy.orm import Session

router = APIRouter(prefix="/feedbacks", tags=["feedbacks"])


@router.post("/", response_model=Feedback, status_code=status.HTTP_201_CREATED)
def create_feedback(
    feedback: FeedbackCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Submit feedback/survey for a completed journey.

    This endpoint is called after user completes a journey and receives
    feedback_requested=true in the JourneyProgressResponse.

    Ratings are on a 1-5 scale:
    - overall_rating: Overall satisfaction
    - cleanliness_rating: Vehicle cleanliness
    - punctuality_rating: On-time performance
    - driver_rating: Driver behavior/service
    - comfort_rating: Comfort level

    Text fields:
    - comment: General comments
    - improvements: What would you improve?
    """
    # Verify that journey belongs to user
    user_journey = crud.get_user_journey(db, str(feedback.user_journey_id))
    if not user_journey:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User journey not found"
        )

    if str(user_journey.user_id) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only submit feedback for your own journeys",
        )

    return feedback_crud.create_feedback(db, feedback, str(current_user.id))


@router.get("/", response_model=List[Feedback])
def get_all_feedbacks(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    _=Depends(require_admin_or_dispatcher),
):
    """
    Get all feedbacks for analytics.
    Requires ADMIN or DISPATCHER role.

    This endpoint is used for data analysis and improving service quality.
    """
    return feedback_crud.get_all_feedbacks(db, skip, limit)
