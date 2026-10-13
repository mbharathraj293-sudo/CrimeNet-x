"""Alert SQLAlchemy model."""
from sqlalchemy import Column, String, DateTime, Text
from datetime import datetime
from backend.database.database import Base


class Alert(Base):
    __tablename__ = "alerts"

    alert_id = Column(String(20), primary_key=True, index=True)
    severity = Column(String(10), default="medium")
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    zone_id = Column(String(10), nullable=False)
    status = Column(String(20), default="new")
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)
    resolved_by = Column(String(50), nullable=True)
