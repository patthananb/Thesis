# Thesis Writing Outline & Guidelines

**Title:** Low-Cost IT/OT Convergence Testbed for Industrial IoT Monitoring
**Author:** Patthanan B. (patthanan.bh@gmail.com)
**Institution:** King Mongkut's University of Technology North Bangkok (KMUTNB)
**Department:** Electrical and Computer Engineering, Faculty of Engineering
**Degree:** Bachelor of Electrical Engineering
**Language:** English (primary), Thai (translation after English draft complete)
**Template reference:** `Thesis paper/THESIS_TEMPLATE_GUIDE.md`
**Source draft:** `senior_project_draft_concise.md`

---

## Front Matter

- [ ] Cover page (EN + TH) — title ≤ 4 lines, author names + student IDs, academic year
- [ ] Approval Certificate — advisor, chairperson, 2× committee members
- [ ] Abstract — **<200 words**, mini-IMRAD structure, 4–5 keywords
- [ ] Acknowledgements
- [ ] Table of Contents *(auto-generated in Word, update with Ctrl-A → F9)*
- [ ] List of Figures *(auto-generated)*
- [ ] List of Tables *(auto-generated)*
- [ ] Nomenclature — Modbus, MQTT, TIG stack symbols, Purdue level labels

---

## Chapter 1 — Introduction

> **Goal:** Convince the reader the problem is real, hard, and worth solving. Follow the 5-paragraph formula.

- [ ] 1.1 Background and Motivation
  - Industry 4.0 and IT/OT convergence demand
  - Legacy OT protocols (Modbus RTU, RS-485) — no auth, serial-only
  - Cost barrier to retrofitting legacy field hardware
- [ ] 1.2 Problem Statement *(5-question formula)*
  1. What is the problem? — OT and IT protocols are incompatible; legacy hardware cannot be replaced
  2. Why is it important? — Industry 4.0 requires real-time OT data in IT dashboards
  3. Why is it hard? — Protocol mismatch, no open benchmark for ESP32 Modbus libraries, security trade-offs
  4. Why hasn't it been solved? — Existing solutions are proprietary or expensive; no empirical ESP32 library comparison exists
  5. What is this work's contribution? — Low-cost testbed + library evaluation + Node-RED vs Telegraf comparison + security demonstration
- [ ] 1.3 Objectives
  1. Build a low-cost IT/OT convergence testbed (MCU + SBC + PLC)
  2. Evaluate 10 open-source ESP32 Modbus TCP gateway libraries empirically
  3. Compare Node-RED vs Telegraf as MQTT-to-InfluxDB pipelines
  4. Demonstrate and discuss IT/OT security gaps
- [ ] 1.4 Scope and Limitations
  - In-scope: Modbus RTU/TCP, MQTT, TIG stack, Cloudflare Tunnel, passive sniffer
  - Out-of-scope: OPC-UA, industrial certification, ATEX environments, production deployment
- [ ] 1.5 Thesis Organization — one paragraph describing each chapter

---

## Chapter 2 — Background and Related Work

> **Goal:** Give the reader just enough theory to understand the design choices. End with a clear research gap.

- [ ] 2.1 IT/OT Convergence and the Purdue Reference Model (ISA-95, Levels 0–4)
- [ ] 2.2 Industrial Communication Protocols
  - 2.2.1 Modbus RTU — serial, RS-485, frame structure, function codes (FC01/02/03/04/05/06)
  - 2.2.2 Modbus TCP — MBAP header, port 502, same FCs over TCP
  - 2.2.3 MQTT — publish/subscribe, QoS 0/1/2, retain, LWT, broker role
- [ ] 2.3 Edge Devices in IIoT
  - 2.3.1 Microcontrollers (ESP32-S3 — FreeRTOS, Wi-Fi, UART, flash/RAM constraints)
  - 2.3.2 Single-Board Computers (Raspberry Pi 4 — Linux, Docker, full IP stack)
  - 2.3.3 Programmable Logic Controllers (Siemens LOGO! 8 — IEC 61131-3, deterministic scan, industrial I/O)
- [ ] 2.4 Time-Series Monitoring Stack
  - Telegraf (agent, input/output plugins), InfluxDB 2 (bucket, Flux query), Grafana (dashboards, data sources)
- [ ] 2.5 Containerisation with Docker Compose — pinned tags, `.env` secrets, `${VAR:?}` guard
- [ ] 2.6 Security Challenges in IT/OT Environments — Modbus has no auth, MQTT anonymous by default, Purdue zone collapse risks
- [ ] 2.7 Related Work and Research Gap — cite prior ESP32 IIoT papers, identify missing empirical library benchmark

---

## Chapter 3 — System Design

> **Goal:** Show the architecture before the implementation details. All design decisions justified here.

- [ ] 3.1 Overall Architecture
  - Purdue-level mapping table (L0 field → L1 PLC → L2 gateway → L3 site → L3.5 remote)
  - Two data paths (Path A: direct Modbus TCP; Path B: RS-485 → MQTT → InfluxDB)
- [ ] 3.2 Hardware Selection and Justification
  - 3.2.1 Siemens LOGO! 8 — why chosen (Modbus TCP native, IEC 61131-3, real industrial I/O, cost ~$150–300)
  - 3.2.2 Waveshare ESP32-S3-Relay-6CH — why chosen (built-in RS-485, relay outputs, $15, PlatformIO support)
  - 3.2.3 Raspberry Pi 4 — why chosen (Docker, Linux, Ethernet, 4 GB RAM, $55)
  - 3.2.4 Field instruments — XY-MD02 (temp/humidity, Modbus RTU), SDM120 (power meter, 8 IEEE-754 floats)
- [ ] 3.3 Network Topology — LAN diagram, IP assignments, port table (502, 1883, 8086, 3000, 9001)
- [ ] 3.4 Data Flow Design
  - 3.4.1 Path A — PLC Modbus TCP slave → any LAN host polls FC03/FC01
  - 3.4.2 Path B — ESP32-S3 polls RTU slaves → publishes MQTT JSON → Telegraf → InfluxDB
  - 3.4.3 Reverse path — LOGO! as Modbus TCP master reads ESP32-S3 HR0–HR1
- [ ] 3.5 Security Architecture — implemented (Cloudflare Tunnel + Access) vs planned (VLAN, MQTT auth, TLS)

---

## Chapter 4 — Implementation

> **Goal:** Reproducible detail. Someone should be able to rebuild the testbed from this chapter.

- [ ] 4.1 OT Layer: Siemens LOGO! 8
  - 4.1.1 Ladder Diagram programs
    - Pump start/stop with self-latch + runtime counter → `VW0`
    - Analog threshold alarm — compares scaled `AI1` vs Modbus-writable setpoint in `VW0`, drives `Q2`, increments `VW2`
  - 4.1.2 Modbus address map (FC01 → `Q*/VQ*`; FC02 → `I*`; FC03/FC06 → `VW*`; FC04 → `AI*/AM*`)
  - 4.1.3 LOGO! as Modbus TCP master — reads ESP32-S3 `HR0` (temp), `HR1` (humidity) into V-memory
  - 4.1.4 LOGO! built-in web HMI vs Grafana dashboard comparison
- [ ] 4.2 Edge Gateway: ESP32-S3 Firmware
  - 4.2.1 Hand-rolled RTU master (~80 lines, CRC-16, unified status codes, exception-frame recognition)
  - 4.2.2 MQTT publisher — QoS 1, topic `sensors/esp32/data`, JSON schema, status codes (value fields omitted on device error)
  - 4.2.3 Modbus TCP slave — `emelianov/modbus-esp8266`, HR0–HR20 (weather scaled integers + SDM120 float pairs)
  - 4.2.4 Cooperative non-blocking loop — 2-second cycle, no `delay()`, services TCP slave + MQTT + RTU + watchdog concurrently
  - 4.2.5 Resource usage: **Flash 946 KB / 1310 KB (72.2%)**, **RAM 48.5 KB / 327.6 KB (14.8%)**
- [ ] 4.3 IT Layer: Containerised TIG + MQTT Stack
  - 4.3.1 Mosquitto 2.0 — anonymous `:1883`, WebSockets `:9001`, Docker log rotation
  - 4.3.2 InfluxDB 2.7 — bucket `sensors`, org `weatherstation`, `${TOKEN:?}` in Compose
  - 4.3.3 Telegraf 1.28 — `inputs.mqtt_consumer` (QoS 1, JSON), Pi host metrics (`cpu`, `mem`, `disk`, `system`, CPU temp), 5-min ping to 1.1.1.1, 5-min `internet_speed`
  - 4.3.4 Grafana 13.0.1 — four dashboards: Temperature & Humidity, SDM120 Power, Pi Telemetry, Networking; anonymous Viewer for kiosk
  - 4.3.5 Cloudflare Tunnel + Access — outbound tunnel, no open router port; gates only Grafana
  - 4.3.6 Kiosk display — Pi OS Lite + `xserver-xorg` + `openbox` + `chromium --kiosk` on 7" touchscreen, auto-login → `startx` → Grafana playlist
- [ ] 4.4 IoT-Sniffer Tool
  - Passive pcap decoder, recognises Modbus TCP (Protocol ID `0x0000`, port `:502`) and MQTT (control-packet structure)
  - Use cases: verify wire byte order, confirm `mbpoll` FC05 appears as plaintext, surface unexpected MQTT publishers
  - Repo: `github.com/patthananb/IoT-sniffer`

---

## Chapter 5 — Experimental Studies

> **Goal:** Empirical, reproducible results. Tables and figures carry most of the weight here.

### Study A — Modbus TCP Gateway Library Evaluation

- [ ] 5.1.1 Scope — 10 libraries evaluated; ESPHome excluded (config-only, out of scope)
  - Rob2011, vwetter, zivillian, harihanv, tobiasfaust/SolaxModbusGateway, eModbus/eModbus, NamNamIoT, maxx-ukoo/esp32-modbus-tcp2rtu, espressif/esp-modbus, emelianov/modbus-esp8266
- [ ] 5.1.2 Evaluation criteria (10 dimensions)
  - Repository activity, popularity, framework support, network interface, Modbus protocol features, software architecture, dependencies, build system, documentation, deployment features
- [ ] 5.1.3 Bench setup
  - Hardware: ESP32-S3-DevKitC-1 + MAX3485 RS-485 transceiver
  - Host: pymodbus 3.x playing TCP client + RTU slave simultaneously
  - One JSON metrics file per PlatformIO environment; Excel scorecard
- [ ] 5.1.4 Metrics
  - Build-time: flash bytes, RAM bytes, build time, warning count
  - Runtime: free heap, min heap, task stack high-water, boot-to-ready time
  - Host-side: latency (mean/p50/p95/p99/max) for FC03 × 10, 100, 125 registers; throughput at 10/50/100 req/s; max concurrent clients at <1% error; stress pass rate (bad CRC, slow slave, slave-off, Wi-Fi drop)
- [ ] 5.1.5 Results — scorecard table, latency box plots, throughput curves
- [ ] 5.1.6 Recommendation — `emelianov/modbus-esp8266` for production (TCP slave + auto-reconnect + multi-client, small footprint); `eModbus/eModbus` for async FreeRTOS-task-based use cases

### Study B — Node-RED vs Telegraf as MQTT Subscriber

- [ ] 5.2.1 Setup — same broker (`sensors/esp32/data`), same InfluxDB bucket, parallel pipelines running simultaneously
  - Telegraf: `inputs.mqtt_consumer` + `outputs.influxdb_v2`
  - Node-RED: `mqtt in` → `json` → function (field rename/scale) → `influxdb out`
- [ ] 5.2.2 Metrics — idle memory (`docker stats` 5-min avg), end-to-end latency (mean + p99, 1000 msgs), throughput ceiling (1000 msg/s burst 60 s, count drops), transformation CPU, failure recovery (broker off 30 s → count lost + time-to-first-write)
- [ ] 5.2.3 Results — comparison table
- [ ] 5.2.4 Recommendation — Telegraf wins on memory, latency, throughput, Git operability; Node-RED wins on visual debugging, complex transforms, prototyping speed; **complementary, not interchangeable**

### Security Demonstration

- [ ] 5.3.1 Unauthenticated Modbus TCP actuation
  ```bash
  mbpoll -a 1 -t 0 -r 0 -1 192.168.1.100 1    # FC05 → physical relay closes
  ```
- [ ] 5.3.2 Anonymous MQTT snoop/spoof — any LAN host can publish/subscribe without credentials
- [ ] 5.3.3 IoT-sniffer capture — plaintext FC05 frame visible on wire, MQTT payload unencrypted
- [ ] 5.3.4 Mitigations — implemented: Cloudflare Tunnel (Grafana only); planned: MQTT auth (`allow_anonymous false`), TLS `:8883`, VLAN OT/IT segregation, firewall port 502, VPN for remote Modbus

---

## Chapter 6 — Discussion

> **Goal:** Synthesise findings, not repeat results. Honest about limitations.

- [ ] 6.1 MCU vs SBC vs PLC — Roles and Fit

| Criterion | ESP32-S3 (MCU) | Raspberry Pi 4 (SBC) | Siemens LOGO! 8 (PLC) |
|---|---|---|---|
| OS / runtime | Arduino / FreeRTOS | Linux | Proprietary |
| Determinism | High (cooperative loop) | Low (Linux scheduler) | High (deterministic scan) |
| Programming | C++ (Arduino) | Python / Node.js / Docker | LAD / FBD (IEC 61131-3) |
| I/O | GPIO + RS-485 + Wi-Fi | GPIO (limited) + Ethernet | 24 VDC, 0–10 V, 4–20 mA, relays |
| Cost (USD) | ~$15 | ~$55 | ~$150–300 |
| Power | <1 W | ~5 W | ~3 W |
| Industrial cert. | None | None | CE / UL / ATEX |
| Role in testbed | Edge protocol gateway (Path B) | Site data plane | Field controller (Path A) |

  **Key point:** Three classes, three correct Purdue layers — complementary, not competing.

- [ ] 6.2 Testbed as a Teaching Platform — demonstrates real protocol stacks, real security gaps, real industrial signals
- [ ] 6.3 Protocol Conversion as a Configuration Choice — once OT and IT share a protocol, data-flow direction is software config, not architecture
- [ ] 6.4 Limitations
  - Single-site testbed; not validated in multi-site or noisy RF environments
  - No industrial certification on MCU/SBC
  - Library evaluation on one hardware revision; results may shift on newer ESP32 revisions
  - Security mitigations only partially implemented

---

## Chapter 7 — Conclusion and Future Work

- [ ] 7.1 Conclusions *(one paragraph per objective)*
  1. A $15 MCU bridges Modbus RTU → Modbus TCP + MQTT from one cooperative loop (72.2% flash, 14.8% RAM)
  2. `emelianov/modbus-esp8266` is the production library choice; `eModbus/eModbus` is best for async use
  3. Telegraf and Node-RED are complementary pipeline tools, not interchangeable
  4. Modbus TCP and anonymous MQTT are real, exploitable LAN-local gaps — demonstrated live
- [ ] 7.2 Future Work
  - MQTT authentication (password file + firmware credentials) and LWT
  - TLS on MQTT `:8883`, InfluxDB, and Grafana
  - VLAN segregation between OT and IT; firewall port 502
  - Firmware ring buffer for telemetry replay during Wi-Fi outage
  - Firmware OTA update mechanism
  - Scheduled InfluxDB backups + Docker `healthcheck` + resource limits
  - OPC-UA as a more secure OT protocol alternative
  - Grafana threshold alerting and file-based dashboard provisioning

---

## Back Matter

- [ ] References — IEEE format, target ~30–50 citations
- [ ] Biography — author background
- [ ] Appendix A — ESP32-S3 key firmware listings (RTU master, MQTT publisher, Modbus TCP slave init)
- [ ] Appendix B — Docker Compose file and Telegraf config
- [ ] Appendix C — Library evaluation full scorecard table
- [ ] Appendix D — IoT-sniffer sample capture output

---

## Writing Checklist (apply to every section before marking done)

- [ ] No first-person pronouns (I/we/my → "this work", "the proposed system", "the authors")
- [ ] Sentences short and precise; avoid stacked noun phrases
- [ ] Technical terms consistent throughout (e.g., always "Modbus TCP" not "ModbusTCP")
- [ ] Every figure referenced in text **before** it appears; caption **below** figure
- [ ] Every table referenced in text **before** it appears; caption **above** table
- [ ] Every equation in borderless 2-column table, numbered `(X.Y)`, referenced as "Equation (X.Y)"
- [ ] All citations in IEEE format `[N]`; all references cited in body text
- [ ] Abstract: mini-IMRAD, <200 words, 4–5 keywords

---

## Writing Order (recommended)

1. Chapter 3 (System Design) — forces you to commit to all architecture decisions
2. Chapter 4 (Implementation) — detail while memory is fresh
3. Chapter 5 (Experiments) — write results as you run them
4. Chapter 2 (Background) — now you know exactly what theory to explain
5. Chapter 1 (Introduction) — write last so contribution statement matches actual results
6. Chapter 6 (Discussion) — synthesise after all results are written
7. Chapter 7 (Conclusion) — last
8. Abstract — very last (after everything else is locked)
9. Front matter — auto-generate TOC/figures/tables in Word

---

*Source repositories: [Lab_network_monitoring](https://github.com/patthananb/Lab_network_monitoring) · [IoT-sniffer](https://github.com/patthananb/IoT-sniffer)*
