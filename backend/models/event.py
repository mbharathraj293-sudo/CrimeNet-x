"""Event SQLAlchemy model."""
from sqlalchemy import Column, String, Float, DateTime, Text
from datetime import datetime
from backend.database.database import Base


class Event(Base):
    __tablename__ = "events"

    event_id = Column(String(20), primary_key=True, index=True)
    event_type = Column(String(100), nullable=False)
    zone_id = Column(String(10), nullable=False, index=True)
    node_id = Column(String(10), nullable=False, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String(20), default="processed")
    severity = Column(String(10), default="low")
    metadata_json = Column(Text, default="{}")
