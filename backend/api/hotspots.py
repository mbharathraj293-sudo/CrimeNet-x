"""Hotspots API endpoint."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database.database import get_db
from backend.models.event import Event
from backend.analytics.geo_analysis import calculate_hotspots, get_map_markers

router = APIRouter(prefix="/hotspots", tags=["hotspots"])


def _events_to_dicts(events):
    return [
        {
            "event_id": e.event_id,
            "event_type": e.event_type,
            "zone_id": e.zone_id,
            "node_id": e.node_id,
            "latitude": e.latitude,
            "longitude": e.longitude,
            "timestamp": e.timestamp,
            "severity": e.severity,
        }
        for e in events
    ]


@router.get("")
def get_hotspots(db: Session = Depends(get_db)):
    """Get activity hotspots from synthetic data."""
    events = db.query(Event).all()
    event_dicts = _events_to_dicts(events)
    hotspots = calculate_hotspots(event_dicts)
    markers = get_map_markers(event_dicts)
    return {
        "hotspots": hotspots,
        "markers": markers,
        "total_events": len(events),
    }
