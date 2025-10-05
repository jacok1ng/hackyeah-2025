"""
Delay prediction API endpoints.

Provides predictions for vehicle delays based on current conditions
and historical patterns.
"""

from typing import Dict, List, Optional

from crud import delay_prediction
from database import get_db
from dependencies import get_current_user
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

router = APIRouter(prefix="/delay-predictions", tags=["Delay Predictions"])


class DelayPredictionResponse(BaseModel):
    """Response model for delay prediction."""

    predicted_delay_minutes: float
    confidence: float
    components: Dict
    prediction_method: str
    note: str
    vehicle_trip_id: Optional[str] = None
    scheduled_departure: Optional[str] = None


class DelayStatisticsResponse(BaseModel):
    """Response model for delay statistics."""

    route_id: str
    period_days: int
    total_trips: int
    trips_with_data: int
    average_delay_minutes: float
    median_delay_minutes: float
    max_delay_minutes: float
    on_time_percentage: float
    note: str


@router.get(
    "/trip/{trip_id}",
    response_model=DelayPredictionResponse,
    summary="Predict delay for a specific trip",
)
def predict_trip_delay(
    trip_id: str,
    current_lat: Optional[float] = Query(None, description="Current latitude"),
    current_lon: Optional[float] = Query(None, description="Current longitude"),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    """
    Predict delay for a specific vehicle trip.

    Combines:
    - Current position vs schedule (if provided)
    - Historical delay patterns
    - Active incidents on route

    **Note:** This is a rule-based algorithm. In production, this should be
    replaced with a time series model (LSTM, Prophet, SARIMA) for better accuracy.

    **Parameters:**
    - `trip_id`: Vehicle trip ID
    - `current_lat`: Current vehicle latitude (optional)
    - `current_lon`: Current vehicle longitude (optional)

    **Returns:**
    - Predicted delay in minutes (positive = late, negative = early)
    - Confidence score (0-1)
    - Breakdown of prediction components
    """
    prediction = delay_prediction.predict_delay(db, trip_id, current_lat, current_lon)

    if "error" in prediction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=prediction["error"],
        )

    return DelayPredictionResponse(**prediction, vehicle_trip_id=trip_id)


@router.get(
    "/route/{route_id}",
    response_model=List[DelayPredictionResponse],
    summary="Predict delays for all upcoming trips on a route",
)
def predict_route_delays(
    route_id: str,
    next_hours: int = Query(2, ge=1, le=24, description="Look ahead hours"),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    """
    Predict delays for all upcoming trips on a route.

    Useful for:
    - Journey planning
    - Alternative route suggestions
    - Proactive notifications

    **Parameters:**
    - `route_id`: Route ID
    - `next_hours`: Number of hours to look ahead (1-24)

    **Returns:**
    - List of predictions for upcoming trips
    - Each prediction includes delay, confidence, and breakdown
    """
    predictions = delay_prediction.predict_delays_for_route(db, route_id, next_hours)

    if not predictions:
        return []

    return [DelayPredictionResponse(**p) for p in predictions]


@router.get(
    "/statistics/{route_id}",
    response_model=DelayStatisticsResponse,
    summary="Get delay statistics for a route",
)
def get_route_delay_statistics(
    route_id: str,
    days: int = Query(30, ge=1, le=90, description="Historical period in days"),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    """
    Get historical delay statistics for a route.

    Provides insights into:
    - Average delays
    - On-time performance
    - Route reliability

    **Parameters:**
    - `route_id`: Route ID
    - `days`: Number of days to analyze (1-90)

    **Returns:**
    - Statistical summary of delays
    - On-time percentage
    - Average and median delays

    **Use cases:**
    - Route reliability analysis
    - Identifying problematic routes
    - Training data collection for ML models
    """
    stats = delay_prediction.get_delay_statistics(db, route_id, days)

    if "error" in stats:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=stats["error"],
        )

    return DelayStatisticsResponse(**stats)


@router.post(
    "/train-model",
    summary="Trigger ML model training (placeholder)",
    tags=["Admin"],
)
def trigger_model_training(
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    """
    **PLACEHOLDER:** Trigger training of the time series model.

    This endpoint is a placeholder for future ML model integration.

    When implemented, it will:
    1. Collect historical data (JourneyData + delays)
    2. Train LSTM/Prophet/SARIMA model
    3. Validate model performance
    4. Deploy new model if better than current

    **Future Implementation:**
    - Extract features from last 90 days
    - Train model with cross-validation
    - A/B test against rule-based
    - Deploy if improvement >10%

    **Current Status:** Not implemented - using rule-based algorithm
    """
    return {
        "status": "not_implemented",
        "message": (
            "ML model training not yet implemented. "
            "Currently using rule-based delay prediction. "
            "Future models: LSTM, Prophet, SARIMA, or Transformer."
        ),
        "next_steps": [
            "1. Collect sufficient training data (>1000 trips with delays)",
            "2. Implement LSTM baseline model",
            "3. Train with hyperparameter tuning",
            "4. A/B test against rule-based",
            "5. Deploy if performance improvement >10%",
        ],
    }
