"""Analytics API - comprehensive analytics endpoints."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database.database import get_db
from backend.models.event import Event
from backend.models.node import Node
from backend.models.network import Network
from backend.models.alert import Alert
from backend.analytics.temporal_analysis import (
    get_hourly_distribution, get_daily_distribution,
    get_zone_timeline, get_event_type_distribution,
    get_activity_trend, get_network_evolution,
)
from backend.analytics.pattern_detection import get_emerging_patterns_summary
from backend.services.network_service import get_full_graph

router = APIRouter(prefix="/analytics", tags=["analytics"])


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
def get_analytics(db: Session = Depends(get_db)):
    """Full analytics dashboard data."""
    events = db.query(Event).all()
    event_dicts = _events_to_dicts(events)
    
    total_events = len(events)
    total_nodes = db.query(Node).count()
    online_nodes = db.query(Node).filter(Node.status == "online").count()
    total_networks = db.query(Network).count()
    active_alerts = db.query(Alert).filter(Alert.status != "resolved").count()
    
    hourly = get_hourly_distribution(event_dicts)
    trend = get_activity_trend(event_dicts)
    patterns = get_emerging_patterns_summary(event_dicts)
    
    return {
        "summary": {
            "total_events": total_events,
            "total_nodes": total_nodes,
            "online_nodes": online_nodes,
            "total_networks": total_networks,
            "active_alerts": active_alerts,
        },
        "hourly_distribution": hourly,
        "activity_trend": trend,
        "emerging_patterns": patterns,
        "timestamp": __import__("datetime").datetime.utcnow().isoformat(),
    }


@router.get("/temporal")
def temporal_analytics(db: Session = Depends(get_db)):
    """Temporal analysis data for timeline page."""
    events = db.query(Event).all()
    event_dicts = _events_to_dicts(events)
    
    return {
        "hourly": get_hourly_distribution(event_dicts),
        "daily": get_daily_distribution(event_dicts),
        "zone_timeline": get_zone_timeline(event_dicts),
        "event_types": get_event_type_distribution(event_dicts),
        "trend": get_activity_trend(event_dicts),
        "network_evolution": get_network_evolution(event_dicts),
    }


@router.get("/patterns")
def pattern_analytics(db: Session = Depends(get_db)):
    """Get all detected emerging patterns."""
    events = db.query(Event).all()
    event_dicts = _events_to_dicts(events)
    return {"patterns": get_emerging_patterns_summary(event_dicts)}


@router.get("/network-graph")
def network_graph_analytics(db: Session = Depends(get_db)):
    """Full network graph for Cytoscape.js visualization."""
    return get_full_graph(db)
