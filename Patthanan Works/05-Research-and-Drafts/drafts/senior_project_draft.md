# Senior Project Draft: Low-Cost IT/OT Convergence Testbed for Industrial IoT

**Advisor Draft — v0.3**
**Author:** Patthanan B.
**Date:** May 2026
**Primary repositories:**
- https://github.com/patthananb/Lab_network_monitoring (ESP32-S3 weather/power station + TIG stack)
- https://github.com/patthananb/IoT-sniffer (passive Modbus TCP + MQTT capture tool)

---

**TL;DR.** This project builds a low-cost, fully self-hosted **IT/OT convergence testbed** that demonstrates how three classes of edge devices — a microcontroller (ESP32-S3), a single-board computer (Raspberry Pi 4), and a programmable logic controller (Siemens LOGO! 8) — can be integrated into one open-source industrial IoT monitoring stack. The OT side is represented by the LOGO! 8 PLC (exposing physical I/O as a Modbus TCP slave) and by two RS-485 Modbus RTU instruments (an XY-MD02 temperature/humidity sensor and an Eastron SDM120 single-phase power meter). The ESP32-S3 acts as a Modbus RTU → Modbus TCP + MQTT gateway. The IT side runs on the Raspberry Pi 4 as a Docker Compose stack — Mosquitto, Telegraf, InfluxDB 2, Grafana — with a Cloudflare Tunnel for authenticated remote access and a 7" touchscreen kiosk for the lab display. Two engineering studies accompany the testbed: a structured evaluation of ten open-source ESP32 Modbus TCP gateway libraries, and an empirical comparison of Node-RED and Telegraf as MQTT subscribers feeding InfluxDB. A separate companion tool, the **IoT-sniffer**, passively captures and decodes Modbus TCP and MQTT traffic on the wire to make the (lack of) protocol-level security visible. Taken together, the work maps the components onto the ISA-95 / Purdue Enterprise Reference Architecture and gives a concrete, measurable answer to the question of how legacy OT field hardware and modern IT analytics tooling can be made to coexist on a single trusted LAN.

---

## 1. Introduction and Motivation

### 1.1 The IT/OT Divide

Industrial control historically separates two domains. **Operational Technology (OT)** is the hardware and software that directly monitors and controls physical processes — PLCs, sensors, actuators, fieldbus networks. **Information Technology (IT)** is the general-purpose computing layer used for analytics, dashboards, alerting, and enterprise integration. The two have traditionally been designed against very different requirements:

- OT prioritises **determinism, long lifecycles, electrical robustness, and certified safety**, and standardised early on serial protocols such as Modbus RTU, PROFIBUS, and HART. These protocols are simple, predictable, and lacking any notion of authentication or encryption.
- IT prioritises **flexibility, scalability, and rapid evolution**, using IP-based packet-switched networks and modern application protocols such as TCP/IP, HTTP, and MQTT.

Industry 4.0 demands that these two worlds talk to each other: OT must supply real-time process data into the IT analytics plane, and IT must increasingly issue supervisory commands back to the field. The challenge is doing so without forklift-replacing the existing OT installed base.

### 1.2 Project Goal

This project builds an end-to-end testbed that bridges OT and IT using only **off-the-shelf, open-source, low-cost components**. The testbed answers four concrete questions:

1. Can a low-cost MCU (a Waveshare ESP32-S3) act as a Modbus RTU → Modbus TCP + MQTT protocol converter, bridging legacy serial field devices into a modern IT monitoring stack while remaining functional, stable, and resource-frugal?
2. Among the available open-source ESP32 Modbus TCP gateway libraries, which one is best suited to that role, and on what evidence?
3. Among the available open-source MQTT consumers, is Node-RED or Telegraf the better choice for feeding a time-series database in production, and on what evidence?
4. How do the three device classes used in this project (MCU, SBC, PLC) compare as IIoT edge nodes, and what is each one's correct role in the converged architecture?

### 1.3 Scope and Deliverables

The deliverables that make up this project are:

- A working ESP32-S3 firmware that polls two RS-485 Modbus RTU instruments and republishes the data as both MQTT JSON (QoS 1) and a Modbus TCP slave (committed at `Lab_network_monitoring/`).
- A working IT stack on a Raspberry Pi 4: Mosquitto, Telegraf, InfluxDB 2, Grafana, plus a `cloudflared` service gated behind a Docker Compose profile.
- A LOGO! 8 PLC programmed in Ladder Diagram (LAD) and configured as a Modbus TCP slave; verified manipulable via `mbpoll` from any LAN host.
- A 7" touchscreen kiosk built on Raspberry Pi OS Lite + Openbox + Chromium, displaying a Grafana playlist full-screen.
- A structured evaluation of ten open-source ESP32 Modbus TCP gateway libraries against build-time, runtime, protocol-feature, and maintenance criteria.
- An empirical comparison of Node-RED and Telegraf subscribed to the same MQTT topic, measured against latency, memory, throughput, and reliability axes.
- A passive **IoT-sniffer** tool used to capture and decode the Modbus TCP and MQTT traffic that flows through the testbed.

---

## 2. System Architecture

The testbed organises the components along the ISA-95 / Purdue Enterprise Reference Architecture so each device class has an unambiguous role:

| Purdue Level | Description | Implementation in this project |
|---|---|---|
| Level 0 | Physical process | Field devices: pushbuttons, relays/indicators, 4–20 mA sensors wired into LOGO! I/O; XY-MD02 and SDM120 on the RS-485 bus |
| Level 1 | Basic control | Siemens LOGO! 8 PLC running Ladder Diagram, exposing I/O as a Modbus TCP slave |
| Level 2 | Supervisory / gateway | Waveshare ESP32-S3 acting as a Modbus RTU master + Modbus TCP slave + MQTT publisher |
| Level 3 | Site operations | Raspberry Pi 4 running Mosquitto, Telegraf, InfluxDB 2, Grafana, optional cloudflared |
| Level 3.5 | Remote access | Cloudflare Tunnel + Cloudflare Access in front of Grafana |

```
+---------------------------------------------------------------------------+
| OT Layer                                                                  |
|                                                                           |
|   Field devices    -- wired I/O --->  Siemens LOGO! 8 PLC                |
|   (pushbuttons,                       (LAD program,                       |
|    indicators,                         Modbus TCP slave, port 502)        |
|    4-20 mA sensors)                                                       |
|                                                                           |
|   XY-MD02 sensor   -- RS-485 ----+                                       |
|                                  |                                       |
|   Eastron SDM120  -- RS-485 -----+---->  Waveshare ESP32-S3              |
|                                          - Modbus RTU master              |
|                                          - Modbus TCP slave (port 502)    |
|                                          - MQTT publisher (QoS 1)         |
+----------------------+--------------------------+-------------------------+
                       |                          |
                       | Modbus TCP               | MQTT (port 1883)
                       v                          v
+---------------------------------------------------------------------------+
| IT Layer (Raspberry Pi 4)                                                 |
|                                                                           |
|   Mosquitto -----+-------------+                                          |
|                  |             |                                          |
|                  v             v                                          |
|             Telegraf       Node-RED                                       |
|             (TIG path)     (comparison path)                              |
|                  \             /                                          |
|                   \           /                                           |
|                    v         v                                            |
|                     InfluxDB 2 ---> Grafana ---> [kiosk display]          |
|                                          \                                |
|                                           \--> Cloudflare Tunnel          |
|                                                (optional, profile-gated)  |
+---------------------------------------------------------------------------+

       +-------------------------------------------------------+
       | IoT-sniffer (separate tool, passive)                  |
       | listens on the LAN segment, decodes Modbus TCP + MQTT |
       +-------------------------------------------------------+
```

There are deliberately **two paths from OT to IT**:

- **Path A — Modbus TCP.** Any IT-side client (a PC, the Raspberry Pi, or another ESP32) can read the LOGO!'s register window directly. This is the OT-native path and is intentionally retained so the testbed shows the same data via the protocol the OT layer was designed around.
- **Path B — MQTT/JSON.** The ESP32-S3 polls the RS-485 instruments and publishes one combined JSON message per cycle to Mosquitto. Telegraf consumes it and writes it into InfluxDB. This is the IT-native path.

Both paths converge in Grafana, giving a unified view of OT field data in an IT dashboard. The IoT-sniffer observes both paths from a tap point on the LAN.

---

## 3. Hardware and Software Inventory

A single master inventory clarifies what physically exists in the testbed and which stack runs where.

| Layer | Hardware | Software / firmware |
|---|---|---|
| Field (OT, L0/L1) | Siemens LOGO! 8 PLC; XY-MD02 temperature/humidity sensor; Eastron SDM120 single-phase power meter; pushbuttons; indicator LEDs / relays; 4–20 mA sensor with 500 Ω shunt | LOGO! Soft Comfort (Ladder Diagram and Function Block Diagram); LOGO! firmware ≥ V8.3 with Modbus TCP enabled |
| Edge gateway (L2) | Waveshare ESP32-S3-Relay-6CH board; on-board RS-485 transceiver | PlatformIO + Arduino core firmware (`firmware_platformio/`); libraries `256dpi/MQTT@^2.5.1` and `emelianov/modbus-esp8266@^4.1.0`; hand-rolled RTU master |
| Site (IT, L3) | Raspberry Pi 4 (4 GB) running Raspberry Pi OS 64-bit | Docker Compose stack: Mosquitto 2.0, Telegraf 1.28, InfluxDB 2.7, Grafana 13.0.1, cloudflared 2026.3.0 |
| Site (IT, comparison path) | Same Raspberry Pi 4 | Node-RED 3.x with `node-red-contrib-influxdb` |
| Display | Raspberry Pi 4 + Official 7" Touchscreen (800×480) | Raspberry Pi OS Lite + `xserver-xorg`, `xinit`, `openbox`, `chromium`, `unclutter` |
| Audit tool | Any Linux host on the LAN segment (PC or Raspberry Pi) | IoT-sniffer (Python, libpcap) |
| Bench rig (library eval only) | ESP32-S3-DevKitC-1 + MAX3485 RS-485 transceiver + USB↔RS-485 dongle | Custom PlatformIO workspace with nine envs; Python host harness driving `pymodbus` 3.x |

The split is intentional: the OT layer is a small, fixed set of field-grade hardware; the IT layer is a single Pi running pinned, containerised services that can be reproduced by `git clone` and `docker compose up -d`.

---

## 4. OT Layer: Siemens LOGO! 8 PLC

### 4.1 Why the LOGO! 8

The Siemens LOGO! 8 is a low-cost programmable logic controller targeted at small automation tasks. Three properties make it the right OT representative for this testbed:

- It is **programmable in Ladder Diagram (LAD) and Function Block Diagram (FBD)**, the same IEC 61131-3 languages used on full-size industrial PLCs, so the OT side of the demo is methodologically authentic and not toy-grade.
- Firmware ≥ V8.3 includes a **native Modbus TCP server on port 502**, so no add-on module is required to talk to the IT layer.
- It accepts **real industrial signal types** (24 VDC digital, 0–10 V analog, 4–20 mA via a 500 Ω shunt), giving an honest example of OT signal conditioning.

### 4.2 Physical I/O — Field Device Wiring

Field devices in this testbed are wired directly to the LOGO!'s terminal block, not connected over a network:

| LOGO! Address | Wired field device | Purpose in the demo |
|---|---|---|
| `I1` | Start pushbutton (Normally Open) | Manual start command for the simulated process |
| `I2` | Stop pushbutton (Normally Closed) | Manual stop / interlock |
| `I3` | Limit / safety switch (Normally Closed) | Process safety interlock |
| `Q1` | Motor / pump output (relay) | Driven output the operator can see |
| `Q2` | Indicator lamp / LED | Status of the simulated process |
| `AI1` | 4–20 mA sensor via 500 Ω shunt → 2–10 V | Continuous analog process variable |
| `AQ1` | 0–10 V analog output | Setpoint or proportional output |

These wirings give the testbed a believable OT story: a "process" with both discrete and continuous variables, manual controls, and a safety interlock.

### 4.3 Ladder Logic Examples

Two LAD programs are written in LOGO! Soft Comfort to give the testbed observable behaviour:

**Program A — Pump start/stop with self-latch and runtime counter.**

```
Network 1 — Manual start / stop with self-latch:

     I1 (Start)    I2 (Stop, NC)    I3 (Interlock, NC)    Q1 (Motor)
  ---[ ]----------[ / ]------------[ / ]------------------( )---
        |
     Q1 (Self-latch)
  ---[ ]------------------------------------------------------
```

Network 2 increments a non-volatile counter (LOGO! "C" block) every time `Q1` rises, giving a runtime statistic the IT side can read over Modbus.

**Program B — Analog threshold alarm.**

The 4–20 mA input scaled to engineering units (using the LOGO! "AI scale" block) is compared against a Modbus-writable setpoint stored in `VW0`. When the input exceeds the setpoint, `Q2` (the indicator lamp) turns on and the alarm count in `VW2` increments. This makes the SCADA-style "supervisory write a setpoint → field controller acts on it" round-trip directly observable.

### 4.4 LOGO! Modbus Address Mapping

The LOGO! 8's memory map is fixed by Siemens and translates as follows into Modbus register types:

| Modbus FC | Modbus address type | LOGO! memory area | Access |
|---|---|---|---|
| FC 01 — Read Coils | Coil (0x) | `Q1..Q20`, `VQ1..VQ16` | Read/Write |
| FC 02 — Read Discrete Inputs | Discrete Input (1x) | `I1..I24` | Read Only |
| FC 03 — Read Holding Registers | Holding Register (4x) | `VW0..VW850` (V-memory words) | Read/Write |
| FC 04 — Read Input Registers | Input Register (3x) | `AI1..AI8`, `AM1..AM6` (analog inputs) | Read Only |
| FC 05 — Force Single Coil | Coil (0x) | `Q1..Q20` | Write |
| FC 06 — Preset Single Register | Holding Register (4x) | `VW0..VW850` | Write |

The setpoint and counter variables used by the LAD programs are mapped into VW (V-memory word) so they appear naturally as Modbus holding registers; the discrete I/O appears in the coil and discrete-input ranges; the 4–20 mA analog input appears as a 16-bit input register.

### 4.5 Manipulating the PLC with `mbpoll`

`mbpoll` is a command-line Modbus master utility used to validate the PLC register map without writing custom client code. Three categories of operation are demonstrated:

**Read** the current process state:
```bash
# Read 10 V-memory words (holding registers) starting at VW0
mbpoll -a 1 -t 4 -r 0 -c 10 192.168.1.100

# Read Q1..Q8 (motor / lamp output coils)
mbpoll -a 1 -t 0 -r 0 -c 8 192.168.1.100

# Read I1..I8 (pushbutton / limit-switch inputs)
mbpoll -a 1 -t 1 -r 0 -c 8 192.168.1.100

# Read AI1 (the 4-20 mA analog input)
mbpoll -a 1 -t 3 -r 0 -c 1 192.168.1.100
```

**Actuate** the PLC's outputs over the wire — turning a physical output on and off without touching the panel:
```bash
# Force Q1 (the motor relay) ON
mbpoll -a 1 -t 0 -r 0 -1 192.168.1.100 1

# Write 750 into VW0 (the alarm setpoint used by Program B)
mbpoll -a 1 -t 4 -r 0 -1 192.168.1.100 750
```

**Probe** the device's protocol behaviour — for example, requesting an out-of-range register:
```bash
mbpoll -a 1 -t 4 -r 9999 -c 1 192.168.1.100   # expects Modbus exception 0x02
```

The actuation case is the most pedagogically valuable: with only the PLC's IP address and slave ID, a laptop on the same network can drive a physical output. This is then re-used in §9 as the entry point for the security discussion.

### 4.6 LOGO! as Both Modbus TCP Slave and Master

Firmware ≥ V8.3 also lets the LOGO! act as a **Modbus TCP master** (client). In this testbed, the LOGO! is configured to read selected holding registers from the ESP32-S3 gateway (`HR0` temperature, `HR1` humidity) and to copy them into V-memory. This makes the LOGO! itself an OT consumer of MCU-sourced sensor data — the **reverse** of the usual data flow — and demonstrates that, once both devices speak Modbus TCP, the direction of the data flow is a configuration choice rather than an architectural constraint.

### 4.7 LOGO! Built-in Web Server vs Grafana

The LOGO! 8 ships with a built-in HTTP HMI page that mirrors the panel display. This is shown in the project alongside the Grafana dashboards for the same process variables — directly contrasting an **OT-flavoured operator UI** (small, fixed, control-room-style) against an **IT-flavoured analytics UI** (large, queryable, time-series-style). This single comparison concretely shows what each layer's tooling is good at.

---

## 5. Edge Gateway: ESP32-S3 Weather + Power Station

The ESP32-S3 is the linchpin of the testbed — the device where the OT and IT halves physically meet.

### 5.1 Hardware

The board is a **Waveshare ESP32-S3-Relay-6CH** with an on-board RS-485 transceiver. RS-485 is wired on UART1 with `TX = GPIO17`, `RX = GPIO18`, running half-duplex at 9600 baud, 8N1. Two slaves share the bus:

| Slave | Address | Protocol details |
|---|---|---|
| XY-MD02 temperature + humidity sensor | `0x01` | FC04 from `0x0001`, quantity 2 (temperature ×10, humidity ×10) |
| Eastron SDM120 single-phase power meter | `0x02` | FC04, eight IEEE-754 float values across pairs of input registers (voltage, current, active power, apparent power, reactive power, power factor, frequency, total active energy) |

### 5.2 Firmware Architecture

Firmware is written in C++ on PlatformIO with the Arduino core; the build environment is `waveshare_esp32s3_relay` (board `esp32s3box`, PSRAM enabled). Two third-party libraries are used:

- `256dpi/MQTT@^2.5.1` — for **QoS 1** publishes (the more common `PubSubClient` is QoS 0 only, which means lost messages are not retransmitted and the time-series database loses samples silently).
- `emelianov/modbus-esp8266@^4.1.0` — used **only for its Modbus TCP slave** (`ModbusIP`). The RTU master is hand-rolled.

The hand-rolled RTU master (~80 lines of C++ in `modbus_rtu.cpp`) builds an 8-byte FC03/FC04 request, computes the CRC-16 by hand, writes the frame on UART1, and reads the response back with bounded timeouts. It returns a unified status code (`OK`, `TIMEOUT`, `CRC_ERROR`, `EXCEPTION`, `BAD_RESPONSE`), and it recognises the 5-byte Modbus exception response separately from a generic timeout. The reason for hand-rolling it is precise control over blocking behaviour inside the same `loop()` that has to also drive `mb.task()` (the TCP slave) and `mqttClient.loop()`.

The main loop is **cooperative and non-blocking**:

```cpp
void loop() {
    mb.task();                  // service Modbus TCP slave clients
    mqttClient.loop();          // service MQTT keep-alive / inbound
    handleNetworkWatchdogs();   // rate-limited WiFi / MQTT reconnect
    handleSensorPolling();      // poll RTU slaves every 2 s
}
```

No FreeRTOS task plumbing is needed; reconnects perform at most one attempt per call and are rate-limited so none of the three roles can starve the others.

### 5.3 Outputs

Each poll cycle (2 s) produces two parallel representations of the same data:

**MQTT JSON**, topic `sensors/esp32/data`, QoS 1, retained = false:

```json
{
  "status": 0,
  "poll_count": 1234,
  "temperature": 24.9,
  "humidity": 48.6,
  "power_status": 0,
  "power_voltage": 229.4,
  "power_current": 0.418,
  "power_watts": 74.6,
  "power_apparent_va": 77.5,
  "power_reactive_var": 12.0,
  "power_factor": 0.963,
  "power_frequency": 50.0,
  "power_energy_kwh": 12.348
}
```

If a device errors out, only its value fields are omitted; its `status` field is always present, so downstream alerts can detect "weather OK, SDM120 timing out" unambiguously.

**Modbus TCP slave** on port 502, mDNS hostname `esp32s3-weather.local`, holding registers `HR0..HR20`:

| HR | Field | Encoding |
|---|---|---|
| 0 | Temperature | int16, raw × 0.1 °C |
| 1 | Humidity | uint16, raw × 0.1 %RH |
| 2 | Weather status | uint16 (0–4) |
| 3 | Poll count | uint16, rolls over at 65535 |
| 4 | SDM120 status | uint16 (0–4) |
| 5–6 | Voltage | IEEE-754 float, high word first |
| 7–8 | Current | IEEE-754 float, high word first |
| 9–10 | Active Power | IEEE-754 float, high word first |
| 11–12 | Apparent Power | IEEE-754 float, high word first |
| 13–14 | Reactive Power | IEEE-754 float, high word first |
| 15–16 | Power Factor | IEEE-754 float, high word first |
| 17–18 | Frequency | IEEE-754 float, high word first |
| 19–20 | Total Active Energy | IEEE-754 float, high word first |

### 5.4 Resource Usage on Target

Build environment: PlatformIO Release, `waveshare_esp32s3_relay`, PSRAM enabled.

| Segment | Used | Total | % |
|---|---|---|---|
| Flash | 946 KB | 1310 KB | 72.2 |
| RAM | 48.5 KB | 327.6 KB | 14.8 |

This leaves enough flash headroom for an OTA partition scheme and very large RAM headroom for a buffering ring during MQTT outages (both deferred to future work).

---

## 6. IT Layer: Containerised TIG + MQTT Stack

The IT stack runs on the Raspberry Pi 4 under Docker Compose. All credentials, organisation, bucket name, and admin token are sourced from a gitignored `.env`; image tags are pinned in the Compose file:

| Service | Image | Tag |
|---|---|---|
| Mosquitto | `eclipse-mosquitto` | `2.0` |
| InfluxDB | `influxdb` | `2.7` |
| Telegraf | `telegraf` | `1.28` |
| Grafana | `grafana/grafana` | `13.0.1` |
| cloudflared | `cloudflare/cloudflared` | `2026.3.0` |

Pinning avoids `:latest` drift between development and deployment.

**Mosquitto** runs an anonymous listener on port 1883 plus WebSockets on 9001, logs to stdout, and Docker rotates the container logs. The anonymous listener is deliberate for the LAN-only configuration; §9 returns to this as a security gap.

**InfluxDB 2** is initialised by the container entrypoint with bucket `sensors`, organisation `weatherstation`, and admin credentials from `.env`. The Compose file uses `${VAR:?error}` so the stack refuses to start when required values are empty — a small but real production-readiness behaviour.

**Telegraf** subscribes to `sensors/esp32/data` at QoS 1 and parses each JSON key into its own field under measurement `weather`. It also collects host telemetry from the Pi (`inputs.cpu`, `inputs.mem`, `inputs.system`, `inputs.disk`, a `[[inputs.file]]` on `/host/sys/class/thermal/thermal_zone0/temp` for Pi CPU temperature), an ICMP `inputs.ping` to `1.1.1.1` every five minutes, and an `inputs.internet_speed` measurement every five minutes.

**Grafana** ships with dashboards for Temperature & Humidity, the SDM120 power meter, Pi host telemetry, and a networking view that combines ping with the speedtest series. Anonymous Viewer access and embedding are toggleable from `.env`, which is what the kiosk display uses.

**Cloudflared** is gated behind a Compose profile (`profiles: ["tunnel"]`), so it does not start unless explicitly enabled. When enabled, the Pi establishes an outbound tunnel to Cloudflare and a Cloudflare Access policy in front of Grafana provides authentication; no inbound port is opened on the home router.

### 6.1 Kiosk Display

A second Raspberry Pi 4 drives the **Official 7" Touchscreen** (800×480) in single-purpose kiosk mode. The OS is Raspberry Pi OS Lite — no desktop — augmented with `xserver-xorg`, `xinit`, `openbox`, `chromium`, and `unclutter`. Auto-login on TTY1 triggers `startx`; Openbox autostart disables screen blanking, hides the cursor, and launches Chromium directly into a Grafana playlist URL in `--kiosk --touch-events=enabled` mode. The kiosk consumes Grafana's anonymous Viewer access, so it does not require a login on boot.

---

## 7. Modbus TCP Gateway Library Evaluation

### 7.1 Motivation

Choosing the right Modbus library for an ESP32 gateway is non-trivial: candidates differ in framework (Arduino vs ESP-IDF), in whether they support TCP, in whether they are blocking or asynchronous, and in whether they are maintained at all. A defensible engineering choice requires evidence, not preference. This part of the project therefore evaluates **ten** open-source ESP32 Modbus TCP gateway projects against a uniform set of criteria.

### 7.2 Projects Evaluated

| # | Project | Class | Framework |
|---|---|---|---|
| 1 | `Rob2011/ESP32.Modbus-TCP-gateway` | App (`.ino`) | Arduino |
| 2 | `vwetter/esp32-modbus-gateway` | App (`.ino`) | Arduino |
| 3 | `zivillian/esp32-modbus-gateway` | PlatformIO project | Arduino + PIO |
| 4 | `harihanv/esp32-modbus-gateway` | App (multi-tab `.ino`) | Arduino |
| 5 | `tobiasfaust/SolaxModbusGateway` | PlatformIO project | Arduino + PIO |
| 6 | `rosenrot00/esphome_modbus_bridge` | ESPHome YAML | (out of scope) |
| 7 | `eModbus/eModbus` | Library | Arduino |
| 8 | `NamNamIoT/ESP32` | App examples | Arduino + emelianov/modbus-esp8266 |
| 9 | `maxx-ukoo/esp32-modbus-tcp2rtu` | IDF project | ESP-IDF |
| 10 | `espressif/esp-modbus` | IDF component | ESP-IDF |

### 7.3 Evaluation Criteria

The criteria are grouped into ten heads (full checklist in `modbus_lib_eval/TODO.md`):

1. Repository maintenance and activity (last commit, total commits, contributor count, issues, PRs).
2. Project popularity (GitHub stars, forks).
3. Framework and platform support (Arduino vs ESP-IDF vs ESPHome; supported variants).
4. Network interface support (Wi-Fi only / Ethernet only / both; Ethernet PHY).
5. Modbus protocol features (TCP master, TCP slave, RTU master, RTU slave, ASCII, bridge mode, function codes, async, non-blocking, multi-client TCP, FreeRTOS task-based comms).
6. Software architecture and implementation (sync vs async, FreeRTOS task usage, modular structure, callback APIs, event-driven, reconnect, watchdog, timeouts, exceptions, CRC).
7. Dependency analysis (external libs, Arduino vs IDF deps, AsyncTCP usage, Wi-Fi/Ethernet/RS-485 libs).
8. Build system and development tools (Arduino IDE / PlatformIO / IDF; CI; tests; examples).
9. Documentation quality (README, API docs, wiring diagrams, examples).
10. Practical deployment features (RS-485 transceiver support, DE/RE control, Wi-Fi reconnect, OTA, static IP).

### 7.4 Bench Setup

A unified PlatformIO workspace contains nine build environments (one per in-scope project; the ESPHome one is excluded). The bench topology uses a single ESP32-S3-DevKitC-1 board as the device under test, an attached MAX3485 RS-485 transceiver, and a host PC that plays **both** the TCP client (driving the bench) and the RTU slave (responding on a USB-RS485 dongle). The host harness is written in Python against `pymodbus` 3.x and writes one JSON metrics file per environment.

### 7.5 Metrics Captured

For every environment, regardless of whether the firmware boots:

- Build-time: flash bytes used / total / %, RAM `.data + .bss` bytes / total / %, build time, compiler warnings, toolchain version.

For functional environments only:

- Runtime: free heap at idle, minimum free heap, TCP-task and RTU-task stack high-water, boot-to-ready time, Wi-Fi connect time.
- Host-side performance: per-FC latency at 10, 100, and 125-register reads (mean, p50, p95, p99, max), achieved throughput at 10 / 50 / 100 req/s, maximum concurrent TCP clients before error rate > 1%, stress / robustness pass count (bad CRC, slow slave, slave-off, Wi-Fi drop).

### 7.6 Result Headline

The full evaluation is captured in `Documentation/docs/modbus_lib_eval_2026-05-11.pdf` and in the per-environment `metrics_*.json` files under `modbus_lib_eval/`. The chosen library for the production ESP32-S3 firmware in `Lab_network_monitoring/` is **`emelianov/modbus-esp8266`** for its Modbus TCP slave, on the grounds that it is actively maintained, supports the slave role with auto-reconnect and multi-client TCP, is small in flash and RAM, and is straightforward to combine with a hand-rolled RTU master in the same `loop()`. **`eModbus/eModbus`** is the strongest alternative and is recommended where asynchronous, FreeRTOS-task-based communication is required.

---

## 8. Node-RED vs Telegraf as MQTT Subscriber

### 8.1 Motivation

Both Node-RED and Telegraf can subscribe to an MQTT topic and write to InfluxDB. Their architectures, however, are very different — Telegraf is a compiled Go agent driven by a TOML configuration file, while Node-RED is a Node.js flow-based runtime driven by a visual editor. The two are often presented as interchangeable; this study tests whether they actually are.

### 8.2 Comparison Setup

Both subscribers run on the same Raspberry Pi 4, against the same Mosquitto broker, consuming the same `sensors/esp32/data` topic, and writing into the same `sensors` bucket in InfluxDB 2.

- Telegraf uses `inputs.mqtt_consumer` (QoS 1, JSON, `name_override = "weather"`) and `outputs.influxdb_v2`.
- Node-RED uses the `mqtt in` node (QoS 1), a `json` parse node, a small function node that renames fields, and the `node-red-contrib-influxdb` `influxdb out` node configured against the same bucket.

### 8.3 Axes Measured

| Axis | How it is measured |
|---|---|
| Architecture style | Plugin pipeline (Go) vs flow runtime (Node.js); descriptive |
| Configuration artefact | TOML vs JSON flow + GUI; descriptive |
| Idle memory | `docker stats` snapshot, 5-minute average |
| End-to-end latency | Timestamp embedded in MQTT payload vs `_time` in InfluxDB; mean and p99 across 1 000 messages |
| Throughput ceiling | Burst publisher at 1 000 msg/s for 60 s; count drops at the InfluxDB side |
| Transformation cost | The same field-rename + scale operation in both; CPU time per message |
| Failure / recovery | Kill Mosquitto, restart 30 s later; count lost samples and time to first write after recovery |
| Visual debugging | Subjective: Node-RED debug nodes vs Telegraf `--test` |
| Operability | Subjective: file-based config vs GUI editor; suitability for source control |
| Learning curve | Time-to-first-message for an engineer unfamiliar with each tool |

### 8.4 Expected Findings (qualitative)

The expected findings, to be confirmed with measurements:

- **Telegraf** wins on memory (Go binary, ~20–40 MB resident), end-to-end latency (no V8 event loop), throughput under load, and operability under source control (single TOML file). It is the right choice for the production data pipeline.
- **Node-RED** wins on visual debugging, ease of complex transformation logic, and prototyping speed. It is the right choice for low-volume, transformation-heavy, evolving flows.

The two are therefore **complementary**, not interchangeable. The testbed runs both in parallel against the same broker for the duration of the comparison study so the measurements are directly comparable.

---

## 9. Security Observation: Unauthenticated Modbus TCP and MQTT

### 9.1 Modbus TCP Has No Authentication

Modbus TCP, in the form deployed on the LOGO! 8 and on the ESP32-S3, **carries no credentials**. Any device on the same network segment can issue an FC03 to read every register and, where the device is configured as a TCP slave that accepts coil writes, can issue an FC05 to force an output. This is **demonstrated live** in the testbed using `mbpoll`:

```bash
mbpoll -a 1 -t 0 -r 0 -1 192.168.1.100 1   # forces Q1 ON
```

The motor relay clicks, the indicator lamp lights, and the operator at the panel sees an unexpected actuation. Nothing on the wire is encrypted; nothing about the request requires authentication.

### 9.2 MQTT Anonymity Is Currently On

`mosquitto.conf` ships with `allow_anonymous true` for the LAN-only configuration. Any host on the Wi-Fi can therefore both spoof telemetry and snoop existing topics. The Cloudflare Tunnel only exposes Grafana, not Mosquitto, so the anonymous broker is not directly reachable from the public internet — but LAN-local threats remain.

### 9.3 The IoT-Sniffer as Audit Tool

The **IoT-sniffer** (`github.com/patthananb/IoT-sniffer`) is a passive packet capture tool developed alongside the testbed. It listens on a specified network interface, recognises Modbus TCP traffic by the fixed `Protocol ID = 0x0000` field in the MBAP header and the `:502` destination port, recognises MQTT traffic by its control-packet structure, and prints decoded transactions in human-readable form. In the testbed, it is used to:

- Confirm that an `mbpoll` write to the LOGO! appears on the wire as a plaintext FC05 frame with no obfuscation — directly visualising the §9.1 finding.
- Verify that the ESP32-S3 issues valid FC03/FC04 requests to the RTU slaves (via the Modbus TCP slave side, observed from any IT host) and that the wire byte order matches the documented register encoding.
- Monitor MQTT topic traffic on Mosquitto and detect any unexpected publisher.

The IoT-sniffer is intentionally **passive**: it never injects packets, never modifies traffic, and requires no configuration on the devices under observation.

### 9.4 Mitigation Strategies

The mitigation strategies — discussed in the project, partially implemented — are:

- **VLAN segregation** between the OT segment and the general IT network, with firewall rules allowing only the designated gateway hosts to talk to Modbus TCP port 502.
- **MQTT authentication** with a Mosquitto password file and `allow_anonymous false`, plus firmware support for `mqttClient.connect(CLIENT_ID, user, pass)`.
- **TLS termination** for MQTT (port 8883), InfluxDB, and Grafana for defence in depth on the LAN.
- **VPN tunnel** for any remote Modbus query, replacing the temptation to expose port 502 directly.

The Cloudflare Tunnel + Cloudflare Access in front of Grafana is the only one of these mitigations currently active and gates remote access to the visualization layer.

---

## 10. Hardware Class Comparison: MCU vs SBC vs PLC for IIoT

The three device classes used in the testbed each fill a distinct role in the IIoT stack. A direct comparison clarifies why the architecture uses all three rather than picking one.

| Criterion | **ESP32-S3 (MCU)** | **Raspberry Pi 4 (SBC)** | **Siemens LOGO! 8 (PLC)** |
|---|---|---|---|
| Operating system / runtime | Bare-metal / FreeRTOS via Arduino core | Linux (Raspberry Pi OS) | Proprietary LOGO! firmware |
| Determinism | High (single cooperative loop) | Low (Linux scheduler) | High (deterministic scan cycle) |
| Programming model | C++ (Arduino) / ESP-IDF | Python, Node.js, Docker, anything | LAD / FBD (IEC 61131-3) |
| Native protocols | MQTT, Modbus TCP, Modbus RTU (via libraries) | Any (full TCP/IP stack) | Modbus TCP, S7, KNX (model-dependent) |
| I/O capability | GPIO + RS-485 + Wi-Fi | GPIO (limited) + USB + Ethernet + Wi-Fi | Industrial 24 VDC digital, 0–10 V / 4–20 mA analog, relay outputs |
| Cost (approx. USD) | ~15 | ~55 | ~150–300 |
| Power consumption | <1 W | ~5 W | ~3 W |
| Industrial certification | None | None | CE, UL, ATEX (model-dependent) |
| Environmental rating | Bare PCB, IP20 | Bare PCB, IP20 | DIN-rail enclosure, industrial temperature range |
| Lifecycle support | Short (consumer-grade SoC) | Medium | Long (10+ years of vendor support) |
| Best IIoT role in this project | Edge protocol gateway (Path B) | Site-level data plane and analytics | Deterministic field controller (Path A) |
| Failure mode in the testbed | One sensor stream interrupted | Whole IT plane interrupted | One physical actuator stuck in last state |

**Key conclusion.** The three device classes are **complementary, not competing**. The PLC takes the deterministic field-control role for which it is certified and designed; the MCU takes the lightweight edge-gateway role where its low cost, low power, and native Wi-Fi matter; the SBC takes the site-level data plane role where a full Linux software stack is required. The IT/OT convergence in this testbed is therefore not "one device replacing the others" but "three devices, each in its correct layer, exchanging data over open protocols."

---

## 11. Integration: How IT and OT Are Actually Joined Here

Bringing §§3–10 together, the project demonstrates the ISA-95 / Purdue model levels 0–3 concretely:

| Level | This project's implementation | Connecting mechanism |
|---|---|---|
| 0 — Physical process | Pushbuttons, indicators, relays, 4–20 mA sensors at the LOGO!; XY-MD02 and SDM120 on the RS-485 bus | Direct wiring / RS-485 |
| 1 — Basic control | LOGO! 8 PLC executing LAD programs (pump start/stop with self-latch; analog threshold alarm) | Modbus TCP slave (port 502) |
| 2 — Supervisory / gateway | ESP32-S3 acting as RTU master + TCP slave + MQTT publisher | MQTT (port 1883) and Modbus TCP (port 502) |
| 3 — Site operations | Mosquitto + Telegraf + InfluxDB + Grafana + Node-RED on the Raspberry Pi 4 | Internal Docker network |
| 3.5 — Remote access | Grafana via Cloudflare Tunnel + Cloudflare Access | Outbound-only, no inbound port |

The **two integration paths** are deliberately preserved:

- **Path A — Direct Modbus TCP.** The Raspberry Pi (or any LAN host) polls the LOGO! directly over Modbus TCP. This is the OT-native data path and lets the IT layer consume process data without any custom firmware running on a gateway.
- **Path B — RS-485 RTU → ESP32-S3 → MQTT → Telegraf → InfluxDB.** The ESP32-S3 polls the legacy RS-485 instruments and publishes structured JSON. This is the IT-native data path and demonstrates the protocol conversion role of an edge gateway.

Both paths converge in Grafana, giving the operator a single unified view. The IoT-sniffer observes both paths from a tap point on the LAN. The LOGO!'s own ability to act as a Modbus TCP master (reading from the ESP32-S3 register window) closes the loop in the opposite direction — proving that, once the two layers share a common protocol, the data-flow direction is a configuration choice rather than an architectural constraint.

---

## 12. Conclusions and Future Work

### 12.1 Conclusions

1. A single low-cost MCU (Waveshare ESP32-S3, ~$15) can credibly bridge Modbus RTU instruments into both a Modbus TCP service and an MQTT analytics pipeline from one cooperative `loop()`, with no RTOS task plumbing required. The production firmware uses 72.2% of flash and 14.8% of RAM, leaving meaningful headroom for OTA and ring-buffered telemetry.
2. A Raspberry Pi 4 is sufficient to host a credible self-hosted "TIG + broker" stack (Mosquitto + Telegraf + InfluxDB 2 + Grafana) with pinned image versions, environment-driven secrets, Pi host telemetry, ICMP and speedtest checks, and a Cloudflare Tunnel for authenticated remote access.
3. The structured Modbus TCP gateway library evaluation gives an evidence-based answer to the library-selection question and is reproducible: nine environments under one PlatformIO workspace, one Python host harness, one JSON metrics file per environment, one Excel scorecard. `emelianov/modbus-esp8266` is the chosen library for the production firmware; `eModbus/eModbus` is the strongest alternative for async, task-based use cases.
4. Telegraf and Node-RED are not interchangeable. Telegraf wins on memory, latency, throughput, and operability under source control; Node-RED wins on visual debugging and complex transformation logic. The recommendation is to use Telegraf for the production data pipeline and Node-RED for prototyping and flow-based logic.
5. The three device classes used in the testbed (MCU, SBC, PLC) are complementary, not competing. Each correctly occupies a distinct Purdue level.
6. Modbus TCP and anonymous MQTT are real, exploitable gaps on a LAN. The project demonstrates the gap concretely with `mbpoll` and the IoT-sniffer, and documents a mitigation roadmap.

### 12.2 Future Work

- Enable MQTT authentication on Mosquitto (`allow_anonymous false`, password file) and update firmware to send credentials.
- Implement MQTT Last-Will-and-Testament on the ESP32 (`sensors/esp32/online` retained, `0` on disconnect, `1` on connect) so subscribers detect dropouts.
- Add a firmware ring buffer so readings taken during an MQTT outage are replayed on reconnect.
- Implement firmware OTA (ArduinoOTA or `ESPAsyncHTTPUpdateServer`) so the ESP32-S3 no longer needs a USB cable for updates.
- Add a scheduled InfluxDB backup job (weekly `influx backup` cron to external storage).
- Add Docker `healthcheck:` blocks and `mem_limit` / `cpus:` constraints.
- Terminate TLS on MQTT (port 8883), InfluxDB, and Grafana even on the LAN, for defence in depth.
- Implement VLAN segregation between the OT and IT segments and firewall the Modbus TCP port to known masters only.
- Evaluate OPC-UA as a more secure alternative to Modbus TCP for OT–IT integration, and add an OPC-UA endpoint on the ESP32-S3 gateway.
- Add Grafana alerting for PLC register threshold violations (e.g., the alarm count in `VW2`).
- Move Grafana dashboards to file-based provisioning instead of API import.

---

*Prepared as a discussion draft for academic advisor review. All component versions, register addresses, library identifiers, and configuration values are cross-checked against the committed source repositories. The Tailscale host used for live-stack verification (`100.69.169.28`) was not reachable during preparation of this draft; the remaining hardware-required confirmations are noted in `Lab_network_monitoring/docs/project_review.md`.*
