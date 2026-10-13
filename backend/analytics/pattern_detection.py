"""
Pattern Detection Engine - detects emerging activity patterns in synthetic data.
All detected patterns require human review and carry no automated enforcement implications.
"""
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Tuple
from collections import Counter
import logging

logger = logging.getLogger("crimenet_x.pattern")


def detect_repeated_activity(events: List[Dict], threshold: int = 3) -> List[Dict]:
    """Detect zones with repeated activity in short time windows."""
    if len(events) < threshold:
        return []
    
    df = pd.DataFrame(events)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp")
    
    patterns = []
    zones = df["zone_id"].unique()
    
    for zone in zones:
        zone_events = df[df["zone_id"] == zone].copy()
        if len(zone_events) < threshold:
            continue
        
        # Rolling 4-hour windows
        zone_events = zone_events.set_index("timestamp").sort_index()
        window_counts = zone_events["event_id"].rolling("4h").count()
        max_count = int(window_counts.max())
        
        if max_count >= threshold:
            patterns.append({
                "pattern_type": "Repeated Activity",
                "zone_id": zone,
                "observation_count": max_count,
                "severity": "high" if max_count >= 8 else "medium",
                "description": (
                    f"Repeated observations detected in {zone} within rolling 4-hour windows. "
                    f"Peak count: {max_count}. Requires Human Review."
                ),
            })
    
    return patterns


def detect_temporal_correlations(events: List[Dict]) -> List[Dict]:
    """Detect events that consistently occur in similar time windows across multiple zones."""
    if len(events) < 10:
        return []
    
    df = pd.DataFrame(events)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["hour"] = df["timestamp"].dt.hour
    
    # Count events by zone+hour
    zone_hour = df.groupby(["zone_id", "hour"]).size().reset_index(name="count")
    
    # Find hours with high cross-zone activity
    hour_totals = zone_hour.groupby("hour")["count"].sum()
    peak_hours = hour_totals[hour_totals > hour_totals.mean() * 1.5].index.tolist()
    
    patterns = []
    for hour in peak_hours:
        zones_at_hour = zone_hour[zone_hour["hour"] == hour]["zone_id"].tolist()
        if len(zones_at_hour) >= 2:
            patterns.append({
                "pattern_type": "Temporal Correlation",
                "hour": hour,
                "zones": zones_at_hour,
                "severity": "medium",
                "description": (
                    f"Elevated activity observed across {len(zones_at_hour)} zones "
                    f"during hour {hour:02d}:00. Temporal correlation detected. "
                    f"Human review recommended."
                ),
            })
    
    return patterns


def detect_location_overlap(events: List[Dict]) -> List[Dict]:
    """Detect events with overlapping coordinates across time windows."""
    if len(events) < 5:
        return []
    
    df = pd.DataFrame(events)
    df["lat_rounded"] = df["latitude"].round(3)
    df["lon_rounded"] = df["longitude"].round(3)
    
    location_counts = df.groupby(["lat_rounded", "lon_rounded", "zone_id"]).size().reset_index(name="count")
    repeated = location_counts[location_counts["count"] >= 3]
    
    patterns = []
    for _, row in repeated.iterrows():
        patterns.append({
            "pattern_type": "Location Overlap",
            "zone_id": row["zone_id"],
            "coordinates": (float(row["lat_rounded"]), float(row["lon_rounded"])),
            "observation_count": int(row["count"]),
            "severity": "medium",
            "description": (
                f"Multiple observations ({int(row['count'])}) recorded at overlapping "
                f"coordinates in {row['zone_id']}. Location recurrence detected."
            ),
        })
    
    return patterns


def detect_network_expansion(events: List[Dict]) -> List[Dict]:
    """Detect expansion of activity across new zones over time."""
    if len(events) < 10:
        return []
    
    df = pd.DataFrame(events)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp")
    
    # Split into first half and second half
    midpoint = len(df) // 2
    early_zones = set(df.iloc[:midpoint]["zone_id"].unique())
    late_zones = set(df.iloc[midpoint:]["zone_id"].unique())
    new_zones = late_zones - early_zones
    
    patterns = []
    if new_zones:
        patterns.append({
            "pattern_type": "Network Expansion",
            "new_zones": list(new_zones),
            "severity": "medium" if len(new_zones) >= 2 else "low",
            "description": (
                f"Activity has extended into {len(new_zones)} additional zone(s) "
                f"in the observation period: {', '.join(new_zones)}. "
                f"Pattern expansion detected."
            ),
        })
    
    return patterns


def compute_analytical_pattern_score(
    connection_strength: int,
    time_correlation: int,
    location_overlap: int,
    event_recurrence: int,
    centrality: int,
) -> int:
    """
    Compute the Analytical Pattern Score (0-100).
    
    This score represents the strength of observed analytical patterns
    in synthetic data. It is NOT a criminal probability score.
    Human review is always required.
    """
    weights = {
        "connection_strength": 0.25,
        "time_correlation": 0.20,
        "location_overlap": 0.25,
        "event_recurrence": 0.20,
        "centrality": 0.10,
    }
    
    score = (
        connection_strength * weights["connection_strength"] +
        time_correlation * weights["time_correlation"] +
        location_overlap * weights["location_overlap"] +
        event_recurrence * weights["event_recurrence"] +
        centrality * weights["centrality"]
    )
    
    return min(100, max(0, round(score)))


def get_emerging_patterns_summary(events: List[Dict]) -> List[Dict]:
    """Get a summary list of all detected emerging patterns."""
    all_patterns = []
    all_patterns.extend(detect_repeated_activity(events))
    all_patterns.extend(detect_temporal_correlations(events))
    all_patterns.extend(detect_location_overlap(events))
    all_patterns.extend(detect_network_expansion(events))
    
    # Deduplicate by zone+type
    seen = set()
    unique_patterns = []
    for p in all_patterns:
        key = (p["pattern_type"], p.get("zone_id", ""))
        if key not in seen:
            seen.add(key)
            unique_patterns.append(p)
    
    return unique_patterns[:10]  # Cap at 10 for display
