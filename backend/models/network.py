"""Network SQLAlchemy models."""
from sqlalchemy import Column, String, Float, DateTime, Integer, ForeignKey
from datetime import datetime
from backend.database.database import Base


class Network(Base):
    __tablename__ = "networks"

    network_id = Column(String(20), primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    score = Column(Integer, default=0)
    node_count = Column(Integer, default=0)
    edge_count = Column(Integer, default=0)
    components = Column(Integer, default=1)
    degree_centrality = Column(Float, default=0.0)
    betweenness = Column(Float, default=0.0)
    connection_strength = Column(Integer, default=0)
    time_correlation = Column(Integer, default=0)
    location_overlap = Column(Integer, default=0)
    event_recurrence = Column(Integer, default=0)
    centrality_score = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)


class NetworkEntity(Base):
    __tablename__ = "network_entities"

    id = Column(Integer, primary_key=True, autoincrement=True)
    network_id = Column(String(20), ForeignKey("networks.network_id"), index=True)
    entity_id = Column(String(20), ForeignKey("entities.entity_id"), index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
