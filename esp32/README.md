# ESP32 Field Node Integration Guide

This directory contains edge hardware firmware and simulation scripts for connecting physical ESP32 microcontrollers to the **CRIMENET-X** intelligence analytics platform.

---

## 1. Architecture

```text
  [ ESP32 Field Node ]
           │
           │ 802.11 b/g/n Wi-Fi
           ▼
  [ HTTP REST API ]
  • POST /api/events          --> Dispatches sensor observations
  • PATCH /api/nodes/{id}/status --> Dispatches heartbeat telemetry (battery, RSSI)
           │
           ▼
  [ CRIMENET-X Backend ] ──WebSocket──> [ Live Command Center UI ]
```

---

## 2. Hardware Bill of Materials (BOM)

- **Microcontroller**: ESP32 DevKit v1 / ESP-WROOM-32
- **Trigger Sensor**: PIR Motion Sensor (HC-SR501 or AM312) / Vibration Sensor (SW-420)
- **Status LED**: Built-in GPIO 2
- **Power**: 5V Micro-USB or 3.7V LiPo battery

---

## 3. Wiring Pinout

| ESP32 Pin | Component Pin | Description |
|-----------|---------------|-------------|
| **GPIO 4** | Sensor OUT / Signal | Digital trigger input (Active HIGH) |
| **3V3** | Sensor VCC | 3.3V Power supply |
| **GND** | Sensor GND | Ground reference |
| **GPIO 2** | Built-in LED | Status indicator |

---

## 4. Flashing Firmware (`firmware.ino`)

1. Install the **Arduino IDE** (v2.0+).
2. Add ESP32 board support via Boards Manager: `https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json`.
3. Install **ArduinoJson** library (v6.x) via Library Manager.
4. Open `esp32/firmware.ino`.
5. Update your Wi-Fi credentials and server IP:
   ```cpp
   const char* WIFI_SSID     = "YOUR_WIFI_SSID";
   const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";
   const char* SERVER_HOST   = "http://192.168.1.100:8000";
   ```
6. Select Board: **ESP32 Dev Module** and upload.

---

## 5. Software Simulation (Without Hardware)

If you do not have physical ESP32 boards available, run the simulated multi-node CLI:

```bash
python esp32/esp32_simulator.py --host http://localhost:8000 --interval 3.0
```

This simulates 5 autonomous edge nodes (`N-01` through `N-05`) sending telemetry heartbeats and spatial events with live coordinate jitter to the backend.
