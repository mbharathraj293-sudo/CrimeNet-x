"""Demo mode API - starts/stops synthetic event generation."""
import asyncio
import random
import logging
from datetime import datetime
from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from backend.database.database import get_db, SessionLocal
from backend.schemas.event import EventCreate
from backend.services.event_service import create_event
from backend.websocket.manager import manager
from backend.config import settings

router = APIRouter(prefix="/demo", tags=["demo"])
logger = logging.getLogger("crimenet_x.demo")

# Demo state
demo_state = {"running": False, "task": None, "generated": 0}

DEMO_ZONES = ["Z-01", "Z-02", "Z-03", "Z-04", "Z-05", "Z-06", "Z-07", "Z-08"]
DEMO_NODES = ["N-01", "N-02", "N-03", "N-04", "N-05"]
DEMO_EVENT_TYPES = [
    "Observed Activity", "Location Recurrence", "Temporal Correlation",
    "Network Relationship", "Environmental Observation", "Pattern Observation"
]
ZONE_COORDS = {
    "Z-01": (12.9716, 77.5946), "Z-02": (12.9800, 77.6100),
    "Z-03": (12.9650, 77.5800), "Z-04": (12.9550, 77.6200),
    "Z-05": (12.9900, 77.5700), "Z-06": (12.9450, 77.5900),
    "Z-07": (13.0000, 77.6050), "Z-08": (12.9600, 77.6300),
}
ZONE_NODE_MAP = {
    "Z-01": "N-04", "Z-02": "N-03", "Z-03": "N-01",
    "Z-04": "N-02", "Z-05": "N-02", "Z-06": "N-04",
    "Z-07": "N-05", "Z-08": "N-05",
}


def jitter(val, scale=0.003):
    return round(val + random.uniform(-scale, scale), 6)


async def generate_demo_events():
    """Background task that generates synthetic events and broadcasts them."""
    logger.info("Demo mode started")
    try:
        while demo_state["running"]:
            interval = random.uniform(settings.DEMO_INTERVAL_MIN, settings.DEMO_INTERVAL_MAX)
            await asyncio.sleep(interval)
            
            if not demo_state["running"]:
                break
            
            # Weight zones - Z-03 appears more often to trigger patterns
            zone_weights = [1, 2, 5, 1, 2, 1, 2, 1]
            zone_id = random.choices(DEMO_ZONES, weights=zone_weights)[0]
            base_lat, base_lon = ZONE_COORDS[zone_id]
            node_id = ZONE_NODE_MAP.get(zone_id, random.choice(DEMO_NODES))
            event_type = random.choices(
                DEMO_EVENT_TYPES,
                weights=[5, 3, 3, 2, 2, 2]
            )[0]
            severity = random.choices(["low", "medium", "high"], weights=[6, 3, 1])[0]
            
            db = SessionLocal()
            try:
                data = EventCreate(
                    node_id=node_id,
                    event_type=event_type,
                    zone_id=zone_id,
                    latitude=jitter(base_lat),
                    longitude=jitter(base_lon),
                    severity=severity,
                )
                event = create_event(db, data)
                demo_state["generated"] += 1
                
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
                    },
                    "demo_total": demo_state["generated"],
                }
                await manager.broadcast(msg)
                logger.debug(f"Demo event {event.event_id} generated")
            except Exception as e:
                logger.error(f"Demo generation error: {e}")
            finally:
                db.close()
    except asyncio.CancelledError:
        logger.debug("Demo task cancelled")
    except Exception as e:
        logger.error(f"Demo generator loop error: {e}")
    finally:
        demo_state["running"] = False
        demo_state["task"] = None
        logger.info("Demo mode stopped")


@router.post("/start")
async def start_demo():
    if demo_state["running"]:
        return {"message": "Demo already running", "status": "running",
                "generated": demo_state["generated"]}
    
    demo_state["running"] = True
    demo_state["generated"] = 0
    demo_state["task"] = asyncio.create_task(generate_demo_events())
    
    await manager.broadcast({"type": "demo_started", "message": "Demo mode activated"})
    return {"message": "Demo mode started", "status": "running"}


@router.post("/stop")
async def stop_demo():
    demo_state["running"] = False
    task = demo_state.get("task")
    if task and not task.done():
        task.cancel()
    demo_state["task"] = None
    await manager.broadcast({"type": "demo_stopped", "message": "Demo mode deactivated",
                              "generated": demo_state["generated"]})
    return {"message": "Demo mode stopped", "status": "stopped",
            "generated": demo_state["generated"]}


@router.get("/status")
def demo_status():
    return {
        "running": demo_state["running"],
        "generated": demo_state["generated"],
    }
