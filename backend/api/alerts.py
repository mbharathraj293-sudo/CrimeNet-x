"""Alerts API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.database.database import get_db
from backend.schemas.alert import AlertResponse, AlertStatusUpdate
from backend.services.alert_service import (
    get_alerts, get_alert, update_alert_status, get_active_alert_count, search_alerts
)
from backend.websocket.manager import manager

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("", response_model=List[AlertResponse])
def list_alerts(
    status: Optional[str] = None,
    severity: Optional[str] = None,
    db: Session = Depends(get_db),
):
    return get_alerts(db, status=status, severity=severity)


@router.get("/count")
def alert_count(db: Session = Depends(get_db)):
    return {"count": get_active_alert_count(db)}


@router.get("/{alert_id}", response_model=AlertResponse)
def get_single_alert(alert_id: str, db: Session = Depends(get_db)):
    alert = get_alert(db, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert


@router.patch("/{alert_id}/status")
async def update_status(alert_id: str, data: AlertStatusUpdate, db: Session = Depends(get_db)):
    allowed_statuses = ["new", "under_review", "resolved"]
    if data.status not in allowed_statuses:
        raise HTTPException(status_code=400, detail=f"Status must be one of: {allowed_statuses}")
    
    alert = update_alert_status(db, alert_id, data.status, data.resolved_by or "Analyst")
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    # Broadcast alert update
    await manager.broadcast({
        "type": "alert_update",
        "alert": {
            "alert_id": alert.alert_id,
            "status": alert.status,
            "severity": alert.severity,
            "title": alert.title,
        }
    })
    return {"message": f"Alert {alert_id} updated to {data.status}", "alert_id": alert_id}


@router.get("/search/q")
def search(q: str = Query(..., min_length=1), db: Session = Depends(get_db)):
    results = search_alerts(db, q)
    return [
        {"type": "alert", "id": a.alert_id, "title": a.title,
         "subtitle": f"{a.zone_id} | {a.severity}"}
        for a in results
    ]
