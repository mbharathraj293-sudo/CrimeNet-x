"""Entity SQLAlchemy model - represents synthetic analytical entities."""
from sqlalchemy import Column, String, DateTime
from datetime import datetime
from backend.database.database import Base


class Entity(Base):
    __tablename__ = "entities"

    entity_id = Column(String(20), primary_key=True, index=True)
    label = Column(String(100), nullable=False)
    type = Column(String(50), default="Subject")
    created_at = Column(DateTime, default=datetime.utcnow)
