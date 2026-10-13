"""
Network Analysis using NetworkX.
Builds relationship graphs from synthetic event data.
All analysis is on synthetic demo data only.
"""
import networkx as nx
import logging
from typing import List, Dict, Any

logger = logging.getLogger("crimenet_x.network_analysis")


def build_event_graph(events: List[Dict]) -> nx.Graph:
    """Build a NetworkX graph from synthetic event data."""
    G = nx.Graph()

    # Add zone nodes
    zones = set(e["zone_id"] for e in events)
    for zone in zones:
        G.add_node(zone, type="zone", label=f"Zone {zone}")

    # Add field node nodes
    nodes = set(e["node_id"] for e in events)
    for node in nodes:
        G.add_node(node, type="field_node", label=f"Node {node}")

    # Connect field nodes to zones
    for event in events:
        if not G.has_edge(event["node_id"], event["zone_id"]):
            G.add_edge(event["node_id"], event["zone_id"],
                       relationship="Observed At", weight=1)
        else:
            G[event["node_id"]][event["zone_id"]]["weight"] += 1

    # Add event type nodes and connect to zones
    event_types = set(e["event_type"] for e in events)
    for et in event_types:
        node_id = f"ET_{et[:8].replace(' ', '_')}"
        G.add_node(node_id, type="event_type", label=et)

    for event in events:
        et_node = f"ET_{event['event_type'][:8].replace(' ', '_')}"
        if not G.has_edge(event["zone_id"], et_node):
            G.add_edge(event["zone_id"], et_node,
                       relationship="Event Sequence", weight=1)
        else:
            G[event["zone_id"]][et_node]["weight"] += 1

    return G


def compute_centrality(G: nx.Graph) -> Dict[str, float]:
    """Compute degree centrality for all nodes."""
    try:
        return nx.degree_centrality(G)
    except Exception as e:
        logger.error(f"Centrality error: {e}")
        return {}


def compute_betweenness(G: nx.Graph) -> Dict[str, float]:
    """Compute betweenness centrality."""
    try:
        return nx.betweenness_centrality(G)
    except Exception as e:
        logger.error(f"Betweenness error: {e}")
        return {}


def detect_communities(G: nx.Graph) -> List[set]:
    """Detect communities using greedy modularity."""
    try:
        if len(G.nodes) < 3:
            return [set(G.nodes)]
        communities = list(nx.community.greedy_modularity_communities(G))
        return communities
    except Exception as e:
        logger.error(f"Community detection error: {e}")
        return [set(G.nodes)]


def get_network_stats(G: nx.Graph) -> Dict[str, Any]:
    """Get comprehensive network statistics."""
    if len(G.nodes) == 0:
        return {"nodes": 0, "edges": 0, "components": 0,
                "density": 0.0, "avg_clustering": 0.0}
    
    centrality = compute_centrality(G)
    betweenness = compute_betweenness(G)
    components = list(nx.connected_components(G))
    
    top_central = max(centrality, key=centrality.get) if centrality else None
    top_between = max(betweenness, key=betweenness.get) if betweenness else None

    return {
        "nodes": G.number_of_nodes(),
        "edges": G.number_of_edges(),
        "components": len(components),
        "density": round(nx.density(G), 4),
        "avg_clustering": round(nx.average_clustering(G), 4),
        "top_central_node": top_central,
        "max_degree_centrality": round(centrality.get(top_central, 0), 4) if top_central else 0,
        "max_betweenness": round(betweenness.get(top_between, 0), 4) if top_between else 0,
        "community_count": len(detect_communities(G)),
    }


def build_cytoscape_elements(G: nx.Graph, network_id: str) -> Dict[str, Any]:
    """Convert NetworkX graph to Cytoscape.js element format."""
    centrality = compute_centrality(G)
    betweenness = compute_betweenness(G)
    communities = detect_communities(G)
    
    community_map = {}
    for i, comm in enumerate(communities):
        for node in comm:
            community_map[node] = f"Cluster {chr(65 + i)}"

    type_colors = {
        "zone": "#4f8ef7",
        "field_node": "#22c55e",
        "event_type": "#f59e0b",
        "entity": "#a78bfa",
    }

    elements = []
    for node_id, data in G.nodes(data=True):
        node_type = data.get("type", "entity")
        elements.append({
            "data": {
                "id": str(node_id),
                "label": data.get("label", str(node_id)),
                "type": node_type,
                "community": community_map.get(node_id, "Cluster A"),
                "centrality": round(centrality.get(node_id, 0), 3),
                "betweenness": round(betweenness.get(node_id, 0), 3),
                "color": type_colors.get(node_type, "#94a3b8"),
            },
            "group": "nodes",
        })

    edge_count = 0
    for src, tgt, data in G.edges(data=True):
        edge_count += 1
        elements.append({
            "data": {
                "id": f"e{edge_count}",
                "source": str(src),
                "target": str(tgt),
                "relationship": data.get("relationship", "Related"),
                "weight": data.get("weight", 1),
            },
            "group": "edges",
        })

    stats = get_network_stats(G)
    
    return {
        "network_id": network_id,
        "elements": elements,
        "stats": stats,
        "community_count": len(communities),
    }
