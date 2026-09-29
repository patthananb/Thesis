# Senior Project Todo List
**Project:** Low-Cost Industrial IoT Laboratory Platform
**Hardware:** Siemens LOGO! 8.4 | WT32-ETH01 (ESP32) | Raspberry Pi | Samkoon HMI
**Deadline:** ~2026-05-31 (2 months)

---

## Phase 1 — Raspberry Pi Gateway Setup (Week 1–2)

- [ ] Flash Raspberry Pi OS (or Ubuntu) on RPi
- [ ] Install Docker + Docker Compose on RPi
- [ ] Deploy **Eclipse Mosquitto** (MQTT broker) in Docker
- [ ] Deploy **Node-RED** in Docker (with persistent volume)
- [ ] Deploy **InfluxDB** in Docker
- [ ] Deploy **Grafana** in Docker
- [ ] Test all services talk to each other on local network
- [ ] Assign static IPs to all devices (RPi, LOGO!, ESP32, HMI)

---

## Phase 2 — LOGO! 8.4 PLC Setup (Week 2–3)

- [ ] Install LOGO! Soft Comfort on your PC
- [ ] Write a basic control program (FBD or Ladder) — e.g. start/stop pump, I/O with panel
- [ ] Configure LOGO! IP address and enable Modbus TCP **slave** mode
- [ ] Configure LOGO! MQTT client (LOGO! 8.4 has native MQTT — configure topics for I/O)
- [ ] Test Node-RED reads LOGO! registers via `node-red-contrib-modbus`
- [ ] Test Node-RED writes to LOGO! coils via Modbus TCP (Node-RED as **master**)
- [ ] Configure LOGO! as Modbus **master** (reads from ESP32 slave registers)

---

## Phase 3 — ESP32 (WT32-ETH01) Firmware (Week 2–4)

- [ ] Set up Arduino IDE or PlatformIO for WT32-ETH01
- [ ] Get Ethernet working (WT32-ETH01 uses LAN8720 built-in — no extra module needed)
- [ ] Implement **Modbus TCP slave** on ESP32 (use `ModbusTCP` library)
- [ ] Implement **Modbus TCP master** on ESP32 (reads from LOGO! or another slave)
- [ ] Implement **MQTT client** on ESP32 (publish sensor data, subscribe to commands)
- [ ] Interface sensors/actuators via I/O panel (digital inputs/outputs, analog if needed)
- [ ] Test LOGO! reading ESP32 registers (LOGO! master → ESP32 slave)
- [ ] Test ESP32 reading LOGO! registers (ESP32 master → LOGO! slave)

---

## Phase 4 — Node-RED Flows (Week 3–4)

- [ ] Install palette: `node-red-contrib-modbus`
- [ ] Install palette: `node-red-dashboard` or `@flowfuse/node-red-dashboard`
- [ ] Install palette: `node-red-contrib-influxdb`
- [ ] Build flow: Modbus TCP master → poll LOGO! registers → publish to MQTT
- [ ] Build flow: MQTT subscribe → write to InfluxDB
- [ ] Build flow: MQTT subscribe → Node-RED dashboard UI (gauges, charts, buttons)
- [ ] Build flow: dashboard button → write Modbus register → control PLC output

---

## Phase 5 — Grafana Dashboards (Week 4–5)

- [ ] Connect Grafana to InfluxDB as data source
- [ ] Create dashboard for PLC I/O status (digital inputs/outputs as stat panels)
- [ ] Create time-series charts for sensor readings
- [ ] Add alert rules (e.g. tank level too high/low)

---

## Phase 6 — Samkoon HMI Integration (Week 4–5)

- [ ] Confirm Samkoon HMI communication protocol (likely Modbus TCP — check manual early!)
- [ ] Configure HMI to connect to LOGO! or Node-RED as Modbus TCP server
- [ ] Design HMI screens: start/stop, status indicators, analog values
- [ ] Test HMI reading live data from LOGO!

---

## Phase 7 — Demo Application: Water Tank Level Control (Week 5–6)

- [ ] Level sensor input → LOGO! analog input (or ESP32)
- [ ] LOGO! controls pump relay output (pump ON when low, OFF when high)
- [ ] All data flows: sensor → MQTT → InfluxDB → Grafana
- [ ] HMI shows tank level + pump status
- [ ] Demonstrate LOGO! as **slave** (Node-RED reads it)
- [ ] Demonstrate LOGO! as **master** (LOGO! reads ESP32 registers)

---

## Phase 8 — Testing & Documentation (Week 7–8)

- [ ] Test Modbus TCP latency (Node-RED → LOGO!, LOGO! → ESP32)
- [ ] Test MQTT message rate and reliability
- [ ] Run system continuously for stability test (24h)
- [ ] Compare PLC vs ESP32 response time for same control logic
- [ ] Write final report

---

## Professor's 4 Required Deliverables

| # | Requirement | Status |
|---|-------------|--------|
| 1 | PLC (LOGO! 8.4) as Modbus TCP slave AND master through Node-RED | ⬜ Not started |
| 2 | ESP32 (WT32-ETH01) as Modbus TCP master/slave | ⬜ Not started |
| 3 | Visualize on Grafana | ⬜ Not started |
| 4 | Visualize on Samkoon HMI | ⬜ Not started |

---

## Risk Assessment

| Item | Risk |
|------|------|
| LOGO! 8.4 Modbus TCP slave | Low — well documented |
| LOGO! 8.4 as Modbus master (reading ESP32) | Medium — less documented |
| WT32-ETH01 Ethernet bring-up | Low — LAN8720 built-in, no extra module |
| Samkoon HMI protocol support | **Medium-High — confirm Week 1** |
| All 4 subsystems integrated | Medium |

> **Start Phase 1 and 2 in parallel this week.**
> Get LOGO! + Node-RED + MQTT talking first — that is the backbone everything else connects to.
> Confirm Samkoon HMI supports Modbus TCP as early as possible.
