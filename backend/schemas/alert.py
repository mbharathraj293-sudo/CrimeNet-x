"""Alert Pydantic schemas."""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class AlertResponse(BaseModel):
    alert_id: str
    severity: str
    title: str
    description: str
    zone_id: str
    status: str
    created_at: datetime
    resolved_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AlertStatusUpdate(BaseModel):
    status: str
    resolved_by: Optional[str] = "Analyst"
