"""
Geospatial Analysis - Hotspot detection using zone clustering.
All coordinates are synthetic demo data.
"""
import pandas as pd
from typing import List, Dict, Any
from backend.config import settings
import logging

logger = logging.getLogger("crimenet_x.geo")

ZONE_NAMES = {
    "Z-01": "Zone Alpha", "Z-02": "Zone Beta", "Z-03": "Zone Gamma",
    "Z-04": "Zone Delta", "Z-05": "Zone Epsilon", "Z-06": "Zone Zeta",
    "Z-07": "Zone Eta", "Z-08": "Zone Theta",
}


def calculate_hotspots(events: List[Dict]) -> List[Dict[str, Any]]:
    """Calculate activity hotspots from synthetic events."""
    if not events:
        return []
    
    df = pd.DataFrame(events)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    
    # Group by zone
    zone_stats = df.groupby("zone_id").agg(
        count=("event_id", "count"),
        lat_mean=("latitude", "mean"),
        lon_mean=("longitude", "mean"),
        lat_std=("latitude", "std"),
        lon_std=("longitude", "std"),
        event_types=("event_type", lambda x: list(x.unique())),
        unique_nodes=("node_id", "nunique"),
        last_event=("timestamp", "max"),
        first_event=("timestamp", "min"),
    ).reset_index()
    
    hotspots = []
    for _, row in zone_stats.iterrows():
        count = int(row["count"])
        
        if count >= settings.HOTSPOT_HIGH_THRESHOLD:
            activity_level = "high"
            pattern_status = "Emerging Pattern"
        elif count >= settings.HOTSPOT_MEDIUM_THRESHOLD:
            activity_level = "medium"
            pattern_status = "Observed Pattern"
        else:
            activity_level = "low"
            pattern_status = "Baseline Activity"
        
        # Time span in hours
        time_span = 0
        if pd.notna(row["last_event"]) and pd.notna(row["first_event"]):
            time_span = round((row["last_event"] - row["first_event"]).total_seconds() / 3600, 1)
        
        hotspots.append({
            "zone_id": row["zone_id"],
            "zone_name": ZONE_NAMES.get(row["zone_id"], row["zone_id"]),
            "count": count,
            "latitude": round(float(row["lat_mean"]), 6),
            "longitude": round(float(row["lon_mean"]), 6),
            "radius": min(count * 30, 500),  # meters
            "activity_level": activity_level,
            "pattern_status": pattern_status,
            "unique_nodes": int(row["unique_nodes"]),
            "event_types": row["event_types"],
            "time_span_hours": time_span,
            "recommendation": "Human review recommended." if activity_level in ("high", "medium") else "Continue monitoring.",
        })
    
    # Sort by count descending
    hotspots.sort(key=lambda x: x["count"], reverse=True)
    return hotspots


def get_map_markers(events: List[Dict]) -> List[Dict[str, Any]]:
    """Get individual event markers for Leaflet map."""
    markers = []
    severity_colors = {
        "high": "#ef4444",
        "medium": "#f59e0b",
        "low": "#22c55e",
    }
    type_icons = {
        "Observed Activity": "eye",
        "Location Recurrence": "map-pin",
        "Temporal Correlation": "clock",
        "Network Relationship": "share-2",
        "Environmental Observation": "activity",
        "Pattern Observation": "search",
    }
    
    for event in events[-200:]:  # Limit to last 200 for performance
        markers.append({
            "event_id": event.get("event_id", ""),
            "event_type": event.get("event_type", ""),
            "zone_id": event.get("zone_id", ""),
            "node_id": event.get("node_id", ""),
            "latitude": event.get("latitude", 0),
            "longitude": event.get("longitude", 0),
            "timestamp": str(event.get("timestamp", "")),
            "severity": event.get("severity", "low"),
            "color": severity_colors.get(event.get("severity", "low"), "#94a3b8"),
            "icon": type_icons.get(event.get("event_type", ""), "circle"),
        })
    
    return markers
