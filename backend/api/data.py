"""Data management API - CSV upload and dataset management."""
import io
import csv
import logging
import random
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from backend.database.database import get_db
from backend.models.event import Event
from backend.services.event_service import get_event_count

router = APIRouter(prefix="/data", tags=["data"])
logger = logging.getLogger("crimenet_x.data")

VALID_EVENT_TYPES = [
    "Observed Activity", "Location Recurrence", "Temporal Correlation",
    "Network Relationship", "Environmental Observation", "Pattern Observation"
]


@router.post("/upload")
async def upload_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Upload a CSV file with synthetic event data."""
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are accepted.")
    
    contents = await file.read()
    text = contents.decode("utf-8")
    reader = csv.DictReader(io.StringIO(text))
    
    required_cols = {"event_type", "zone_id", "node_id", "latitude", "longitude"}
    rows = list(reader)
    
    if not rows:
        raise HTTPException(status_code=400, detail="CSV file is empty.")
    
    headers = set(reader.fieldnames or [])
    missing = required_cols - headers
    if missing:
        raise HTTPException(status_code=400, detail=f"Missing columns: {missing}")
    
    imported = 0
    errors = []
    base_count = get_event_count(db)
    
    for i, row in enumerate(rows[:500]):  # Cap at 500 rows
        try:
            lat = float(row["latitude"])
            lon = float(row["longitude"])
            if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
                errors.append(f"Row {i+1}: Invalid coordinates")
                continue
            
            event_type = row["event_type"].strip()
            if event_type not in VALID_EVENT_TYPES:
                event_type = "Observed Activity"
            
            ts_str = row.get("timestamp", "")
            try:
                ts = datetime.fromisoformat(ts_str)
            except (ValueError, TypeError):
                ts = datetime.utcnow()
            
            event = Event(
                event_id=f"EVT-{base_count + imported + 1:04d}",
                event_type=event_type,
                zone_id=row.get("zone_id", "Z-01"),
                node_id=row.get("node_id", "N-01"),
                latitude=round(lat, 6),
                longitude=round(lon, 6),
                timestamp=ts,
                status="processed",
                severity=row.get("severity", "low"),
                metadata_json="{}",
            )
            db.add(event)
            imported += 1
        except Exception as e:
            errors.append(f"Row {i+1}: {str(e)}")
    
    db.commit()
    return {
        "message": f"Imported {imported} events",
        "imported": imported,
        "errors": errors[:10],
        "total_events": get_event_count(db),
    }


@router.get("/stats")
def data_stats(db: Session = Depends(get_db)):
    """Get database statistics."""
    from backend.models.node import Node
    from backend.models.network import Network
    from backend.models.alert import Alert
    
    events = db.query(Event).all()
    zones = set(e.zone_id for e in events)
    nodes_used = set(e.node_id for e in events)
    event_types = set(e.event_type for e in events)
    
    return {
        "total_events": len(events),
        "unique_zones": len(zones),
        "zones": sorted(zones),
        "unique_nodes": len(nodes_used),
        "event_types": sorted(event_types),
        "total_nodes": db.query(Node).count(),
        "total_networks": db.query(Network).count(),
        "total_alerts": db.query(Alert).count(),
    }


@router.delete("/reset")
def reset_events(db: Session = Depends(get_db)):
    """Reset events table (for demo purposes only)."""
    count = db.query(Event).count()
    db.query(Event).delete()
    db.commit()
    return {"message": f"Deleted {count} events"}
