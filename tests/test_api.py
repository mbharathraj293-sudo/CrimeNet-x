"""
Comprehensive API test suite for CRIMENET-X backend.
Verifies all REST endpoints, validation errors, schemas, and lifecycle operations.
"""
import pytest
from datetime import datetime


def test_health_check(client):
    """Verify /api/health endpoint returns operational status."""
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "operational"
    assert data["app"] == "CrimeNet-X"
    assert data["database"] == "online"


def test_analytics_summary(client):
    """Verify /api/analytics returns valid summary and distributions."""
    res = client.get("/api/analytics")
    assert res.status_code == 200
    data = res.json()
    assert "summary" in data
    assert "total_events" in data["summary"]
    assert "total_nodes" in data["summary"]
    assert "hourly_distribution" in data
    assert "activity_trend" in data


def test_temporal_analytics(client):
    """Verify /api/analytics/temporal returns time-series distributions."""
    res = client.get("/api/analytics/temporal")
    assert res.status_code == 200
    data = res.json()
    assert "hourly" in data
    assert "daily" in data
    assert "zone_timeline" in data
    assert "event_types" in data
    assert "trend" in data
    assert "network_evolution" in data


def test_pattern_analytics(client):
    """Verify /api/analytics/patterns returns emerging pattern lists."""
    res = client.get("/api/analytics/patterns")
    assert res.status_code == 200
    data = res.json()
    assert "patterns" in data
    assert isinstance(data["patterns"], list)


def test_list_events(client):
    """Verify /api/events listing with pagination and filters."""
    res = client.get("/api/events?limit=10")
    assert res.status_code == 200
    events = res.json()
    assert isinstance(events, list)
    assert len(events) <= 10
    if events:
        first = events[0]
        assert "event_id" in first
        assert "event_type" in first
        assert "zone_id" in first
        assert "latitude" in first
        assert "longitude" in first


def test_recent_events(client):
    """Verify /api/events/recent returns recent events."""
    res = client.get("/api/events/recent?limit=5")
    assert res.status_code == 200
    events = res.json()
    assert isinstance(events, list)
    assert len(events) <= 5


def test_event_count(client):
    """Verify /api/events/count returns integer count."""
    res = client.get("/api/events/count")
    assert res.status_code == 200
    data = res.json()
    assert "count" in data
    assert isinstance(data["count"], int)
    assert data["count"] >= 0


def test_search_events(client):
    """Verify /api/events/search searches by term."""
    res = client.get("/api/events/search?q=Observed")
    assert res.status_code == 200
    results = res.json()
    assert isinstance(results, list)


def test_create_event_valid(client):
    """Verify POST /api/events successfully creates an event."""
    payload = {
        "node_id": "N-01",
        "event_type": "Observed Activity",
        "zone_id": "Z-01",
        "latitude": 12.9716,
        "longitude": 77.5946,
        "severity": "low",
    }
    res = client.post("/api/events", json=payload)
    assert res.status_code in [200, 201]
    data = res.json()
    assert data["node_id"] == "N-01"
    assert data["zone_id"] == "Z-01"
    assert "event_id" in data
    assert data["event_id"].startswith("EVT-")


def test_create_event_validation_error(client):
    """Verify POST /api/events rejects invalid coordinates."""
    invalid_payload = {
        "node_id": "N-01",
        "event_type": "Observed Activity",
        "zone_id": "Z-01",
        "latitude": 199.99,  # Invalid latitude (> 90)
        "longitude": 77.5946,
    }
    res = client.post("/api/events", json=invalid_payload)
    assert res.status_code == 422


def test_list_nodes(client):
    """Verify /api/nodes returns edge node telemetry list."""
    res = client.get("/api/nodes")
    assert res.status_code == 200
    nodes = res.json()
    assert isinstance(nodes, list)
    assert len(nodes) > 0
    node = nodes[0]
    assert "node_id" in node
    assert "status" in node
    assert "battery" in node


def test_get_single_node(client):
    """Verify /api/nodes/{id} returns node details."""
    res = client.get("/api/nodes/N-01")
    assert res.status_code == 200
    node = res.json()
    assert node["node_id"] == "N-01"


def test_get_node_not_found(client):
    """Verify /api/nodes/{id} returns 404 for unknown node."""
    res = client.get("/api/nodes/NON_EXISTENT")
    assert res.status_code == 404


def test_update_node_status(client):
    """Verify PATCH /api/nodes/{id}/status updates telemetry."""
    payload = {
        "status": "online",
        "battery": 88,
        "signal_strength": -55,
    }
    res = client.patch("/api/nodes/N-01/status", json=payload)
    assert res.status_code == 200
    
    # Confirm persistence
    get_res = client.get("/api/nodes/N-01")
    assert get_res.status_code == 200
    assert get_res.json()["battery"] == 88
    assert get_res.json()["signal_strength"] == -55


def test_list_networks(client):
    """Verify /api/networks returns network clusters."""
    res = client.get("/api/networks")
    assert res.status_code == 200
    networks = res.json()
    assert isinstance(networks, list)
    assert len(networks) > 0


def test_get_full_network_graph(client):
    """Verify /api/networks/graph/full returns Cytoscape-formatted structure."""
    res = client.get("/api/networks/graph/full")
    assert res.status_code == 200
    data = res.json()
    assert "elements" in data
    assert isinstance(data["elements"], list)
    assert len(data["elements"]) > 0
    node_elements = [e for e in data["elements"] if e.get("group") == "nodes"]
    edge_elements = [e for e in data["elements"] if e.get("group") == "edges"]
    assert len(node_elements) > 0
    assert len(edge_elements) > 0


def test_get_single_network_and_graph(client):
    """Verify /api/networks/{id} and subgraph."""
    res = client.get("/api/networks/NET-001")
    assert res.status_code == 200
    assert res.json()["network_id"] == "NET-001"
    
    g_res = client.get("/api/networks/NET-001/graph")
    assert g_res.status_code == 200
    assert "elements" in g_res.json()


def test_get_hotspots(client):
    """Verify /api/hotspots returns spatial cluster definitions."""
    res = client.get("/api/hotspots")
    assert res.status_code == 200
    data = res.json()
    assert "hotspots" in data
    assert "markers" in data
    assert "total_events" in data
    assert isinstance(data["hotspots"], list)
    assert isinstance(data["markers"], list)


def test_list_alerts(client):
    """Verify /api/alerts returns triage queue."""
    res = client.get("/api/alerts")
    assert res.status_code == 200
    alerts = res.json()
    assert isinstance(alerts, list)


def test_alert_count(client):
    """Verify /api/alerts/count returns active count."""
    res = client.get("/api/alerts/count")
    assert res.status_code == 200
    assert "count" in res.json()


def test_update_alert_status_lifecycle(client):
    """Verify alert status transition New -> Under Review -> Resolved."""
    alerts_res = client.get("/api/alerts")
    assert alerts_res.status_code == 200
    alerts = alerts_res.json()
    if alerts:
        target_id = alerts[0]["alert_id"]
        
        # Transition to under_review
        res1 = client.patch(f"/api/alerts/{target_id}/status", json={"status": "under_review", "resolved_by": "Test Analyst"})
        assert res1.status_code == 200
        
        # Transition to resolved
        res2 = client.patch(f"/api/alerts/{target_id}/status", json={"status": "resolved", "resolved_by": "Lead Reviewer"})
        assert res2.status_code == 200
        
        # Check invalid status
        res_invalid = client.patch(f"/api/alerts/{target_id}/status", json={"status": "invalid_state"})
        assert res_invalid.status_code == 400


def test_data_stats(client):
    """Verify /api/data/stats returns database metric counts."""
    res = client.get("/api/data/stats")
    assert res.status_code == 200
    data = res.json()
    assert "total_events" in data
    assert "total_nodes" in data
    assert "total_networks" in data
    assert "total_alerts" in data


def test_csv_upload_validation(client):
    """Verify /api/data/upload validates file format and columns."""
    # 1. Non-CSV rejection
    res_bad_ext = client.post("/api/data/upload", files={"file": ("test.txt", b"plain text", "text/plain")})
    assert res_bad_ext.status_code == 400
    
    # 2. Empty CSV
    res_empty = client.post("/api/data/upload", files={"file": ("empty.csv", b"", "text/csv")})
    assert res_empty.status_code == 400
    
    # 3. Missing required columns
    bad_csv = b"col1,col2\nval1,val2\n"
    res_missing = client.post("/api/data/upload", files={"file": ("bad.csv", bad_csv, "text/csv")})
    assert res_missing.status_code == 400
    
    # 4. Valid CSV import
    valid_csv = (
        b"event_type,zone_id,node_id,latitude,longitude,severity\n"
        b"Observed Activity,Z-01,N-01,12.9716,77.5946,low\n"
        b"Temporal Correlation,Z-02,N-03,12.9800,77.6100,medium\n"
    )
    res_valid = client.post("/api/data/upload", files={"file": ("valid.csv", valid_csv, "text/csv")})
    assert res_valid.status_code == 200
    data = res_valid.json()
    assert data["imported"] == 2


def test_demo_lifecycle(client):
    """Verify demo mode start, status, duplicate prevention, and stop."""
    # Check initial status
    status_res = client.get("/api/demo/status")
    assert status_res.status_code == 200
    
    # Start demo
    start_res = client.post("/api/demo/start")
    assert start_res.status_code == 200
    assert start_res.json()["status"] == "running"
    
    # Guard against duplicate start
    dup_res = client.post("/api/demo/start")
    assert dup_res.status_code == 200
    assert dup_res.json()["message"] == "Demo already running"
    
    # Stop demo
    stop_res = client.post("/api/demo/stop")
    assert stop_res.status_code == 200
    assert stop_res.json()["status"] == "stopped"


def test_static_routes(client):
    """Verify root and static page routing."""
    res_root = client.get("/")
    assert res_root.status_code == 200
    assert "CRIMENET-X" in res_root.text

    res_index = client.get("/index.html")
    assert res_index.status_code == 200
    assert "CRIMENET-X" in res_index.text

    res_page = client.get("/pages/command-center.html")
    assert res_page.status_code == 200
    assert "Command Center" in res_page.text
