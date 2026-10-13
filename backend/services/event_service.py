"""Event service - business logic for event operations."""
import uuid
import logging
from datetime import datetime
from sqlalchemy.orm import Session
from backend.models.event import Event
from backend.schemas.event import EventCreate

logger = logging.getLogger("crimenet_x.event_service")

_event_counter = None


def _get_next_event_id(db: Session) -> str:
    count = db.query(Event).count()
    return f"EVT-{count + 1:04d}"


def create_event(db: Session, data: EventCreate) -> Event:
    event_id = _get_next_event_id(db)
    ts = data.timestamp or datetime.utcnow()
    event = Event(
        event_id=event_id,
        event_type=data.event_type,
        zone_id=data.zone_id,
        node_id=data.node_id,
        latitude=data.latitude,
        longitude=data.longitude,
        timestamp=ts,
        status="processed",
        severity=data.severity or "low",
        metadata_json=data.metadata_json or "{}",
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    logger.info(f"Created event {event_id}")
    return event


def get_events(db: Session, skip: int = 0, limit: int = 100,
               zone_id: str = None, event_type: str = None,
               node_id: str = None) -> list:
    query = db.query(Event)
    if zone_id:
        query = query.filter(Event.zone_id == zone_id)
    if event_type:
        query = query.filter(Event.event_type == event_type)
    if node_id:
        query = query.filter(Event.node_id == node_id)
    return query.order_by(Event.timestamp.desc()).offset(skip).limit(limit).all()


def get_recent_events(db: Session, limit: int = 50) -> list:
    return db.query(Event).order_by(Event.timestamp.desc()).limit(limit).all()


def get_event_count(db: Session) -> int:
    return db.query(Event).count()


def search_events(db: Session, query: str, limit: int = 20) -> list:
    q = f"%{query}%"
    return (
        db.query(Event)
        .filter(
            (Event.event_id.ilike(q)) |
            (Event.event_type.ilike(q)) |
            (Event.zone_id.ilike(q)) |
            (Event.node_id.ilike(q))
        )
        .limit(limit)
        .all()
    )
