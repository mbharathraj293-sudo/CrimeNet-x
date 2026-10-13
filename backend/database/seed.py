"""
Database seeder - generates realistic synthetic demo data for CRIMENET-X.
All data is completely synthetic and for academic demonstration only.
"""
import random
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from backend.database.database import SessionLocal, engine
from backend.models.event import Event
from backend.models.node import Node
from backend.models.entity import Entity
from backend.models.network import Network, NetworkEntity
from backend.models.alert import Alert

# Synthetic zones with coordinates centered around a generic location
ZONES = {
    "Z-01": {"name": "Zone Alpha",   "lat": 12.9716, "lon": 77.5946, "base_lat": 12.9716, "base_lon": 77.5946},
    "Z-02": {"name": "Zone Beta",    "lat": 12.9800, "lon": 77.6100, "base_lat": 12.9800, "base_lon": 77.6100},
    "Z-03": {"name": "Zone Gamma",   "lat": 12.9650, "lon": 77.5800, "base_lat": 12.9650, "base_lon": 77.5800},
    "Z-04": {"name": "Zone Delta",   "lat": 12.9550, "lon": 77.6200, "base_lat": 12.9550, "base_lon": 77.6200},
    "Z-05": {"name": "Zone Epsilon", "lat": 12.9900, "lon": 77.5700, "base_lat": 12.9900, "base_lon": 77.5700},
    "Z-06": {"name": "Zone Zeta",    "lat": 12.9450, "lon": 77.5900, "base_lat": 12.9450, "base_lon": 77.5900},
    "Z-07": {"name": "Zone Eta",     "lat": 13.0000, "lon": 77.6050, "base_lat": 13.0000, "base_lon": 77.6050},
    "Z-08": {"name": "Zone Theta",   "lat": 12.9600, "lon": 77.6300, "base_lat": 12.9600, "base_lon": 77.6300},
}

EVENT_TYPES = [
    "Observed Activity",
    "Location Recurrence",
    "Temporal Correlation",
    "Network Relationship",
    "Environmental Observation",
    "Pattern Observation",
]

NODES_DATA = [
    {"node_id": "N-01", "name": "Field Node Alpha",   "zone_id": "Z-03", "lat": 12.9650, "lon": 77.5800, "battery": 91},
    {"node_id": "N-02", "name": "Field Node Beta",    "zone_id": "Z-05", "lat": 12.9900, "lon": 77.5700, "battery": 82},
    {"node_id": "N-03", "name": "Field Node Gamma",   "zone_id": "Z-02", "lat": 12.9800, "lon": 77.6100, "battery": 67},
    {"node_id": "N-04", "name": "Field Node Delta",   "zone_id": "Z-01", "lat": 12.9716, "lon": 77.5946, "battery": 95},
    {"node_id": "N-05", "name": "Field Node Epsilon", "zone_id": "Z-07", "lat": 13.0000, "lon": 77.6050, "battery": 73},
]

ENTITIES_DATA = [
    {"entity_id": "E-001", "label": "Entity Alpha",   "type": "Subject"},
    {"entity_id": "E-002", "label": "Entity Beta",    "type": "Subject"},
    {"entity_id": "E-003", "label": "Entity Gamma",   "type": "Subject"},
    {"entity_id": "E-004", "label": "Entity Delta",   "type": "Object"},
    {"entity_id": "E-005", "label": "Entity Epsilon", "type": "Subject"},
    {"entity_id": "E-006", "label": "Entity Zeta",    "type": "Object"},
    {"entity_id": "E-007", "label": "Entity Eta",     "type": "Subject"},
    {"entity_id": "E-008", "label": "Entity Theta",   "type": "Subject"},
]

NETWORKS_DATA = [
    {"network_id": "NET-001", "name": "Network Cluster Alpha", "score": 78},
    {"network_id": "NET-002", "name": "Network Cluster Beta",  "score": 64},
    {"network_id": "NET-003", "name": "Network Cluster Gamma", "score": 55},
    {"network_id": "NET-004", "name": "Network Cluster Delta", "score": 82},
    {"network_id": "NET-005", "name": "Network Cluster Epsilon","score": 47},
    {"network_id": "NET-006", "name": "Network Cluster Zeta",  "score": 71},
]


def jitter(val, scale=0.005):
    return val + random.uniform(-scale, scale)


def seed_nodes(db: Session):
    existing = db.query(Node).count()
    if existing > 0:
        return
    now = datetime.utcnow()
    for nd in NODES_DATA:
        node = Node(
            node_id=nd["node_id"],
            name=nd["name"],
            zone_id=nd["zone_id"],
            status="online" if nd["node_id"] != "N-03" else "offline",
            battery=nd["battery"],
            latitude=nd["lat"],
            longitude=nd["lon"],
            last_seen=now - timedelta(seconds=random.randint(5, 60)),
            firmware_version="v2.1.0",
            signal_strength=random.randint(-70, -40),
        )
        db.add(node)
    db.commit()


def seed_entities(db: Session):
    existing = db.query(Entity).count()
    if existing > 0:
        return
    for ent in ENTITIES_DATA:
        entity = Entity(
            entity_id=ent["entity_id"],
            label=ent["label"],
            type=ent["type"],
        )
        db.add(entity)
    db.commit()


def seed_networks(db: Session):
    existing = db.query(Network).count()
    if existing > 0:
        return
    for net in NETWORKS_DATA:
        network = Network(
            network_id=net["network_id"],
            name=net["name"],
            score=net["score"],
            node_count=random.randint(8, 22),
            edge_count=random.randint(12, 35),
            components=random.randint(1, 4),
            degree_centrality=round(random.uniform(0.45, 0.85), 2),
            betweenness=round(random.uniform(0.25, 0.65), 2),
            connection_strength=random.randint(55, 95),
            time_correlation=random.randint(50, 90),
            location_overlap=random.randint(60, 95),
            event_recurrence=random.randint(50, 85),
            centrality_score=random.randint(45, 80),
        )
        db.add(network)
    db.commit()
    
    # Link entities to networks
    entities = db.query(Entity).all()
    networks = db.query(Network).all()
    for net in networks:
        sample = random.sample(entities, k=random.randint(2, 5))
        for ent in sample:
            link = NetworkEntity(network_id=net.network_id, entity_id=ent.entity_id)
            db.add(link)
    db.commit()


def seed_events(db: Session):
    existing = db.query(Event).count()
    if existing > 0:
        return
    
    now = datetime.utcnow()
    events = []
    event_counter = 1

    # Generate 160 events spread over last 72 hours
    # Intentionally cluster Zone Z-03 to trigger hotspot/pattern
    zone_weights = {
        "Z-01": 8, "Z-02": 10, "Z-03": 30, "Z-04": 8,
        "Z-05": 12, "Z-06": 8, "Z-07": 12, "Z-08": 7,
    }
    zone_list = []
    for z, w in zone_weights.items():
        zone_list.extend([z] * w)

    node_zone_map = {nd["zone_id"]: nd["node_id"] for nd in NODES_DATA}

    for i in range(165):
        hours_back = random.uniform(0, 72)
        ts = now - timedelta(hours=hours_back)
        zone_id = random.choice(zone_list)
        zone_info = ZONES[zone_id]
        
        # Assign node if available for zone
        node_id = node_zone_map.get(zone_id, random.choice([nd["node_id"] for nd in NODES_DATA]))
        
        event = Event(
            event_id=f"EVT-{event_counter:04d}",
            event_type=random.choice(EVENT_TYPES),
            zone_id=zone_id,
            node_id=node_id,
            latitude=round(jitter(zone_info["base_lat"]), 6),
            longitude=round(jitter(zone_info["base_lon"]), 6),
            timestamp=ts,
            status="processed",
            severity=random.choice(["low", "medium", "high", "low", "medium"]),
            metadata_json="{}",
        )
        events.append(event)
        event_counter += 1

    db.add_all(events)
    db.commit()


def seed_alerts(db: Session):
    existing = db.query(Alert).count()
    if existing > 0:
        return
    now = datetime.utcnow()
    alerts_data = [
        {
            "alert_id": "ALT-0001",
            "severity": "high",
            "title": "Emerging Activity Pattern",
            "description": "Repeated observations detected across multiple time windows in Zone Z-03. Requires Human Review.",
            "zone_id": "Z-03",
            "status": "new",
            "created_at": now - timedelta(hours=1),
        },
        {
            "alert_id": "ALT-0002",
            "severity": "medium",
            "title": "Location Recurrence Detected",
            "description": "Multiple observations recorded at overlapping coordinates in Zone Z-05 within a 4-hour window.",
            "zone_id": "Z-05",
            "status": "new",
            "created_at": now - timedelta(hours=3),
        },
        {
            "alert_id": "ALT-0003",
            "severity": "high",
            "title": "Network Relationship Identified",
            "description": "Analytical pattern score threshold exceeded for Network Cluster Alpha. Human review recommended.",
            "zone_id": "Z-01",
            "status": "under_review",
            "created_at": now - timedelta(hours=5),
        },
        {
            "alert_id": "ALT-0004",
            "severity": "medium",
            "title": "Temporal Correlation Pattern",
            "description": "Events in Zone Z-07 show temporal correlation across consecutive observation windows.",
            "zone_id": "Z-07",
            "status": "new",
            "created_at": now - timedelta(hours=8),
        },
    ]
    for a in alerts_data:
        alert = Alert(
            alert_id=a["alert_id"],
            severity=a["severity"],
            title=a["title"],
            description=a["description"],
            zone_id=a["zone_id"],
            status=a["status"],
            created_at=a["created_at"],
        )
        db.add(alert)
    db.commit()


def run_seed():
    db = SessionLocal()
    try:
        seed_nodes(db)
        seed_entities(db)
        seed_networks(db)
        seed_events(db)
        seed_alerts(db)
        print("[SEED] Database seeded with synthetic demo data.")
    finally:
        db.close()
