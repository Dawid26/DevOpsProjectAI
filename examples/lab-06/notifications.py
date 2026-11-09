"""FastAPI route that validates the incident and queues its notification."""

import os
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from redis import Redis
from redis.backoff import NoBackoff
from redis.exceptions import ConnectionError as RedisConnectionError
from redis.exceptions import TimeoutError as RedisTimeoutError
from redis.retry import Retry as RedisRetry
from rq import Queue, Retry
from sqlalchemy.orm import Session

from .db import get_db
from .jobs import notify_incident
from .models import Incident

router = APIRouter()
DbSession = Annotated[Session, Depends(get_db)]


@router.post("/incidents/{incident_id}/notification", status_code=202)
def enqueue_notification(incident_id: int, db: DbSession):
    if db.get(Incident, incident_id) is None:
        raise HTTPException(status_code=404, detail="Incident not found")

    try:
        with Redis.from_url(
            os.getenv("REDIS_URL", "redis://redis:6379/0"),
            socket_connect_timeout=1,
            socket_timeout=1,
            retry=RedisRetry(NoBackoff(), 0),
        ) as connection:
            queue = Queue("notifications", connection=connection)
            job = queue.enqueue(
                notify_incident,
                incident_id,
                retry=Retry(max=2, interval=[5, 10]),
            )
    except (RedisConnectionError, RedisTimeoutError):
        raise HTTPException(
            status_code=503, detail="Notification queue unavailable"
        ) from None

    return {"job_id": job.id, "incident_id": incident_id}
