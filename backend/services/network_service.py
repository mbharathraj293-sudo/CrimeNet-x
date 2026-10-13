"""Network service - builds and queries network graphs."""
import logging
from sqlalchemy.orm import Session
from backend.models.network import Network, NetworkEntity
from backend.models.entity import Entity
from backend.models.event import Event
from backend.analytics.network_analysis import build_event_graph, build_cytoscape_elements

logger = logging.getLogger("crimenet_x.network_service")


def get_networks(db: Session) -> list:
    return db.query(Network).order_by(Network.score.desc()).all()


def get_network(db: Session, network_id: str) -> Network:
    return db.query(Network).filter(Network.network_id == network_id).first()


def get_network_graph(db: Session, network_id: str) -> dict:
    """Build a Cytoscape.js graph for a specific network."""
    network = get_network(db, network_id)
    if not network:
        return None
    
    # Get all events and build graph
    events = db.query(Event).limit(200).all()
    event_dicts = [
        {
            "event_id": e.event_id,
            "zone_id": e.zone_id,
            "node_id": e.node_id,
            "event_type": e.event_type,
            "timestamp": e.timestamp,
        }
        for e in events
    ]
    
    G = build_event_graph(event_dicts)
    graph_data = build_cytoscape_elements(G, network_id)
    
    # Add network metadata
    graph_data["network_meta"] = {
        "name": network.name,
        "score": network.score,
        "degree_centrality": network.degree_centrality,
        "betweenness": network.betweenness,
        "connection_strength": network.connection_strength,
        "time_correlation": network.time_correlation,
        "location_overlap": network.location_overlap,
        "event_recurrence": network.event_recurrence,
        "centrality_score": network.centrality_score,
        "components": network.components,
    }
    
    return graph_data


def get_full_graph(db: Session) -> dict:
    """Build the full system-wide network graph."""
    events = db.query(Event).limit(300).all()
    event_dicts = [
        {
            "event_id": e.event_id,
            "zone_id": e.zone_id,
            "node_id": e.node_id,
            "event_type": e.event_type,
            "timestamp": e.timestamp,
        }
        for e in events
    ]
    G = build_event_graph(event_dicts)
    return build_cytoscape_elements(G, "FULL")


def get_network_count(db: Session) -> int:
    return db.query(Network).count()
