"""Persistent record of the notification simulated in LAB 06."""

from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from .db import Base
from .models import Incident


class NotificationEvent(Base):
    __tablename__ = "notification_events"
    __table_args__ = (
        UniqueConstraint("incident_id", "event_type", name="uq_notification_event"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    incident_id: Mapped[int] = mapped_column(ForeignKey(Incident.id), nullable=False)
    event_type: Mapped[str] = mapped_column(String(40), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
