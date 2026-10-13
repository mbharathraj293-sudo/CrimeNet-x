"""Alert service - business logic for alert lifecycle management."""
import logging
from datetime import datetime
from sqlalchemy.orm import Session
from backend.models.alert import Alert

logger = logging.getLogger("crimenet_x.alert_service")


def get_alerts(db: Session, status: str = None, severity: str = None) -> list:
    query = db.query(Alert)
    if status:
        query = query.filter(Alert.status == status)
    if severity:
        query = query.filter(Alert.severity == severity)
    return query.order_by(Alert.created_at.desc()).all()


def get_alert(db: Session, alert_id: str) -> Alert:
    return db.query(Alert).filter(Alert.alert_id == alert_id).first()


def update_alert_status(db: Session, alert_id: str, status: str, resolved_by: str = "Analyst") -> Alert:
    alert = get_alert(db, alert_id)
    if not alert:
        return None
    alert.status = status
    if status == "resolved":
        alert.resolved_at = datetime.utcnow()
        alert.resolved_by = resolved_by
    db.commit()
    db.refresh(alert)
    logger.info(f"Alert {alert_id} updated to {status}")
    return alert


def create_alert_from_pattern(db: Session, pattern: dict, auto_id_prefix: str = "ALT") -> Alert:
    """Create an alert from a detected pattern."""
    count = db.query(Alert).count()
    alert_id = f"{auto_id_prefix}-{count + 100:04d}"
    alert = Alert(
        alert_id=alert_id,
        severity=pattern.get("severity", "medium"),
        title=f"{pattern['pattern_type']} Detected",
        description=pattern.get("description", "Emerging pattern detected. Human review recommended."),
        zone_id=pattern.get("zone_id", "Z-01"),
        status="new",
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert


def get_active_alert_count(db: Session) -> int:
    return db.query(Alert).filter(Alert.status != "resolved").count()


def search_alerts(db: Session, query: str, limit: int = 20) -> list:
    q = f"%{query}%"
    return (
        db.query(Alert)
        .filter(
            (Alert.alert_id.ilike(q)) |
            (Alert.title.ilike(q)) |
            (Alert.zone_id.ilike(q))
        )
        .limit(limit)
        .all()
    )
