# Thesis Defense Presentation Plan
**Title:** Design and Implementation of IT/OT Integration in IIoT Applications  
**Student:** Patthanan Bhandhumanee  
**Institution:** KMUTNB  

---

## 1. Timeline

| Phase | Duration | Notes |
|-------|----------|-------|
| Opening + Introduction | 3 min | Slide 1–3 |
| Background & Theory | 5 min | Slide 4–7 |
| System Design | 6 min | Slide 8–12 |
| Results & Discussion | 7 min | Slide 13–17 |
| Conclusion & Future Work | 2 min | Slide 18–19 |
| Live Demo | 5 min | Optional — confirm with committee |
| Q&A | 10 min | — |
| **Total** | **~38 min** | |

> Adjust if committee gives a strict time limit (typically 20–30 min presentation + Q&A at KMUTNB).

---

## 2. Slide Outline

### Slide 1 — Title Slide
- Thesis title, student name, advisor name, degree, date
- Department / Faculty / KMUTNB logo

### Slide 2 — Problem Statement
**Talking points:**
- OT devices (PLC, sensors) speak Modbus; IT systems speak HTTP/MQTT/JSON — no native bridge
- Industrial data trapped in isolated OT networks → no real-time dashboards, no analytics
- Security gap: unauthenticated Modbus TCP allows arbitrary register writes (FC05 coil actuation)

### Slide 3 — Objectives
- Design and implement an IT/OT integration stack for an IIoT testbed
- Evaluate Modbus TCP gateway libraries on ESP32-S3
- Benchmark Node-RED vs Telegraf for MQTT→InfluxDB ingestion
- Identify security vulnerabilities in the deployed stack

### Slide 4 — System Architecture Overview
**Visual:** Purdue/ISA-95 level diagram  
`XY-MD02 sensor (L0) → ESP32-S3 gateway (L1) → LOGO! 8.4 PLC (L2) → Raspberry Pi 4 TIG stack (L3/L4)`  
**Talking points:**
- IT/OT boundary at ESP32-S3: speaks Modbus RTU southbound, Modbus TCP + MQTT northbound
- Each layer maps to a Purdue model level

### Slide 5 — Protocol Stack: Modbus
**Visual:** ADU frame diagram (Address | FC | Data | CRC)  
**Talking points:**
- RS-485 differential signalling: V_diff = V_A − V_B, threshold ±200 mV
- RTU timing: 3.5-character silent gap between frames at 9600 baud = 3.6 ms
- TCP encapsulation: 6-byte MBAP header (Transaction ID, Protocol ID, Length, Unit ID) wraps PDU
- FC03 holding registers (LOGO!), FC04 input registers (XY-MD02)

### Slide 6 — Protocol Stack: MQTT
**Visual:** Pub/Sub topology diagram (ESP32-S3 → Mosquitto → Telegraf/Grafana)  
**Talking points:**
- Pub/Sub decouples producers from consumers — ESP32-S3 publishes without knowing who subscribes
- QoS 1 chosen: at-least-once delivery with PUBACK handshake; QoS 2 overhead unnecessary at 2 s intervals
- LWT: `sensors/esp32/status = offline` auto-published by broker on ungraceful disconnect
- Ports: 1883 plaintext (internal LAN), 9001 WebSocket; 8883 TLS deferred to future work

### Slide 7 — TIG Stack
**Visual:** Docker Compose dependency graph  
`Mosquitto → Telegraf → InfluxDB ← Grafana`  
**Talking points:**
- All services in Docker Compose with pinned image tags and health checks
- InfluxDB line protocol: `measurement[,tags] fields timestamp_ns`
- Flux query for downsampled 1-hour mean; Grafana 4 dashboards

### Slide 8 — Hardware Components
**Visual:** Photo of full testbed / wiring diagram  
| Component | Role | Interface |
|-----------|------|-----------|
| Waveshare ESP32-S3 Relay 6CH | Edge gateway | RS-485, Wi-Fi |
| XY-MD02 | Temp + humidity sensor | Modbus RTU |
| Siemens LOGO! 8.4 | PLC logic controller | Modbus TCP |
| Raspberry Pi 4 | IT server (TIG stack) | Ethernet |
| SDM120 | Power meter | Modbus RTU |

### Slide 9 — ESP32-S3 Firmware Design
**Visual:** Cooperative `loop()` flowchart  
**Talking points:**
- PlatformIO + Arduino core; no RTOS — cooperative scheduling by function timing
- Three concurrent roles: RTU master (FC04 → XY-MD02), MQTT publisher (256dpi/MQTT v2.5.1), Modbus TCP slave (emelianov/modbus-esp8266 v4.1.0)
- Flash 72.2%, RAM 14.8% — headroom for OTA future addition

### Slide 10 — LOGO! 8.4 PLC Integration
**Visual:** LAD logic screenshot + Modbus TCP register map  
**Talking points:**
- LOGO! acts as both Modbus TCP server (ESP32-S3 reads V-memory HR0–HR9) and client (writes set-points back)
- V-memory address mapping: VM0 → HR0, etc.
- Ladder logic: IF (temp > threshold) THEN relay coil Q1 ON

### Slide 11 — Study A: Library Evaluation (Modbus TCP Gateway)
**Visual:** Scorecard table (9 libraries × 5 criteria)  
**Criteria:** Modbus TCP slave support, FC coverage, concurrent connections, documentation quality, active maintenance  
**Result:** emelianov/modbus-esp8266 recommended — only library meeting all 5 criteria  
**Talking points:**
- 9 libraries evaluated; ESPHome excluded (config-file only, no library API)
- 4 libraries eliminated in round 1 (no TCP slave mode)

### Slide 12 — Study B: Node-RED vs Telegraf
**Visual:** Latency box-plot comparison  
**Talking points:**
- Metric: end-to-end MQTT → InfluxDB write latency over 1000 messages
- Telegraf: lower median latency, lower jitter — stateless Go binary vs Node.js event loop
- Node-RED eliminated; Telegraf adopted for production stack

### Slide 13 — Study C: Security Findings
**Visual:** IoT-sniffer terminal screenshot  
**Talking points:**
- Modbus TCP has zero authentication — any host on LAN can send FC05 to actuate LOGO! relay
- MQTT anonymous mode — any client can publish to any topic (spoofed `sensors/esp32/data`)
- IoT-sniffer tool: passive Python/libpcap decoder that fingerprints Modbus TCP frames without injecting traffic
- Mitigations recommended: MQTT ACL + password file, VLAN segmentation, VPN gateway

### Slide 14 — Key Results Summary

| Study | Outcome |
|-------|---------|
| A — Library eval | emelianov recommended; 8/9 libraries had gaps |
| B — Broker comparison | Telegraf 23% lower median latency vs Node-RED |
| C — Security audit | 2 unauthenticated attack vectors documented |
| System | End-to-end pipeline: sensor → PLC → MQTT → InfluxDB → Grafana working at 2 s intervals |

### Slide 15 — Conclusion
- Demonstrated full IT/OT integration across Purdue L0–L4 using commodity hardware (<฿5,000 total BOM)
- Systematic protocol selection (Modbus RTU for OT polling, MQTT pub/sub for IT distribution)
- Identified and documented two security vulnerabilities with practical mitigation paths

### Slide 16 — Future Work
- **Security:** MQTT TLS (port 8883), mutual client certificates, VLAN segmentation
- **Firmware:** NVS ring buffer for telemetry replay during Wi-Fi outages; OTA update
- **Protocol:** OPC-UA as an authenticated alternative OT protocol (open62541)
- **Scale:** Multi-site InfluxDB federation via remote_write

### Slide 17 — Q&A / Thank You
- Contact, GitHub repo link, acknowledgements

---

## 3. Talking Points & Script Notes

### Opening hook (30 s)
> "In a typical factory, a sensor reading a temperature has existed for decades — but that number has never left the OT network. This project builds the bridge."

### Transition: Background → System
> "Now that we understand why the gap exists, let me walk through exactly how we closed it."

### Transition: System → Results
> "The system is built. Let's look at whether it performs and what vulnerabilities we uncovered."

### Closing
> "The full pipeline runs end-to-end on a ฿5,000 testbed. The security findings highlight that IT/OT integration without access control creates new attack surfaces — and the mitigations are well-understood and implementable."

---

## 4. Live Demo Script (if allowed)

**Duration:** ~5 minutes

1. **Show Grafana dashboard** — live temperature + humidity from XY-MD02 (2 s refresh)
2. **Trigger LOGO! relay manually** via Soft Comfort → show relay status update in Grafana within one polling cycle
3. **Run IoT-sniffer** in terminal — show passive Modbus TCP frame decode without touching the device
4. **Show unauthenticated MQTT** — `mosquitto_pub -t sensors/esp32/data -m '{"temp":99}'` → show spoofed value appear in Grafana briefly

> **Risk note:** Steps 3–4 are security demos. Confirm with advisor whether to include or keep to simulation screenshots.

---

## 5. Anticipated Q&A

| Question | Suggested Answer |
|----------|-----------------|
| Why not use OPC-UA instead of Modbus? | OPC-UA has built-in security (PKI, sessions) but LOGO! 8.4 only supports Modbus TCP; OPC-UA is listed as future work |
| Why Telegraf over Node-RED? | Study B benchmark: 23% lower median latency and stateless architecture eliminates flow state drift |
| How is Modbus TCP secure in production? | It isn't — this is a known limitation documented in Section 4.3; mitigation requires VLAN isolation + VPN |
| Why QoS 1 and not QoS 2? | At 2 s publish interval, duplicate delivery (QoS 1 edge case) is harmless; QoS 2 four-packet handshake adds 2× RTT with no benefit |
| Can this scale to more devices? | Yes — Mosquitto supports thousands of concurrent clients; InfluxDB 2 remote_write enables multi-site federation (Section 5.2) |
| Why cooperative scheduling on ESP32-S3 instead of FreeRTOS tasks? | Simpler reasoning about timing, no mutex needed for shared register array, sufficient at 2 s cycle; FreeRTOS considered overkill for this payload |
| What is the latency from sensor to Grafana? | Modbus RTU poll (500 ms) + MQTT publish (<5 ms) + Telegraf batch (1 s default) + InfluxDB write + Grafana refresh = ~3–4 s end-to-end |

---

## 6. Preparation Checklist

- [ ] Convert slide outline to actual slides (PowerPoint / Beamer)
- [ ] Export system architecture diagram as high-res image
- [ ] Export Grafana dashboard as screenshot (or live if demo allowed)
- [ ] Print or prepare library scorecard table
- [ ] Run full end-to-end system test 1 day before defense
- [ ] Practice full run-through (target: under 30 min without Q&A)
- [ ] Prepare printed 1-page system overview as handout for committee
- [ ] Confirm with advisor: demo allowed yes/no, time limit, number of committee members

---

*Last updated: 2026-06-10*
