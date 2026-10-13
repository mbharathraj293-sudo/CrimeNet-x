"""Event Pydantic schemas."""
from pydantic import BaseModel, field_validator, model_validator
from typing import Optional
from datetime import datetime


class EventCreate(BaseModel):
    node_id: str
    event_type: str
    zone_id: str
    latitude: float
    longitude: float
    timestamp: Optional[datetime] = None
    severity: Optional[str] = "low"
    metadata_json: Optional[str] = "{}"

    @model_validator(mode="before")
    @classmethod
    def handle_lat_lon_alias(cls, data):
        if isinstance(data, dict):
            if "lat" in data and "latitude" not in data:
                data["latitude"] = data["lat"]
            if "lon" in data and "longitude" not in data:
                data["longitude"] = data["lon"]
        return data

    @field_validator("latitude")
    @classmethod
    def validate_lat(cls, v):
        if not -90 <= v <= 90:
            raise ValueError("Latitude must be between -90 and 90")
        return round(v, 6)

    @field_validator("longitude")
    @classmethod
    def validate_lon(cls, v):
        if not -180 <= v <= 180:
            raise ValueError("Longitude must be between -180 and 180")
        return round(v, 6)

    @field_validator("event_type")
    @classmethod
    def validate_event_type(cls, v):
        allowed = [
            "Observed Activity", "Location Recurrence", "Temporal Correlation",
            "Network Relationship", "Environmental Observation", "Pattern Observation"
        ]
        if v not in allowed:
            raise ValueError(f"Event type must be one of: {allowed}")
        return v

    @field_validator("zone_id")
    @classmethod
    def validate_zone(cls, v):
        if not v.startswith("Z-"):
            raise ValueError("Zone ID must start with 'Z-'")
        return v


class EventResponse(BaseModel):
    event_id: str
    event_type: str
    zone_id: str
    node_id: str
    latitude: float
    longitude: float
    timestamp: datetime
    created_at: datetime
    status: str
    severity: str

    class Config:
        from_attributes = True
