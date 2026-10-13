"""Node SQLAlchemy model - represents ESP32 field nodes."""
from sqlalchemy import Column, String, Float, DateTime, Integer
from datetime import datetime
from backend.database.database import Base


class Node(Base):
    __tablename__ = "nodes"

    node_id = Column(String(10), primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    zone_id = Column(String(10), nullable=False)
    status = Column(String(20), default="offline")
    battery = Column(Integer, default=100)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    last_seen = Column(DateTime, default=datetime.utcnow)
    firmware_version = Column(String(20), default="v2.1.0")
    signal_strength = Column(Integer, default=-60)
    created_at = Column(DateTime, default=datetime.utcnow)
