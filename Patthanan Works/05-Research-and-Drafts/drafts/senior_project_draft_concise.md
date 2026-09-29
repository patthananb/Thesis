# Senior Project — Concise Draft: Low-Cost IT/OT Convergence Testbed

**Advisor Draft — v0.3-concise**
**Author:** Patthanan B.
**Date:** May 2026
**Repositories:** [Lab_network_monitoring](https://github.com/patthananb/Lab_network_monitoring), [IoT-sniffer](https://github.com/patthananb/IoT-sniffer)

---

**TL;DR.** A low-cost, fully self-hosted IT/OT convergence testbed integrating three edge-device classes — a Waveshare ESP32-S3 microcontroller, a Raspberry Pi 4 single-board computer, and a Siemens LOGO! 8 PLC — into one open-source industrial IoT monitoring stack. The OT side comprises the LOGO! 8 (physical I/O exposed as a Modbus TCP slave) and two RS-485 Modbus RTU instruments (XY-MD02 sensor, Eastron SDM120 power meter). The ESP32-S3 acts as a Modbus RTU → Modbus TCP + MQTT gateway. The IT side runs Mosquitto, Telegraf, InfluxDB 2, and Grafana under Docker Compose on the Pi 4, with a Cloudflare Tunnel for authenticated remote access and a 7" touchscreen kiosk for the lab display. Two engineering studies accompany the testbed: a ten-project evaluation of open-source ESP32 Modbus TCP gateway libraries, and an empirical Node-RED vs Telegraf comparison. A passive companion tool, the IoT-sniffer, decodes Modbus TCP and MQTT traffic on the wire to make the protocol-level security gaps visible.

---

## 1. Motivation

OT historically uses deterministic serial protocols (Modbus RTU, PROFIBUS, HART) with no authentication; IT uses IP-based, packet-switched protocols (MQTT, HTTP). Industry 4.0 requires that the two domains interoperate without forklift-replacing legacy field hardware. This project answers four concrete questions: (i) can a low-cost MCU credibly bridge Modbus RTU into Modbus TCP and MQTT, (ii) which open-source ESP32 Modbus TCP library is best for that role, (iii) is Node-RED or Telegraf the better MQTT consumer for an InfluxDB pipeline, and (iv) how do MCUs, SBCs, and PLCs compare as IIoT edge nodes?

## 2. System Architecture

Mapped onto the ISA-95 / Purdue model:

| Purdue Level | Component |
|---|---|
| L0 Physical | Pushbuttons, indicators, relays, 4–20 mA sensors on LOGO! I/O; XY-MD02 + SDM120 on the RS-485 bus |
| L1 Control | Siemens LOGO! 8, Ladder Diagram, Modbus TCP slave on `:502` |
| L2 Gateway | Waveshare ESP32-S3: RTU master + TCP slave + MQTT publisher |
| L3 Site | Pi 4 running Mosquitto, Telegraf, InfluxDB 2, Grafana (Docker Compose) |
| L3.5 Remote | Cloudflare Tunnel + Cloudflare Access in front of Grafana |

Two data paths are preserved:
- **Path A — direct Modbus TCP** from any LAN host (or the Pi) to the LOGO!.
- **Path B — RS-485 → ESP32-S3 → MQTT → Telegraf → InfluxDB**.

Both paths converge in Grafana. The IoT-sniffer observes both from a tap on the LAN.

## 3. Hardware / Software Inventory

| Layer | Hardware | Software |
|---|---|---|
| Field (OT L0/L1) | LOGO! 8 PLC; XY-MD02; SDM120; pushbuttons; LED/relay; 4–20 mA sensor + 500 Ω shunt | LOGO! Soft Comfort (LAD/FBD); LOGO! firmware ≥ V8.3 with Modbus TCP |
| Edge gateway (L2) | Waveshare ESP32-S3-Relay-6CH | PlatformIO + Arduino core; `256dpi/MQTT`, `emelianov/modbus-esp8266`; hand-rolled RTU master |
| Site (IT L3) | Raspberry Pi 4 | Docker Compose: Mosquitto 2.0, Telegraf 1.28, InfluxDB 2.7, Grafana 13.0.1, cloudflared 2026.3.0 |
| Comparison path | Pi 4 | Node-RED 3.x + `node-red-contrib-influxdb` |
| Display | Pi 4 + Official 7" Touchscreen (800×480) | Raspberry Pi OS Lite + Openbox + Chromium kiosk |
| Audit | Any Linux host | IoT-sniffer (Python, libpcap) |
| Library bench | ESP32-S3-DevKitC-1 + MAX3485 + USB-RS-485 dongle | Custom PlatformIO workspace + Python `pymodbus` host harness |

## 4. OT Layer: Siemens LOGO! 8

The LOGO! 8 is the OT representative because it is programmable in IEC 61131-3 Ladder Diagram, supports Modbus TCP natively (firmware ≥ V8.3), and accepts real industrial signal types (24 VDC digital, 0–10 V analog, 4–20 mA via 500 Ω shunt).

**Wired field devices (representative):** `I1` start pushbutton, `I2` stop pushbutton (NC), `I3` interlock (NC), `Q1` motor/pump output, `Q2` indicator lamp, `AI1` 4–20 mA sensor, `AQ1` 0–10 V output.

**Ladder programs.** (a) Pump start/stop with self-latch and runtime counter — classic OT teaching example, increments a non-volatile counter in V-memory on every `Q1` rise so the IT side can read uptime via Modbus. (b) Analog threshold alarm — compares scaled `AI1` against a Modbus-writable setpoint in `VW0`, drives `Q2` and increments `VW2` on alarm, giving a SCADA-style supervisory-write round-trip the testbed can demonstrate.

**Modbus address mapping** is fixed by Siemens: FC01 → `Q*`/`VQ*` coils; FC02 → `I*` discrete inputs; FC03/FC06 → `VW*` holding registers; FC04 → `AI*`/`AM*` input registers.

**Manipulation with `mbpoll`** demonstrates three categories:

```bash
mbpoll -a 1 -t 4 -r 0 -c 10 192.168.1.100         # read VW block (process state)
mbpoll -a 1 -t 0 -r 0 -1 192.168.1.100 1          # force Q1 ON (physical actuation)
mbpoll -a 1 -t 4 -r 9999 -c 1 192.168.1.100       # out-of-range probe (FC exception 0x02)
```

The actuation case is the most pedagogically valuable: with only the PLC's IP address, a laptop drives a physical output. This is the entry point for the security discussion in §9.

**LOGO! as Modbus TCP master.** Firmware ≥ V8.3 also lets the LOGO! act as a client. It is configured here to read `HR0` (temperature) and `HR1` (humidity) from the ESP32-S3 and copy them into V-memory — making the LOGO! itself an OT consumer of MCU sensor data, and closing the data flow in the reverse direction.

**LOGO! built-in web HMI vs Grafana.** Both render the same process variables but represent two tooling cultures: an OT-flavoured fixed operator panel and an IT-flavoured queryable time-series dashboard.

## 5. Edge Gateway: ESP32-S3 Weather + Power Station

The Waveshare ESP32-S3-Relay-6CH polls two RS-485 slaves at 9600 baud, 8N1, on UART1 (`TX = GPIO17`, `RX = GPIO18`):

- **XY-MD02** at address `0x01` — temperature + humidity, FC04 from `0x0001` × 2 registers.
- **Eastron SDM120** at address `0x02` — eight IEEE-754 floats (V, I, W, VA, VAr, PF, Hz, kWh) across pairs of input registers.

Firmware: C++ on PlatformIO with Arduino core. Libraries: `256dpi/MQTT@^2.5.1` (QoS 1 — `PubSubClient` is QoS 0 only and silently drops messages on Wi-Fi hiccups) and `emelianov/modbus-esp8266@^4.1.0` (Modbus TCP slave only). The RTU master is hand-rolled (~80 lines, CRC-16 by hand, unified status codes, exception-frame recognition) for precise control over blocking behaviour. The main `loop()` is cooperative and non-blocking, servicing the TCP slave, the MQTT client, the watchdogs, and the RTU poll cycle without ever stalling any role.

Each 2-second cycle produces:

- **MQTT JSON** on topic `sensors/esp32/data` at QoS 1, retained = false, with per-device status codes and value fields (status is always present; value fields are omitted on a device error).
- **Modbus TCP slave** on port 502 (mDNS `esp32s3-weather.local`), holding registers `HR0..HR20`: weather as scaled integers, SDM120 as IEEE-754 float pairs.

Resource usage on target: **Flash 946 KB / 1310 KB (72.2%)**, **RAM 48.5 KB / 327.6 KB (14.8%)**.

## 6. IT Layer: Containerised TIG + MQTT Stack

All services run on the Pi 4 under Docker Compose with pinned image tags and `.env`-driven secrets. The Compose file uses `${VAR:?error}` for required values so the stack refuses to start with empty credentials.

- **Mosquitto 2.0** — anonymous listener on `:1883`, WebSockets on `:9001`, stdout logging with Docker rotation.
- **InfluxDB 2.7** — initialised with bucket `sensors`, organisation `weatherstation`, token from `.env`.
- **Telegraf 1.28** — `inputs.mqtt_consumer` (QoS 1, JSON, measurement `weather`); Pi host telemetry (`cpu`, `mem`, `system`, `disk`, file-based CPU temp); 5-minute `inputs.ping` to `1.1.1.1`; 5-minute `inputs.internet_speed`.
- **Grafana 13.0.1** — dashboards for Temperature & Humidity, SDM120 Power, Pi Telemetry, Networking; anonymous Viewer access toggleable for kiosk use.
- **cloudflared 2026.3.0** — gated behind a `tunnel` Compose profile. With it on, the Pi establishes an outbound tunnel; Cloudflare Access enforces auth in front of Grafana. No inbound port is opened on the router.

**Kiosk display.** A second Pi 4 + Official 7" Touchscreen runs Raspberry Pi OS Lite with `xserver-xorg`, `xinit`, `openbox`, `chromium`, `unclutter`. Auto-login on TTY1 triggers `startx`; Openbox autostart disables screen blanking and launches Chromium directly into a Grafana playlist in `--kiosk` mode.

## 7. Modbus TCP Gateway Library Evaluation

Ten open-source ESP32 Modbus TCP gateway projects evaluated under one PlatformIO workspace (nine in-scope; ESPHome out of scope): Rob2011, vwetter, zivillian, harihanv, tobiasfaust/SolaxModbusGateway, eModbus/eModbus, NamNamIoT, maxx-ukoo/esp32-modbus-tcp2rtu, espressif/esp-modbus.

**Criteria (ten heads):** repository activity, popularity, framework support, network interface, Modbus protocol features, software architecture, dependencies, build system, documentation, practical deployment features.

**Bench setup.** Single ESP32-S3-DevKitC-1 board with MAX3485 RS-485 transceiver. Host PC plays both TCP client and RTU slave (`pymodbus` 3.x). One JSON metrics file per environment; Excel scorecard rolls up across all envs.

**Metrics captured.** Build-time: flash bytes / RAM bytes / build time / warnings. Runtime: free heap, min heap, task stack high-water, boot-to-ready. Host-side: latency (mean / p50 / p95 / p99 / max) for FC03 × 10, 100, 125 regs; throughput at 10, 50, 100 req/s; max concurrent clients at < 1% error; stress pass count (bad CRC, slow slave, slave-off, Wi-Fi drop).

**Headline result.** The production firmware uses `emelianov/modbus-esp8266` for its Modbus TCP slave: maintained, supports slave role with auto-reconnect and multi-client TCP, small in flash and RAM, combines cleanly with the hand-rolled RTU master in one `loop()`. **`eModbus/eModbus`** is the strongest alternative where async, FreeRTOS-task-based communication is required. Full evaluation: `Documentation/docs/modbus_lib_eval_2026-05-11.pdf`.

## 8. Node-RED vs Telegraf as MQTT Subscribers

Both subscribe to the same `sensors/esp32/data` topic on the same broker and write to the same InfluxDB bucket. Telegraf uses `inputs.mqtt_consumer` + `outputs.influxdb_v2`; Node-RED uses `mqtt in` + `json` + function (field rename / scale) + `influxdb out`.

**Axes measured.** Idle memory (`docker stats` 5-min average), end-to-end latency (mean and p99 across 1 000 messages), throughput ceiling (1 000 msg/s burst for 60 s, count drops), transformation CPU cost, failure recovery (kill broker for 30 s, count lost samples and time to first write after recovery), visual debugging, operability under source control, learning curve.

**Expected findings.** Telegraf wins on memory (~20–40 MB, Go), latency (no V8 event loop), throughput under load, and operability under source control. Node-RED wins on visual debugging, complex transformation logic, and prototyping speed. They are **complementary**, not interchangeable: Telegraf for the production pipeline, Node-RED for flow-based prototyping. Both run in parallel during the comparison study so the numbers are directly comparable.

## 9. Security Observation

**Modbus TCP carries no credentials.** Demonstrated live with `mbpoll -a 1 -t 0 -r 0 -1 192.168.1.100 1` — the motor relay clicks, the indicator lamp lights, nothing on the wire is encrypted or authenticated.

**MQTT is anonymous by default in this configuration.** Any host on the LAN can both spoof and snoop telemetry. The Cloudflare Tunnel only exposes Grafana, not Mosquitto, so the broker is unreachable from the public internet — but LAN-local threats remain.

**The IoT-sniffer** ([IoT-sniffer repo](https://github.com/patthananb/IoT-sniffer)) is a passive, purpose-built decoder run alongside the testbed. It recognises Modbus TCP by the fixed Protocol ID `0x0000` and port `:502`, recognises MQTT by its control-packet structure, and prints decoded transactions human-readably. In the testbed it confirms that `mbpoll` actuation appears on the wire as a plaintext FC05 frame, verifies the wire byte order of ESP32-S3 RTU requests against the documented register encoding, and surfaces any unexpected MQTT publisher.

**Mitigations** (partially implemented): VLAN segregation between OT and IT segments; MQTT authentication (`allow_anonymous false` + password file + firmware credential support); TLS termination on MQTT `:8883`, InfluxDB, and Grafana even on the LAN; VPN tunnel for any remote Modbus query. Cloudflare Tunnel + Access in front of Grafana is the only mitigation currently active and gates only the visualization layer.

## 10. MCU vs SBC vs PLC Comparison

| Criterion | ESP32-S3 (MCU) | Raspberry Pi 4 (SBC) | Siemens LOGO! 8 (PLC) |
|---|---|---|---|
| OS / runtime | Arduino / FreeRTOS | Linux | Proprietary |
| Determinism | High (cooperative loop) | Low (Linux scheduler) | High (deterministic scan) |
| Programming | C++ (Arduino) | Anything (Python, Node.js, Docker) | LAD / FBD (IEC 61131-3) |
| I/O | GPIO + RS-485 + Wi-Fi | GPIO (limited) + USB + Ethernet | 24 VDC, 0–10 V, 4–20 mA, relays |
| Cost (USD) | ~15 | ~55 | ~150–300 |
| Power | <1 W | ~5 W | ~3 W |
| Industrial cert. | None | None | CE / UL / ATEX (model-dependent) |
| Environmental | Bare PCB, IP20 | Bare PCB, IP20 | DIN-rail, industrial temp |
| Lifecycle | Short (consumer SoC) | Medium | Long (10+ years vendor support) |
| Role in this project | Edge protocol gateway (Path B) | Site-level data plane | Field controller (Path A) |

**Conclusion.** Three classes, three correct layers, exchanging data over open protocols — **complementary, not competing**. IT/OT convergence is "each device in its right place," not "one device replacing the others."

## 11. Integration Summary

Two data paths from OT to IT, both converging in Grafana:

- **Path A.** Any LAN host (or the Pi) polls the LOGO! directly over Modbus TCP. OT-native; no custom firmware required.
- **Path B.** ESP32-S3 polls the RS-485 instruments, publishes JSON over MQTT, Telegraf writes into InfluxDB. IT-native; demonstrates the protocol-conversion role of the edge gateway.

The LOGO!'s ability to act as a Modbus TCP master (reading from the ESP32-S3 register window) closes the loop in the reverse direction. The IoT-sniffer observes all paths from a LAN tap. Together, the configuration shows that once OT and IT share a common protocol, the data-flow direction is a configuration choice rather than an architectural constraint.

## 12. Conclusions and Future Work

**Conclusions.** A $15 MCU can credibly bridge Modbus RTU into Modbus TCP and MQTT from one cooperative loop, using 72.2% flash and 14.8% RAM. A Raspberry Pi 4 hosts a complete, pinned, environment-driven TIG + MQTT stack with Cloudflare Tunnel for authenticated remote access. The library evaluation is reproducible and points to `emelianov/modbus-esp8266` as the production choice, with `eModbus/eModbus` as the strongest async alternative. Telegraf and Node-RED are complementary, not interchangeable. The three device classes (MCU, SBC, PLC) correctly occupy distinct Purdue levels. Modbus TCP and anonymous MQTT are real, exploitable LAN-local gaps, demonstrated live with `mbpoll` and the IoT-sniffer.

**Future work.** Enable MQTT authentication and LWT; add a firmware ring buffer for telemetry replay; implement firmware OTA; add scheduled InfluxDB backups; add Docker `healthcheck:` blocks and resource limits; terminate TLS on MQTT / InfluxDB / Grafana; VLAN-segregate OT from IT and firewall port 502; evaluate OPC-UA as a more secure alternative; add Grafana threshold alerting and file-based dashboard provisioning.

---

*Prepared as a concise discussion draft for academic advisor review; a longer companion draft (v0.3) and the source repositories cover the full detail.*
