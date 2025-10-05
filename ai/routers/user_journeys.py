from datetime import date, datetime, timedelta
from hashlib import md5
from typing import List

import crud
import googlemaps
from config import settings
from database import get_db
from db_models import UserJourney as UserJourneyDB
from dependencies import get_current_user
from enums import UserRole
from fastapi import APIRouter, Depends, HTTPException, status
from models import (
    FullRouteResponse,
    RouteProposal,
    RouteProposalRequest,
    RouteProposalsResponse,
    StepInfo,
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
    journey: UserJourneyCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Create a new user journey for the authenticated user.
    Journey is automatically assigned to the authenticated user.

    Triggers:
    - If user is disabled and journey is scheduled for tomorrow, notifies DISPATCHER
    - Sets notification_time to 30 minutes before journey start
    """
    # Create journey first
    db_journey = crud.create_user_journey(db, journey, str(current_user.id))

    # Set notification_time automatically if planned_date is provided
    if journey.planned_date:
        reminder_time = journey.planned_date - timedelta(minutes=30)
        if reminder_time > datetime.now():
            # Update notification_time directly in database
            db_journey_model = (
                db.query(UserJourneyDB)
                .filter(UserJourneyDB.id == str(db_journey.id))
                .first()
            )
            if db_journey_model:
                db_journey_model.notification_time = reminder_time
                db.commit()
                db.refresh(db_journey_model)
                # Update returned model
                db_journey.notification_time = reminder_time

    # Trigger 1: Notify DISPATCHER if disabled person schedules journey for next day
    # This is returned as part of response, not stored in database
    if bool(current_user.is_disabled) and journey.planned_date:
        tomorrow = date.today() + timedelta(days=1)
        if journey.planned_date.date() == tomorrow:
            # TODO: In production, send actual notification to dispatchers
            # For now, this would be handled by a separate notification service
            print(
                f"[NOTIFICATION] User {current_user.name} (disabled) scheduled journey for tomorrow"
            )

    return db_journey


@router.get("/my", response_model=List[UserJourney])
def get_my_journeys(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Get all journeys for the authenticated user."""
    return crud.get_user_journeys(db, str(current_user.id), skip=skip, limit=limit)


@router.get("/my/saved", response_model=List[UserJourney])
def get_my_saved_journeys(
    db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    """Get saved (not active) journeys for the authenticated user (max 10)."""
    return crud.get_user_saved_journeys(db, str(current_user.id))


@router.get("/my/active", response_model=UserJourney | None)
def get_my_active_journey(
    db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    """Get the active journey for the authenticated user."""
    return crud.get_user_active_journey(db, str(current_user.id))


@router.get("/{journey_id}", response_model=UserJourney)
def get_user_journey(
    journey_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Get a specific user journey by ID.
    User can only view their own journeys.
    """
    db_journey = crud.get_user_journey(db, journey_id)
    if not db_journey:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User journey not found"
        )

    if str(db_journey.user_id) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own journeys",
        )

    return db_journey


@router.put("/{journey_id}", response_model=UserJourney)
def update_user_journey(
    journey_id: str,
    journey: UserJourneyUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Update a user journey.
    User can only update their own journeys.
    """
    db_journey = crud.get_user_journey(db, journey_id)
    if not db_journey:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User journey not found"
        )

    if str(db_journey.user_id) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own journeys",
        )

    db_journey = crud.update_user_journey(db, journey_id, journey)
    return db_journey


@router.delete("/{journey_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_journey(
    journey_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Delete a user journey.
    User can only delete their own journeys.
    """
    db_journey = crud.get_user_journey(db, journey_id)
    if not db_journey:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User journey not found"
        )

    if str(db_journey.user_id) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own journeys",
        )

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
def create_user_journey_stop(
    journey_id: str,
    stop: UserJourneyStopCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Add a stop to a user journey.
    User can only add stops to their own journeys.
    """
    db_journey = crud.get_user_journey(db, journey_id)
    if not db_journey:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User journey not found"
        )

    if str(db_journey.user_id) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only add stops to your own journeys",
        )

    return crud.create_user_journey_stop(db, journey_id, stop)


@router.get("/{journey_id}/stops", response_model=List[UserJourneyStop])
def get_user_journey_stops(
    journey_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Get all stops for a user journey.
    User can only view stops for their own journeys.
    """
    db_journey = crud.get_user_journey(db, journey_id)
    if not db_journey:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User journey not found"
        )

    if str(db_journey.user_id) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view stops for your own journeys",
        )

    return crud.get_user_journey_stops(db, journey_id)


@router.put("/stops/{stop_id}", response_model=UserJourneyStop)
def update_user_journey_stop(
    stop_id: str,
    stop: UserJourneyStopUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Update a user journey stop.
    User can only update stops in their own journeys.
    """
    db_stop = crud.get_user_journey_stop(db, stop_id)
    if not db_stop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User journey stop not found"
        )

    db_journey = crud.get_user_journey(db, str(db_stop.user_journey_id))
    if db_journey and str(db_journey.user_id) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update stops in your own journeys",
        )

    db_stop = crud.update_user_journey_stop(db, stop_id, stop)
    return db_stop


@router.delete("/stops/{stop_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_journey_stop(
    stop_id: str, db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    """
    Delete a user journey stop.
    User can only delete stops from their own journeys.
    """
    db_stop = crud.get_user_journey_stop(db, stop_id)
    if not db_stop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User journey stop not found"
        )

    db_journey = crud.get_user_journey(db, str(db_stop.user_journey_id))
    if db_journey and str(db_journey.user_id) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete stops from your own journeys",
        )

    success = crud.delete_user_journey_stop(db, stop_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User journey stop not found"
        )


@router.delete("/{journey_id}/stops", status_code=status.HTTP_204_NO_CONTENT)
def delete_all_stops_from_journey(
    journey_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Delete all stops from a user journey.
    User can only delete stops from their own journeys.
    """
    db_journey = crud.get_user_journey(db, journey_id)
    if not db_journey:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User journey not found"
        )

    if str(db_journey.user_id) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete stops from your own journeys",
        )

    crud.delete_all_user_journey_stops(db, journey_id)


@router.get("/{journey_id}/full-route", response_model=FullRouteResponse)
def get_user_journey_full_route(
    journey_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Get the complete GPS route for a user journey.
    Returns all route segments and their GPS points in order.
    User can only view routes for their own journeys.
    """
    db_journey = crud.get_user_journey(db, journey_id)
    if not db_journey:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User journey not found"
        )

    if str(db_journey.user_id) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view routes for your own journeys",
        )

    journey_stops = crud.get_user_journey_stops(db, journey_id)

    if len(journey_stops) < 2:
        return FullRouteResponse(
            total_stops=len(journey_stops),
            total_segments=0,
            total_points=0,
            segments=[],
        )

    segments = []
    total_points = 0

    for i in range(len(journey_stops) - 1):
        from_stop = journey_stops[i]
        to_stop = journey_stops[i + 1]

        segment = crud.get_route_segment_by_stops(
            db, str(from_stop.stop_id), str(to_stop.stop_id)
        )

        if segment:
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


@router.post("/proposals", response_model=RouteProposalsResponse)
def get_route_proposals(
    request: RouteProposalRequest,
    current_user=Depends(get_current_user),
):
    """
    Get route proposals from Google Maps API.

    This endpoint queries Google Maps Directions API with different parameters
    to find the best public transit routes between two points.

    Args:
        request: Contains start_point, destination, api_key, and departure_datetime

    Returns:
        RouteProposalsResponse with list of route proposals
    """
    # Google Maps type mapping to GTFS
    GOOGLE_TO_GTFS = {
        "BUS": (3, "bus"),
        "TRAM": (0, "tram"),
        "LIGHT_RAIL": (0, "tram"),
        "HEAVY_RAIL": (2, "train"),
        "COMMUTER_TRAIN": (2, "train"),
        "SUBWAY": (2, "train"),
        "RAIL": (2, "train"),
    }

    # Use API key from request or fall back to environment variable
    api_key = request.api_key or settings.GOOGLE_MAPS_API_KEY

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google Maps API key not provided. Set GOOGLE_MAPS_API_KEY environment variable or pass api_key in request.",
        )

    try:
        gmaps = googlemaps.Client(key=api_key)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid Google Maps API key: {str(e)}",
        )

    # Generate different query variants
    variants = []
    for mins in [0, 5, 10]:
        for pref in [None, "less_walking", "fewer_transfers"]:
            params = {
                "origin": request.start_point,
                "destination": request.destination,
                "mode": "transit",
                "transit_mode": ["bus"],
                "departure_time": request.departure_datetime + timedelta(minutes=mins),
            }
            if pref:
                params["transit_routing_preference"] = pref
            variants.append(params)

    proposals = []
    seen = set()

    for p in variants:
        try:
            routes = gmaps.directions(**p)
        except Exception as e:
            # Skip failed requests
            continue

        if not routes:
            continue

        r = routes[0]  # Take the best route for this variant
        leg = r["legs"][0]

        # Create fingerprint for deduplication (line/headsign + first departure)
        transit_fingerprint = []
        for step in leg["steps"]:
            if step["travel_mode"] == "TRANSIT":
                line = step["transit_details"]["line"].get("short_name") or step[
                    "transit_details"
                ]["line"].get("name")
                headsign = step["transit_details"].get("headsign")
                depart = step["transit_details"]["departure_time"]["value"]
                transit_fingerprint.append(f"{line}|{headsign}|{depart}")

        key = md5("|".join(transit_fingerprint).encode()).hexdigest()
        if key in seen:
            continue
        seen.add(key)

        # Extract step information
        steps_info = []
        for step in leg["steps"]:
            gtfs_route_type, gtfs_mode = (None, "walk")
            if step["travel_mode"] == "TRANSIT":
                vehicle_type = step["transit_details"]["line"]["vehicle"]["type"]
                gtfs_route_type, gtfs_mode = GOOGLE_TO_GTFS.get(
                    vehicle_type, (None, "unknown")
                )

            steps_info.append(
                StepInfo(
                    start_lat=step["start_location"]["lat"],
                    start_lng=step["start_location"]["lng"],
                    end_lat=step["end_location"]["lat"],
                    end_lng=step["end_location"]["lng"],
                    gtfs_route_type=gtfs_route_type,
                    gtfs_mode=gtfs_mode,
                )
            )

        proposals.append(
            RouteProposal(
                summary=r.get("summary"),
                departure_time=(
                    leg["departure_time"]["text"] if "departure_time" in leg else None
                ),
                arrival_time=(
                    leg["arrival_time"]["text"] if "arrival_time" in leg else None
                ),
                duration=leg["duration"]["text"],
                steps_info=steps_info,
            )
        )

    return RouteProposalsResponse(proposals=proposals, total_proposals=len(proposals))
