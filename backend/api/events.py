"""Events API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.database.database import get_db
from backend.schemas.event import EventCreate, EventResponse
from backend.services.event_service import (
    create_event, get_events, get_recent_events, get_event_count, search_events
)
from backend.websocket.manager import manager
import asyncio

router = APIRouter(prefix="/events", tags=["events"])


@router.post("", response_model=EventResponse)
async def post_event(data: EventCreate, db: Session = Depends(get_db)):
    """Receive a new event from ESP32 field node or demo generator."""
    event = create_event(db, data)
    # Broadcast via WebSocket
    msg = {
        "type": "new_event",
        "event": {
            "event_id": event.event_id,
            "event_type": event.event_type,
            "zone_id": event.zone_id,
            "node_id": event.node_id,
            "latitude": event.latitude,
            "longitude": event.longitude,
            "timestamp": event.timestamp.isoformat(),
            "severity": event.severity,
            "status": event.status,
        }
    }
    await manager.broadcast(msg)
    return event


@router.get("", response_model=List[EventResponse])
def list_events(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=500),
    zone_id: Optional[str] = None,
    event_type: Optional[str] = None,
    node_id: Optional[str] = None,
    db: Session = Depends(get_db),
):
    return get_events(db, skip=skip, limit=limit, zone_id=zone_id,
                      event_type=event_type, node_id=node_id)


@router.get("/recent", response_model=List[EventResponse])
def recent_events(limit: int = Query(50, le=200), db: Session = Depends(get_db)):
    return get_recent_events(db, limit=limit)


@router.get("/count")
def event_count(db: Session = Depends(get_db)):
    return {"count": get_event_count(db)}


@router.get("/search")
def search(q: str = Query(..., min_length=1), db: Session = Depends(get_db)):
    results = search_events(db, q)
    return [
        {"type": "event", "id": e.event_id, "title": e.event_type,
         "subtitle": f"{e.zone_id} | {e.node_id}"}
        for e in results
    ]
