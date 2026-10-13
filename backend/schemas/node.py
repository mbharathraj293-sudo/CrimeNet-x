"""Node Pydantic schemas."""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class NodeResponse(BaseModel):
    node_id: str
    name: str
    zone_id: str
    status: str
    battery: int
    latitude: float
    longitude: float
    last_seen: Optional[datetime]
    firmware_version: str
    signal_strength: int

    class Config:
        from_attributes = True


class NodeStatusUpdate(BaseModel):
    status: str
    battery: Optional[int] = None
    signal_strength: Optional[int] = None
