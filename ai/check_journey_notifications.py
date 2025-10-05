"""
Job script to check for journey notifications.
Run this script every minute with a task scheduler (cron/Windows Task Scheduler).

Usage:
    python check_journey_notifications.py
"""

from datetime import datetime
from uuid import UUID

from database import SessionLocal
from db_models import UserJourney
from enums import NotificationType
from models import SystemNotification


def check_and_send_journey_reminders():
    """
    Check for UserJourneys with notification_time <= now and send reminders.
    After sending, clears the notification_time field.
    """
    db = SessionLocal()
    try:
        now = datetime.now()

        # Get all user journeys with pending notifications
        all_journeys = (
            db.query(UserJourney)
            .filter(UserJourney.notification_time.isnot(None))
            .all()
        )

        pending_notifications = []

        for journey in all_journeys:
            # Check if notification_time is set and in the past
            if journey.notification_time and journey.notification_time <= now:  # type: ignore
                # Create notification
                notification = SystemNotification(
                    notification_type=NotificationType.JOURNEY_REMINDER,
                    message=f"Your journey {journey.name} starts in 30 minutes!",
                    related_journey_id=UUID(str(journey.id)),  # type: ignore
                    created_at=now,
                )
                pending_notifications.append(
                    {
                        "user_id": str(journey.user_id),
                        "journey_id": str(journey.id),
                        "notification": notification,
                    }
                )

                # Clear notification_time (set to None)
                setattr(journey, "notification_time", None)

        if pending_notifications:
            db.commit()
            print(
                f"[{now}] Found {len(pending_notifications)} pending notification(s)"
            )  # noqa: E501

            for item in pending_notifications:
                print(f"  - Sending notification to user {item['user_id']}")
                print(f"    Journey: {item['journey_id']}")
                print(f"    Message: {item['notification'].message}")
                print(f"  ✅ Notification sent")

            print(f"[{now}] Done!")
        else:
            print(f"[{now}] No pending notifications")

    except Exception as e:
        print(f"[{datetime.now()}] Error: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    check_and_send_journey_reminders()
