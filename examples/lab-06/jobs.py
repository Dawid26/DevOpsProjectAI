"""RQ task that records one simulated notification per incident and event type."""

from sqlalchemy.dialects.postgresql import insert

from .db import get_engine
from .notification_models import NotificationEvent


def notify_incident(incident_id: int) -> dict:
    statement = (
        insert(NotificationEvent)
        .values(incident_id=incident_id, event_type="incident_notification")
        .on_conflict_do_nothing(index_elements=["incident_id", "event_type"])
        .returning(NotificationEvent.id)
    )
    with get_engine().begin() as connection:
        notification_id = connection.execute(statement).scalar_one_or_none()

    status = "created" if notification_id is not None else "already_exists"
    print(f"incident_id={incident_id} notification={status}", flush=True)
    return {"incident_id": incident_id, "status": status}
