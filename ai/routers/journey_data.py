from datetime import datetime
from typing import List, Union

import crud
from crud import journey_tracking
from database import get_db
from db_models import Stop
from db_models import UserJourney as UserJourneyDB
from db_models import UserJourneyStop as UserJourneyStopDB
from dependencies import get_current_user, require_admin_or_dispatcher
from fastapi import APIRouter, Depends, HTTPException, status
from models import JourneyData, JourneyDataCreate, JourneyProgressResponse
from sqlalchemy.orm import Session

router = APIRouter(prefix="/journey-data", tags=["journey-data"])


@router.post(
    "/",
    response_model=Union[JourneyData, JourneyProgressResponse],
    status_code=status.HTTP_201_CREATED,
)
def create_journey_data(
    journey_data: JourneyDataCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Create sensor data for a vehicle trip (GPS tracking from mobile app).

    If user_journey_id is provided and journey is in progress, returns:
    - Real-time progress information
    - Distance/time to next stop and journey end
    - On-time status
    - Remaining stops

    Otherwise, returns the created JourneyData record.

    Mobile app should send GPS updates regularly (e.g., every 10-30 seconds).
    """
    # Create the journey data record
    created_data = crud.create_journey_data(db, journey_data)

    # If user_journey_id is not provided, just return the data
    if not journey_data.user_journey_id:
        return created_data

    # Get the user journey
    user_journey = (
        db.query(UserJourneyDB)
        .filter(UserJourneyDB.id == str(journey_data.user_journey_id))
        .first()
    )

    # If journey not in progress, just return the data
    if not user_journey or not bool(user_journey.is_in_progress):
        return created_data

    # Calculate real-time progress
    current_lat = journey_data.latitude
    current_lon = journey_data.longitude

    if current_lat is None or current_lon is None:
        return created_data

    # Find nearest stop and update current_stop_index
    nearest = journey_tracking.find_nearest_stop_on_journey(
        db, str(journey_data.user_journey_id), current_lat, current_lon
    )

    if nearest:
        # Update current stop index if we're close enough (within 200 meters)
        if nearest["distance"] < 200:
            new_index = int(nearest["stop_index"])
            current_idx = int(user_journey.current_stop_index)  # type: ignore
            if new_index > current_idx:
                user_journey.current_stop_index = new_index  # type: ignore
                db.commit()

    # Get journey stops for progress calculation
    journey_stops = (
        db.query(UserJourneyStopDB)
        .filter(UserJourneyStopDB.user_journey_id == str(journey_data.user_journey_id))
        .order_by(UserJourneyStopDB.stop_order)
        .all()
    )

    total_stops = len(journey_stops)
    current_stop_index = int(user_journey.current_stop_index)  # type: ignore

    # Calculate distances and times
    distance_info = journey_tracking.calculate_remaining_distance(
        db,
        str(journey_data.user_journey_id),
        current_stop_index,
        current_lat,
        current_lon,
    )

    # Get next stop info
    next_stop_name = None
    if distance_info["next_stop"]:
        next_stop_name = str(distance_info["next_stop"].name)

    # Calculate times
    time_to_next = None
    time_to_end = None
    if distance_info["distance_to_next_stop"]:
        time_to_next = journey_tracking.estimate_time_to_arrival(
            distance_info["distance_to_next_stop"], average_speed_kmh=30.0
        )
    if distance_info["distance_to_end"]:
        time_to_end = journey_tracking.estimate_time_to_arrival(
            distance_info["distance_to_end"], average_speed_kmh=30.0
        )

    # Check if on time
    elapsed_minutes = 0.0
    started = user_journey.started_at
    if started is not None:  # type: ignore
        elapsed = datetime.now() - started  # type: ignore
        elapsed_minutes = elapsed.total_seconds() / 60.0

    timing_info = journey_tracking.check_if_on_time(
        db, str(journey_data.user_journey_id), current_stop_index, elapsed_minutes
    )

    # Get remaining stop names
    remaining_stop_names = []
    for i in range(current_stop_index, total_stops):
        stop = db.query(Stop).filter(Stop.id == str(journey_stops[i].stop_id)).first()
        if stop:
            remaining_stop_names.append(str(stop.name))

    # Calculate progress percentage
    progress_percentage = (
        (current_stop_index / total_stops * 100) if total_stops > 0 else 0.0
    )

    # Check if journey completed (at last stop and close to it)
    journey_completed = False
    feedback_requested = bool(user_journey.feedback_requested)  # type: ignore

    # Detect journey completion:
    # - User is at the last stop (current_stop_index == total_stops - 1)
    # - Distance to end is very small (<100 meters)
    if current_stop_index >= total_stops - 1:
        if distance_info["distance_to_end"] and distance_info["distance_to_end"] < 100:
            journey_completed = True

            # Request feedback if not already requested
            if not feedback_requested:
                user_journey.feedback_requested = True  # type: ignore
                db.commit()
                feedback_requested = True

    return JourneyProgressResponse(
        on_time=timing_info["on_time"],
        delay_minutes=timing_info.get("delay_minutes"),
        distance_to_next_stop_meters=distance_info["distance_to_next_stop"],
        time_to_next_stop_minutes=time_to_next,
        next_stop_name=next_stop_name,
        distance_to_end_meters=distance_info["distance_to_end"],
        time_to_end_minutes=time_to_end,
        remaining_stops=total_stops - current_stop_index,
        remaining_stop_names=remaining_stop_names,
        current_stop_index=current_stop_index,
        total_stops=total_stops,
        progress_percentage=progress_percentage,
        feedback_requested=feedback_requested,
        journey_completed=journey_completed,
    )


@router.get("/", response_model=List[JourneyData])
def get_all_journey_data(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    _=Depends(require_admin_or_dispatcher),
):
    """Get all sensor data. Requires ADMIN or DISPATCHER role for analytics."""
    return crud.get_journey_data_list(db, skip=skip, limit=limit)


@router.get("/{journey_data_id}", response_model=JourneyData)
def get_journey_data(
    journey_data_id: str,
    db: Session = Depends(get_db),
    _=Depends(require_admin_or_dispatcher),
):
    """Get specific sensor data. Requires ADMIN or DISPATCHER role."""
    db_journey_data = crud.get_journey_data(db, journey_data_id)
    if not db_journey_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="JourneyData not found"
        )
    return db_journey_data
