"""Nodes API endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from backend.database.database import get_db
from backend.models.node import Node
from backend.schemas.node import NodeResponse, NodeStatusUpdate

router = APIRouter(prefix="/nodes", tags=["nodes"])


@router.get("", response_model=List[NodeResponse])
def list_nodes(db: Session = Depends(get_db)):
    return db.query(Node).all()


@router.get("/{node_id}", response_model=NodeResponse)
def get_node(node_id: str, db: Session = Depends(get_db)):
    node = db.query(Node).filter(Node.node_id == node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    return node


@router.patch("/{node_id}/status")
def update_node_status(node_id: str, data: NodeStatusUpdate, db: Session = Depends(get_db)):
    node = db.query(Node).filter(Node.node_id == node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    node.status = data.status
    if data.battery is not None:
        node.battery = data.battery
    if data.signal_strength is not None:
        node.signal_strength = data.signal_strength
    node.last_seen = datetime.utcnow()
    db.commit()
    db.refresh(node)
    return {"message": "Node updated", "node_id": node_id}


@router.get("/search/q")
def search_nodes(q: str, db: Session = Depends(get_db)):
    qp = f"%{q}%"
    nodes = db.query(Node).filter(
        (Node.node_id.ilike(qp)) | (Node.name.ilike(qp)) | (Node.zone_id.ilike(qp))
    ).limit(10).all()
    return [
        {"type": "node", "id": n.node_id, "title": n.name,
         "subtitle": f"{n.zone_id} | {n.status}"}
        for n in nodes
    ]
