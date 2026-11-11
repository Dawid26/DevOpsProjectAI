"""Input and output validation for REST endpoints."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

Severity = Literal["low", "medium", "high", "critical"]
Status = Literal["open", "investigating", "resolved"]


class IncidentCreate(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    severity: Severity


class IncidentStatusUpdate(BaseModel):
    status: Status


class IncidentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    severity: Severity
    status: Status
    created_at: datetime
