"""
CRIMENET-X - ESP32 Hardware Field Node Simulator
================================================
Simulates 5 physical ESP32 edge sensor nodes transmitting telemetry and
synthetic sensor incidents to the CRIMENET-X backend over HTTP REST.

Usage:
    python esp32/esp32_simulator.py [--host http://localhost:8000] [--interval 4]
"""

import argparse
import random
import time
import requests

NODES = [
    {"node_id": "N-01", "name": "Field Node Alpha",   "zone_id": "Z-03", "lat": 12.9650, "lon": 77.5800, "battery": 92},
    {"node_id": "N-02", "name": "Field Node Beta",    "zone_id": "Z-05", "lat": 12.9900, "lon": 77.5700, "battery": 84},
    {"node_id": "N-03", "name": "Field Node Gamma",   "zone_id": "Z-02", "lat": 12.9800, "lon": 77.6100, "battery": 68},
    {"node_id": "N-04", "name": "Field Node Delta",   "zone_id": "Z-01", "lat": 12.9716, "lon": 77.5946, "battery": 96},
    {"node_id": "N-05", "name": "Field Node Epsilon", "zone_id": "Z-07", "lat": 13.0000, "lon": 77.6050, "battery": 74},
]

EVENT_TYPES = [
    "Observed Activity",
    "Location Recurrence",
    "Temporal Correlation",
    "Network Relationship",
    "Environmental Observation",
    "Pattern Observation"
]


def jitter(val, scale=0.003):
    return round(val + random.uniform(-scale, scale), 6)


def run_simulation(host: str, interval: float):
    print(f"[*] CRIMENET-X ESP32 Simulator Active")
    print(f"[*] Target Host: {host}")
    print(f"[*] Transmitting sensor telemetry every ~{interval}s...")
    print(f"[*] Press Ctrl+C to terminate simulation.\n")

    cycle = 0
    try:
        while True:
            cycle += 1
            node = random.choice(NODES)

            # 1. Dispatch periodic node status heartbeat
            rssi = random.randint(-75, -45)
            node["battery"] = max(10, node["battery"] - (1 if random.random() < 0.1 else 0))
            
            try:
                status_res = requests.patch(
                    f"{host}/api/nodes/{node['node_id']}/status",
                    json={
                        "status": "online",
                        "battery": node["battery"],
                        "signal_strength": rssi
                    },
                    timeout=5
                )
                if status_res.status_code == 200:
                    print(f"[{node['node_id']}] Heartbeat ACK | Batt: {node['battery']}% | RSSI: {rssi} dBm")
            except Exception as e:
                print(f"[!] Error contacting {host}: {e}")

            # 2. Trigger sensor incident
            event_type = random.choice(EVENT_TYPES)
            severity = random.choices(["low", "medium", "high"], weights=[6, 3, 1])[0]

            payload = {
                "node_id": node["node_id"],
                "event_type": event_type,
                "zone_id": node["zone_id"],
                "latitude": jitter(node["lat"]),
                "longitude": jitter(node["lon"]),
                "severity": severity
            }

            try:
                evt_res = requests.post(f"{host}/api/events", json=payload, timeout=5)
                if evt_res.status_code in [200, 201]:
                    evt_data = evt_res.json()
                    print(f" >> [TRIGGER] {node['node_id']} ({node['zone_id']}) -> {event_type} [{severity.upper()}] EVT_ID: {evt_data.get('event_id')}")
            except Exception as e:
                print(f"[!] Event dispatch error: {e}")

            time.sleep(random.uniform(interval * 0.7, interval * 1.3))

    except KeyboardInterrupt:
        print("\n[*] ESP32 Field Simulator stopped.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CRIMENET-X ESP32 Field Simulator")
    parser.add_argument("--host", default="http://localhost:8000", help="CRIMENET-X Backend URL")
    parser.add_argument("--interval", type=float, default=3.5, help="Event generation cadence in seconds")
    args = parser.parse_args()
    run_simulation(args.host, args.interval)
