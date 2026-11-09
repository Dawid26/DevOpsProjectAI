"""Controlled first-attempt failure for a local LAB 06 exercise."""

from rq import get_current_job

from .jobs import notify_incident


def fail_once_then_notify(incident_id: int) -> dict:
    job = get_current_job()
    if job is None:
        raise RuntimeError("Run this function as an RQ job")

    first_attempt = job.connection.set(
        f"lab06:fail-once:{job.id}", "1", nx=True, ex=3600
    )
    if first_attempt:
        raise RuntimeError("LAB 06 controlled first-attempt failure")

    return notify_incident(incident_id)
