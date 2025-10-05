"""
Automatic delay monitoring system.

This script runs periodically (every 1-3 minutes) to:
1. Check all active vehicle trips
2. Calculate current delay predictions
3. Store predictions in database
4. Send notifications when delays exceed thresholds

Usage:
    python monitor_delays.py

To run as scheduled job (Windows):
    schtasks /create /tn "DelayMonitor" /tr "python monitor_delays.py" /sc minute /mo 3

To run as scheduled job (Linux/Mac):
    */3 * * * * cd /path/to/project && python monitor_delays.py

TODO: REPLACE WITH TIME SERIES MODEL
====================================
Current approach uses rule-based algorithm.
Future: LSTM/Prophet model for better predictions.
"""

import sys
from datetime import datetime, timedelta
from pathlib import Path

from sqlalchemy import and_

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

# These imports need to be after sys.path modification
if True:  # noqa: SIM102
    from crud import delay_prediction
    from database import SessionLocal
    from db_models import User, UserJourney, VehicleTrip
    from enums import NotificationType
    from models import SystemNotification


def get_active_vehicle_trips(db):
    """
    Get all currently active vehicle trips.

    A trip is active if:
    - Status is IN_PROGRESS
    - OR scheduled to depart within last 2 hours and not completed
    """
    now = datetime.now()
    time_window_start = now - timedelta(hours=2)
    time_window_end = now + timedelta(hours=1)

    active_trips = (
        db.query(VehicleTrip)
        .filter(
            and_(
                VehicleTrip.scheduled_departure >= time_window_start,
                VehicleTrip.scheduled_departure <= time_window_end,
            )
        )
        .all()
    )

    return active_trips


def get_latest_gps_position(db, vehicle_trip_id: str):
    """Get the latest GPS position for a vehicle trip."""
    from db_models import JourneyData

    latest_gps = (
        db.query(JourneyData)
        .filter(JourneyData.vehicle_trip_id == vehicle_trip_id)
        .order_by(JourneyData.timestamp.desc())
        .first()
    )

    if latest_gps and latest_gps.latitude and latest_gps.longitude:
        return float(latest_gps.latitude), float(latest_gps.longitude)  # type: ignore

    return None, None


def get_users_on_trip(db, vehicle_trip_id: str):
    """
    Get all users currently on this vehicle trip.

    Based on:
    - Active UserJourney with journey data for this trip
    - OR users with tickets valid for this trip
    """
    from db_models import JourneyData

    # Find users who have sent GPS data for this trip recently (last 10 minutes)
    recent_time = datetime.now() - timedelta(minutes=10)

    users_with_gps = (
        db.query(User)
        .join(JourneyData, JourneyData.user_id == User.id)
        .filter(
            and_(
                JourneyData.vehicle_trip_id == vehicle_trip_id,
                JourneyData.timestamp >= recent_time,
            )
        )
        .distinct()
        .all()
    )

    # Also find users with active UserJourney for this route
    trip = db.query(VehicleTrip).filter(VehicleTrip.id == vehicle_trip_id).first()
    if not trip:
        return users_with_gps

    users_with_journey = (
        db.query(User)
        .join(UserJourney, UserJourney.user_id == User.id)
        .filter(
            and_(
                UserJourney.is_in_progress.is_(True),  # type: ignore
                UserJourney.planned_date >= datetime.now() - timedelta(hours=2),
            )
        )
        .distinct()
        .all()
    )

    # Combine and deduplicate
    all_users = {str(u.id): u for u in users_with_gps + users_with_journey}
    return list(all_users.values())


def send_delay_notification(
    user: User,
    vehicle_trip_id: str,
    predicted_delay: float,
    confidence: float,
):
    """
    Send delay notification to user.

    This is a system notification (not stored in database).
    In production, this would trigger:
    - Push notification
    - SMS (optional)
    - Email (optional)
    """
    message = (
        f"⚠️ Delay alert: Your vehicle is predicted to be {predicted_delay:.0f} minutes late. "
        f"Confidence: {confidence*100:.0f}%"
    )

    notification = SystemNotification(
        notification_type=NotificationType.DELAY_DETECTED,
        message=message,
        related_journey_id=None,
        related_report_id=None,
    )

    # Print to console (in production, send via push notification service)
    print(f"[NOTIFICATION] To {user.name}: {message}")

    return notification


def process_vehicle_trip(db, trip: VehicleTrip):
    """
    Process a single vehicle trip:
    1. Get latest GPS position
    2. Calculate delay prediction
    3. Check if notification needed
    4. Send notifications to users
    """
    trip_id = str(trip.id)

    # Get latest GPS position
    lat, lon = get_latest_gps_position(db, trip_id)

    # Calculate prediction
    prediction = delay_prediction.predict_delay(db, trip_id, lat, lon)

    if "error" in prediction:
        return None

    predicted_delay = prediction["predicted_delay_minutes"]
    confidence = prediction["confidence"]

    # Store prediction (optional - for historical analysis)
    # TODO: Create DelayPrediction table to store these

    # Check if notification needed (delay > 5 minutes and confidence > 0.6)
    users = []
    if predicted_delay > 5.0 and confidence > 0.6:
        # Get users on this trip
        users = get_users_on_trip(db, trip_id)

        # Send notifications
        for user in users:
            send_delay_notification(user, trip_id, predicted_delay, confidence)

    return {
        "vehicle_trip_id": trip_id,
        "predicted_delay": predicted_delay,
        "confidence": confidence,
        "notified_users": len(users),
    }


def monitor_delays():
    """
    Main monitoring function.

    Called every 1-3 minutes by scheduler.
    """
    print("=" * 60)
    print(f"DELAY MONITORING - {datetime.now().isoformat()}")
    print("=" * 60)

    db = SessionLocal()

    try:
        # Get all active trips
        active_trips = get_active_vehicle_trips(db)

        print(f"\nFound {len(active_trips)} active vehicle trips")

        if not active_trips:
            print("No active trips to monitor")
            return

        # Process each trip
        results = []
        for trip in active_trips:
            try:
                result = process_vehicle_trip(db, trip)
                if result:
                    results.append(result)
            except Exception as e:
                print(f"Error processing trip {trip.id}: {e}")
                continue

        # Summary
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        print(f"Trips processed: {len(results)}")

        delays = [r for r in results if r["predicted_delay"] > 5.0]
        print(f"Trips with delays (>5 min): {len(delays)}")

        total_notified = sum(r["notified_users"] for r in results)
        print(f"Users notified: {total_notified}")

        if delays:
            print("\nDelayed trips:")
            for r in delays:
                print(
                    f"  - Trip {r['vehicle_trip_id'][:8]}...: "
                    f"+{r['predicted_delay']:.1f} min "
                    f"(confidence: {r['confidence']:.0%})"
                )

        print("=" * 60)

    except Exception as e:
        print(f"ERROR in delay monitoring: {e}")
        import traceback

        traceback.print_exc()

    finally:
        db.close()


def main():
    """Entry point for the delay monitoring system."""
    try:
        monitor_delays()
    except KeyboardInterrupt:
        print("\n\nMonitoring stopped by user")
    except Exception as e:
        print(f"\n\nFATAL ERROR: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
