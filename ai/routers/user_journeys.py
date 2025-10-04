from typing import List

import crud
from database import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from models import (
    FullRouteResponse,
    UserJourney,
    UserJourneyCreate,
    UserJourneyStop,
    UserJourneyStopCreate,
    UserJourneyStopUpdate,
    UserJourneyUpdate,
)
from sqlalchemy.orm import Session

router = APIRouter(prefix="/user-journeys", tags=["user-journeys"])


@router.post("/", response_model=UserJourney, status_code=status.HTTP_201_CREATED)
def create_user_journey(
    user_journey: UserJourneyCreate,
    user_id: str,
    db: Session = Depends(get_db),
):
    """
    Create a new user journey.
    - is_saved: True for saved journeys (up to 10 per user)
    - is_active: True for the currently active journey (only 1 per user)
    """
    return crud.create_user_journey(db, user_journey, user_id)


@router.get("/user/{user_id}", response_model=List[UserJourney])
def get_user_journeys(
    user_id: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    """Get all journeys for a specific user."""
    return crud.get_user_journeys(db, user_id, skip=skip, limit=limit)


@router.get("/user/{user_id}/saved", response_model=List[UserJourney])
def get_user_saved_journeys(user_id: str, db: Session = Depends(get_db)):
    """Get user's saved journeys (up to 10)."""
    return crud.get_user_saved_journeys(db, user_id)


@router.get("/user/{user_id}/active", response_model=UserJourney)
def get_user_active_journey(user_id: str, db: Session = Depends(get_db)):
    """Get user's currently active journey."""
    db_journey = crud.get_user_active_journey(db, user_id)
    if not db_journey:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active journey found for this user",
        )
    return db_journey


@router.get("/{journey_id}", response_model=UserJourney)
def get_user_journey(journey_id: str, db: Session = Depends(get_db)):
    db_journey = crud.get_user_journey(db, journey_id)
    if not db_journey:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User journey not found"
        )
    return db_journey


@router.put("/{journey_id}", response_model=UserJourney)
def update_user_journey(
    journey_id: str, journey_update: UserJourneyUpdate, db: Session = Depends(get_db)
):
    db_journey = crud.update_user_journey(db, journey_id, journey_update)
    if not db_journey:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User journey not found"
        )
    return db_journey


@router.delete("/{journey_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_journey(journey_id: str, db: Session = Depends(get_db)):
    success = crud.delete_user_journey(db, journey_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User journey not found"
        )


# UserJourneyStop endpoints
@router.post(
    "/{journey_id}/stops",
    response_model=UserJourneyStop,
    status_code=status.HTTP_201_CREATED,
)
def add_stop_to_journey(
    journey_id: str,
    stop: UserJourneyStopCreate,
    db: Session = Depends(get_db),
):
    """Add a stop to a user journey."""
    # Verify journey exists
    db_journey = crud.get_user_journey(db, journey_id)
    if not db_journey:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User journey not found"
        )

    return crud.create_user_journey_stop(db, journey_id, stop)


@router.get("/{journey_id}/stops", response_model=List[UserJourneyStop])
def get_journey_stops(journey_id: str, db: Session = Depends(get_db)):
    """Get all stops for a user journey, ordered by stop_order."""
    # Verify journey exists
    db_journey = crud.get_user_journey(db, journey_id)
    if not db_journey:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User journey not found"
        )

    return crud.get_user_journey_stops(db, journey_id)


@router.put("/stops/{stop_id}", response_model=UserJourneyStop)
def update_journey_stop(
    stop_id: str, stop_update: UserJourneyStopUpdate, db: Session = Depends(get_db)
):
    """Update a stop in a user journey."""
    db_stop = crud.update_user_journey_stop(db, stop_id, stop_update)
    if not db_stop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Journey stop not found"
        )
    return db_stop


@router.delete("/stops/{stop_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_journey_stop(stop_id: str, db: Session = Depends(get_db)):
    """Delete a stop from a user journey."""
    success = crud.delete_user_journey_stop(db, stop_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Journey stop not found"
        )


@router.delete("/{journey_id}/stops", status_code=status.HTTP_204_NO_CONTENT)
def delete_all_journey_stops(journey_id: str, db: Session = Depends(get_db)):
    """Delete all stops from a user journey."""
    # Verify journey exists
    db_journey = crud.get_user_journey(db, journey_id)
    if not db_journey:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User journey not found"
        )

    crud.delete_all_user_journey_stops(db, journey_id)


@router.get("/{journey_id}/full-route", response_model=FullRouteResponse)
def get_user_journey_full_route(journey_id: str, db: Session = Depends(get_db)):
    """
    Get the complete GPS route for a user journey.
    Returns all route segments and their GPS points in order.
    """
    # Get user journey
    db_journey = crud.get_user_journey(db, journey_id)
    if not db_journey:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User journey not found"
        )

    # Get stops for this journey (ordered by stop_order)
    journey_stops = crud.get_user_journey_stops(db, journey_id)

    if len(journey_stops) < 2:
        return FullRouteResponse(
            total_stops=len(journey_stops),
            total_segments=0,
            total_points=0,
            segments=[],
        )

    # Build segments between consecutive stops
    segments = []
    total_points = 0

    for i in range(len(journey_stops) - 1):
        from_stop = journey_stops[i]
        to_stop = journey_stops[i + 1]

        # Find route segment between these stops
        segment = crud.get_route_segment_by_stops(
            db, str(from_stop.stop_id), str(to_stop.stop_id)
        )

        if segment:
            # Get all GPS points for this segment
            points = crud.get_shape_points_by_shape_id(db, str(segment.shape_id))
            total_points += len(points)

            segments.append(
                {
                    "from_stop_id": from_stop.stop_id,
                    "to_stop_id": to_stop.stop_id,
                    "shape_id": segment.shape_id,
                    "point_count": len(points),
                    "points": [
                        {
                            "lat": p.shape_pt_lat,
                            "lon": p.shape_pt_lon,
                            "sequence": p.shape_pt_sequence,
                            "distance": p.shape_dist_traveled,
                        }
                        for p in points
                    ],
                }
            )
        else:
            # No route segment found between these stops
            segments.append(
                {
                    "from_stop_id": from_stop.stop_id,
                    "to_stop_id": to_stop.stop_id,
                    "shape_id": None,
                    "point_count": 0,
                    "points": [],
                    "note": "No route segment defined between these stops",
                }
            )

    return FullRouteResponse(
        total_stops=len(journey_stops),
        total_segments=len(segments),
        total_points=total_points,
        segments=segments,
    )
