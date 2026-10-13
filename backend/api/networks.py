"""Networks API endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from backend.database.database import get_db
from backend.schemas.network import NetworkResponse
from backend.services.network_service import (
    get_networks, get_network, get_network_graph, get_full_graph
)

router = APIRouter(prefix="/networks", tags=["networks"])


@router.get("", response_model=List[NetworkResponse])
def list_networks(db: Session = Depends(get_db)):
    return get_networks(db)


@router.get("/graph/full")
def full_graph(db: Session = Depends(get_db)):
    """Get full system-wide network graph for Cytoscape.js."""
    return get_full_graph(db)


@router.get("/{network_id}", response_model=NetworkResponse)
def get_single_network(network_id: str, db: Session = Depends(get_db)):
    network = get_network(db, network_id)
    if not network:
        raise HTTPException(status_code=404, detail="Network not found")
    return network


@router.get("/{network_id}/graph")
def network_graph(network_id: str, db: Session = Depends(get_db)):
    """Get Cytoscape.js graph for a specific network."""
    graph = get_network_graph(db, network_id)
    if not graph:
        raise HTTPException(status_code=404, detail="Network not found")
    return graph
