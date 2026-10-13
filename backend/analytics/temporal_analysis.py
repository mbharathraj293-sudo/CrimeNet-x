"""
Temporal Analysis using Pandas.
Computes hourly/daily distributions of synthetic events for Chart.js.
"""
import pandas as pd
import numpy as np
from typing import List, Dict, Any
import logging

logger = logging.getLogger("crimenet_x.temporal")


def events_to_dataframe(events: List[Dict]) -> pd.DataFrame:
    """Convert event list to DataFrame."""
    if not events:
        return pd.DataFrame()
    df = pd.DataFrame(events)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["hour"] = df["timestamp"].dt.hour
    df["date"] = df["timestamp"].dt.date
    df["day_name"] = df["timestamp"].dt.day_name()
    df["week"] = df["timestamp"].dt.isocalendar().week.astype(int)
    return df


def get_hourly_distribution(events: List[Dict]) -> Dict[str, Any]:
    """Get event counts by hour of day."""
    df = events_to_dataframe(events)
    if df.empty:
        return {"labels": list(range(24)), "data": [0] * 24}
    
    hourly = df.groupby("hour").size().reindex(range(24), fill_value=0)
    return {
        "labels": [f"{h:02d}:00" for h in range(24)],
        "data": hourly.tolist(),
    }


def get_daily_distribution(events: List[Dict]) -> Dict[str, Any]:
    """Get event counts by day."""
    df = events_to_dataframe(events)
    if df.empty:
        return {"labels": [], "data": []}
    
    daily = df.groupby("date").size().sort_index()
    return {
        "labels": [str(d) for d in daily.index],
        "data": daily.tolist(),
    }


def get_zone_timeline(events: List[Dict]) -> Dict[str, Any]:
    """Get event counts per zone over time (last 24h, hourly)."""
    df = events_to_dataframe(events)
    if df.empty:
        return {"labels": [], "datasets": []}
    
    # Last 24 hours
    cutoff = df["timestamp"].max() - pd.Timedelta(hours=24)
    recent = df[df["timestamp"] >= cutoff].copy()
    
    if recent.empty:
        return {"labels": [], "datasets": []}
    
    recent["hour_bucket"] = recent["timestamp"].dt.floor("h")
    zones = recent["zone_id"].unique()
    hours = sorted(recent["hour_bucket"].unique())
    
    datasets = []
    colors = ["#4f8ef7", "#22c55e", "#f59e0b", "#ef4444", "#a78bfa", "#14b8a6", "#f97316", "#ec4899"]
    
    for i, zone in enumerate(sorted(zones)):
        zone_data = recent[recent["zone_id"] == zone]
        counts = zone_data.groupby("hour_bucket").size()
        color = colors[i % len(colors)]
        datasets.append({
            "label": zone,
            "data": [int(counts.get(h, 0)) for h in hours],
            "borderColor": color,
            "backgroundColor": color + "33",
            "fill": True,
            "tension": 0.4,
        })
    
    return {
        "labels": [h.strftime("%H:%M") for h in hours],
        "datasets": datasets,
    }


def get_event_type_distribution(events: List[Dict]) -> Dict[str, Any]:
    """Get event type counts for donut chart."""
    df = events_to_dataframe(events)
    if df.empty:
        return {"labels": [], "data": []}
    
    counts = df["event_type"].value_counts()
    return {
        "labels": counts.index.tolist(),
        "data": counts.tolist(),
    }


def get_activity_trend(events: List[Dict]) -> Dict[str, Any]:
    """Get events per hour for the last 12 hours for trend chart."""
    df = events_to_dataframe(events)
    if df.empty:
        return {"labels": [], "events": [], "alerts": []}
    
    now = df["timestamp"].max()
    cutoff = now - pd.Timedelta(hours=12)
    recent = df[df["timestamp"] >= cutoff].copy()
    recent["hour_bucket"] = recent["timestamp"].dt.floor("h")
    
    all_hours = pd.date_range(
        start=cutoff.floor("h"), end=now.floor("h"), freq="h"
    )
    counts = recent.groupby("hour_bucket").size().reindex(all_hours, fill_value=0)
    
    # Simulate alert counts as a fraction of events
    alert_counts = (counts * np.random.uniform(0.1, 0.3, len(counts))).astype(int)
    
    return {
        "labels": [h.strftime("%H:%M") for h in all_hours],
        "events": counts.tolist(),
        "alerts": alert_counts.tolist(),
    }


def get_network_evolution(events: List[Dict]) -> Dict[str, Any]:
    """Get network relationship count over time."""
    df = events_to_dataframe(events)
    if df.empty:
        return {"labels": [], "data": []}
    
    daily = df.groupby("date").size().sort_index()
    cumulative = daily.cumsum()
    
    return {
        "labels": [str(d) for d in cumulative.index],
        "data": (cumulative // 3).tolist(),  # Scale to relationship count
    }
