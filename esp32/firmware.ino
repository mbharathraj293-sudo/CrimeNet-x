/*
 * ============================================================================
 * CRIMENET-X - ESP32 Field Node Firmware
 * ============================================================================
 * Academic Prototype - Edge IoT Node Integration
 *
 * This firmware connects an ESP32 microcontroller to local Wi-Fi and dispatches
 * synthetic environmental sensor telemetry and observed incident events to the
 * CRIMENET-X FastAPI backend via RESTful HTTP JSON payloads.
 *
 * Hardware:
 *   - ESP32 Development Board (ESP-WROOM-32)
 *   - Digital Input Trigger (PIR Motion / Vibration Sensor on GPIO 4)
 *   - Status Indicator LED (GPIO 2)
 *
 * Ethical Notice:
 *   All data transmitted represents synthetic demo environmental patterns.
 *   No biometric, facial, or real-world personal identification is performed.
 * ============================================================================
 */

#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

// ─── Network Configuration ──────────────────────────────────────────────────
const char* WIFI_SSID     = "YOUR_WIFI_SSID";
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";

// CRIMENET-X Backend Server URL
const char* SERVER_HOST   = "http://192.168.1.100:8000"; // Replace with your host IP

// ─── Node Identity Configuration ────────────────────────────────────────────
const char* NODE_ID       = "N-01";            // Matches database node_id
const char* NODE_ZONE     = "Z-03";            // Assigned synthetic sector
const float NODE_LAT      = 12.9650;           // Base sector latitude
const float NODE_LON      = 77.5800;           // Base sector longitude
const char* FIRMWARE_VER  = "v2.1.0";

// ─── Pin Definitions ────────────────────────────────────────────────────────
const int SENSOR_PIN      = 4;                 // Digital sensor trigger input
const int LED_PIN         = 2;                 // Built-in status indicator LED

// ─── Timing Parameters ──────────────────────────────────────────────────────
unsigned long lastHeartbeat = 0;
const unsigned long HEARTBEAT_INTERVAL = 30000; // 30 seconds

int batteryLevel = 95;

void setup() {
  Serial.begin(115200);
  pinMode(SENSOR_PIN, INPUT_PULLDOWN);
  pinMode(LED_PIN, OUTPUT);

  Serial.println("\n[CRIMENET-X] Initializing ESP32 Field Node...");
  Serial.print("[CRIMENET-X] Node ID: "); Serial.println(NODE_ID);
  Serial.print("[CRIMENET-X] Sector: ");  Serial.println(NODE_ZONE);

  connectToWiFi();
  sendHeartbeat();
}

void loop() {
  // Check Wi-Fi connection
  if (WiFi.status() != WL_CONNECTED) {
    connectToWiFi();
  }

  // Periodic Telemetry Heartbeat
  if (millis() - lastHeartbeat >= HEARTBEAT_INTERVAL) {
    lastHeartbeat = millis();
    sendHeartbeat();
  }

  // Sensor Event Trigger Detection
  if (digitalRead(SENSOR_PIN) == HIGH) {
    Serial.println("[CRIMENET-X] Sensor activity triggered!");
    digitalWrite(LED_PIN, HIGH);
    sendIncidentEvent("Observed Activity", "medium");
    delay(2000); // Debounce
    digitalWrite(LED_PIN, LOW);
  }

  delay(100);
}

void connectToWiFi() {
  Serial.print("[Wi-Fi] Connecting to ");
  Serial.println(WIFI_SSID);

  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(500);
    Serial.print(".");
    digitalWrite(LED_PIN, !digitalRead(LED_PIN));
    attempts++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    digitalWrite(LED_PIN, HIGH);
    Serial.println("\n[Wi-Fi] Connected successfully!");
    Serial.print("[Wi-Fi] IP Address: ");
    Serial.println(WiFi.localIP());
  } else {
    digitalWrite(LED_PIN, LOW);
    Serial.println("\n[Wi-Fi] Connection timed out. Retrying...");
  }
}

void sendHeartbeat() {
  if (WiFi.status() != WL_CONNECTED) return;

  HTTPClient http;
  String url = String(SERVER_HOST) + "/api/nodes/" + NODE_ID + "/status";

  http.begin(url);
  http.addHeader("Content-Type", "application/json");

  // Construct JSON payload
  StaticJsonDocument<128> doc;
  doc["status"]          = "online";
  doc["battery"]         = batteryLevel;
  doc["signal_strength"] = WiFi.RSSI();

  String requestBody;
  serializeJson(doc, requestBody);

  int httpCode = http.PATCH(requestBody);

  if (httpCode > 0) {
    Serial.printf("[Heartbeat] Node %s ping sent: HTTP %d\n", NODE_ID, httpCode);
  } else {
    Serial.printf("[Heartbeat] Ping failed: %s\n", http.errorToString(httpCode).c_str());
  }

  http.end();

  // Subtle simulated battery decrement
  if (batteryLevel > 15 && random(0, 5) == 0) {
    batteryLevel--;
  }
}

void sendIncidentEvent(const char* eventType, const char* severity) {
  if (WiFi.status() != WL_CONNECTED) return;

  HTTPClient http;
  String url = String(SERVER_HOST) + "/api/events";

  http.begin(url);
  http.addHeader("Content-Type", "application/json");

  // Add random GPS jitter for spatial clustering
  float jitterLat = NODE_LAT + ((random(-30, 30)) / 10000.0);
  float jitterLon = NODE_LON + ((random(-30, 30)) / 10000.0);

  StaticJsonDocument<256> doc;
  doc["node_id"]    = NODE_ID;
  doc["event_type"] = eventType;
  doc["zone_id"]    = NODE_ZONE;
  doc["latitude"]   = jitterLat;
  doc["longitude"]  = jitterLon;
  doc["severity"]   = severity;

  String requestBody;
  serializeJson(doc, requestBody);

  int httpCode = http.POST(requestBody);

  if (httpCode == 200 || httpCode == 201) {
    Serial.printf("[Event] Dispatched event to CRIMENET-X: HTTP %d\n", httpCode);
  } else {
    Serial.printf("[Event] Transmission error: HTTP %d (%s)\n", httpCode, http.errorToString(httpCode).c_str());
  }

  http.end();
}
