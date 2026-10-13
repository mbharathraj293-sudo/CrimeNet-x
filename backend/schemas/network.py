"""Network Pydantic schemas."""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class NetworkResponse(BaseModel):
    network_id: str
    name: str
    score: int
    node_count: int
    edge_count: int
    components: int
    degree_centrality: float
    betweenness: float
    connection_strength: int
    time_correlation: int
    location_overlap: int
    event_recurrence: int
    centrality_score: int
    created_at: datetime

    class Config:
        from_attributes = True


class NetworkGraphNode(BaseModel):
    id: str
    label: str
    type: str
    group: Optional[str] = None


class NetworkGraphEdge(BaseModel):
    source: str
    target: str
    relationship: str
    weight: float = 1.0


class NetworkGraphResponse(BaseModel):
    network_id: str
    nodes: List[NetworkGraphNode]
    edges: List[NetworkGraphEdge]
    metadata: dict
