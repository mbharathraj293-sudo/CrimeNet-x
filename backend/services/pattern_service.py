"""Pattern service - orchestrates pattern detection and alert creation."""
import logging
from sqlalchemy.orm import Session
from backend.models.event import Event
from backend.analytics.pattern_detection import get_emerging_patterns_summary
from backend.services.alert_service import create_alert_from_pattern, get_alerts

logger = logging.getLogger("crimenet_x.pattern_service")


def run_pattern_detection(db: Session) -> list:
    """Run full pattern detection pipeline and create alerts for new patterns."""
    events = db.query(Event).all()
    event_dicts = [
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
    
    patterns = get_emerging_patterns_summary(event_dicts)
    
    # Get existing alert titles to avoid duplicates
    existing_alerts = get_alerts(db)
    existing_titles = {a.title for a in existing_alerts}
    
    new_alerts = []
    for pattern in patterns:
        title = f"{pattern['pattern_type']} Detected"
        if title not in existing_titles and pattern.get("severity") in ("high", "medium"):
            alert = create_alert_from_pattern(db, pattern)
            new_alerts.append(alert)
            existing_titles.add(title)
    
    return patterns
