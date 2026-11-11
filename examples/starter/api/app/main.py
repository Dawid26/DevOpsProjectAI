"""IncidentFlow API — the first working part of the DevOps lab."""

from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy import select, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from .db import Base, get_db, get_engine
from .models import Incident  # noqa: F401 — registers model metadata
from .schemas import IncidentCreate, IncidentRead, IncidentStatusUpdate


@asynccontextmanager
async def lifespan(app: FastAPI):
    # W etapie 2 wystarczy; później przejdziemy na migracje Alembic.
    Base.metadata.create_all(bind=get_engine())
    yield


app = FastAPI(title="IncidentFlow API", version="0.1.0", lifespan=lifespan)
DbSession = Annotated[Session, Depends(get_db)]


@app.get("/")
def index():
    return {"app": "IncidentFlow", "docs": "/docs", "version": "0.1.0"}


@app.get("/health")
def health():
    # Liveness: działa proces HTTP. Nie zależy od bazy.
    return {"status": "alive"}


@app.get("/ready")
def readiness():
    # Readiness: aplikacja może obsługiwać żądania wymagające bazy.
    try:
        with get_engine().connect() as conn:
            conn.execute(text("SELECT 1"))
    except (SQLAlchemyError, OSError):
        raise HTTPException(status_code=503, detail="Database unavailable") from None
    return {"status": "ready", "database": "connected"}


@app.post("/incidents", response_model=IncidentRead, status_code=status.HTTP_201_CREATED)
def create_incident(payload: IncidentCreate, db: DbSession):
    incident = Incident(title=payload.title, severity=payload.severity, status="open")
    db.add(incident)
    db.commit()
    db.refresh(incident)
    return incident


@app.get("/incidents", response_model=list[IncidentRead])
def list_incidents(db: DbSession):
    return db.scalars(select(Incident).order_by(Incident.id.desc())).all()


@app.get("/incidents/{incident_id}", response_model=IncidentRead)
def get_incident(incident_id: int, db: DbSession):
    incident = db.get(Incident, incident_id)
    if incident is None:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident


@app.patch("/incidents/{incident_id}", response_model=IncidentRead)
def change_incident_status(incident_id: int, payload: IncidentStatusUpdate, db: DbSession):
    incident = db.get(Incident, incident_id)
    if incident is None:
        raise HTTPException(status_code=404, detail="Incident not found")
    incident.status = payload.status
    db.commit()
    db.refresh(incident)
    return incident
