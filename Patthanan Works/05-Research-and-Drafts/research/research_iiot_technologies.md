# Research: Industrial IoT Technologies for a Low-Cost IIoT Laboratory Platform

**Project Context:** Design of a Low-Cost Industrial IoT Laboratory Platform Using PLC, Microcontrollers, and Single-Board Computers
**Prepared by:** Bean
**Date:** March 2026
**Based on:** Professor's Briefing — `plc_iot_project_2026-03-02.pdf`

---

## Table of Contents

1. [SCADA — Supervisory Control and Data Acquisition](#1-scada)
2. [Modbus TCP — Industrial Ethernet Communication Protocol](#2-modbus-tcp)
3. [MQTT — Message Queuing Telemetry Transport](#3-mqtt)
4. [Node-RED — Flow-Based IoT Middleware](#4-node-red)
5. [Siemens LOGO! 8.4 — Low-Cost PLC](#5-siemens-logo-84)
6. [System Integration: How the Technologies Interconnect](#6-system-integration)
7. [References](#7-references)

---

## 1. SCADA

### 1.1 Definition and Fundamental Theory

**SCADA (Supervisory Control and Data Acquisition)** is an industrial control system architecture used to monitor, supervise, and control distributed processes and equipment through centralized software.

From a control-systems perspective, a SCADA system is best understood through the **hierarchical automation pyramid** (ISA-95 standard):

```
Level 4: Enterprise (ERP)
Level 3: Operations Management (MES)
Level 2: SCADA / HMI (Supervisory)   <-- SCADA resides here
Level 1: PLC / RTU (Control)
Level 0: Field Devices (Sensors/Actuators)
```

SCADA operates at **Level 2**, collecting real-time data from Level 1 devices (PLCs, RTUs) and presenting it to operators via an HMI (Human-Machine Interface), while also issuing supervisory control commands back downward.

### 1.2 Core SCADA Components

| Component | Role |
|-----------|------|
| **Field Devices** | Sensors (temperature, pressure, level) and actuators (valves, motors) |
| **RTU (Remote Terminal Unit)** | Microprocessor-based field device; reads sensors, executes local control, reports upstream |
| **PLC (Programmable Logic Controller)** | Executes deterministic ladder/function-block logic at the field level |
| **Communication Network** | Transfers data between field devices and the SCADA master (historically serial; modern = Ethernet/IP) |
| **SCADA Master/Server** | Centralized software collecting, storing, and displaying data; generates alarms |
| **HMI (Human-Machine Interface)** | Graphical interface for operators to visualize state and issue commands |
| **Historian Database** | Time-series store for all collected data (e.g., InfluxDB, OSIsoft PI) |

### 1.3 RTU Fundamentals

An **RTU** performs the following signal-processing chain:

1. **Analog Input Acquisition:** A physical quantity (e.g., pressure *P* in Pa) is converted by a sensor into a current signal *I* in the 4–20 mA standard range.
2. **Analog-to-Digital Conversion (ADC):** The ADC samples the signal at rate *f_s* and quantizes it to *n* bits.
   - **Nyquist criterion:** $f_s \geq 2 f_{max}$ where $f_{max}$ is the highest frequency component of the measured signal.
   - **Resolution:** $\Delta = \frac{V_{FS}}{2^n}$ (full-scale voltage divided by number of quantization levels).
3. **Digital Processing:** Local control logic or alarm logic is applied.
4. **Communication:** Data is serialized and transmitted to the SCADA master via the chosen protocol (Modbus, DNP3, IEC 60870-5, etc.).

The **4–20 mA current loop** is the dominant field wiring standard because current is immune to resistive voltage drops in long cable runs. The engineering-value conversion formula is:

$$x = x_{min} + \frac{(I - 4\,\text{mA})}{16\,\text{mA}} \cdot (x_{max} - x_{min})$$

where *x* is the measured physical quantity, *I* is the loop current, and *x_min*, *x_max* are the sensor's calibrated range.

**Example (from briefing — LOGO! 8.4 analog input):**
The Siemens LOGO! 8 uses a 500 Ω shunt resistor to convert the 4–20 mA loop current to a 2–10 V voltage that its analog input (AIx) can read:

$$V_{AIx} = I_{sensor} \times R_{shunt} = I_{sensor} \times 500\,\Omega$$

At *I* = 4 mA → *V* = 2 V (0% of range); at *I* = 20 mA → *V* = 10 V (100% of range).

### 1.4 SCADA Generations

| Generation | Era | Key Characteristic |
|-----------|-----|-------------------|
| 1st — Monolithic | 1970s | Mainframe-based, proprietary, standalone |
| 2nd — Distributed | 1980s–90s | Networked SCADA nodes via proprietary LANs |
| 3rd — Networked | 2000s | Open standards (OPC), Ethernet/IP, IT integration |
| **4th — IoT-based** | 2010s–present | Cloud, MQTT, REST APIs, edge computing, open hardware |

### 1.5 IoT-Based SCADA (4th Generation)

IoT-based SCADA, also called **4th-generation SCADA**, replaces proprietary hardware with:
- **Edge devices / SBCs** (e.g., Raspberry Pi) acting as local servers and gateways
- **Open protocols**: MQTT, HTTPS, REST APIs, WebSocket
- **Open-source software**: Node-RED (flow engine), Grafana (visualization), InfluxDB (time-series DB), Eclipse Mosquitto (MQTT broker)
- **Cloud platforms**: AWS IoT, Azure IoT Hub, ThingSpeak

In the project's architecture, the **Raspberry Pi SBC** running Node-RED, Mosquitto, and InfluxDB replaces the traditional proprietary SCADA server, making this a textbook 4th-generation IoT-SCADA implementation.

### 1.6 Key Performance Metrics

- **Scan rate (polling period):** $T_{scan}$ — how often the SCADA master reads all field devices.
- **System latency:** $\tau_{total} = \tau_{network} + \tau_{processing} + \tau_{display}$
- **Data throughput:** $R = \frac{N_{tags} \times \text{bytes/tag}}{T_{scan}}$ bytes/s
- **Availability:** $A = \frac{MTTF}{MTTF + MTTR}$ where MTTF = Mean Time To Failure, MTTR = Mean Time To Repair.

---

## 2. Modbus TCP

### 2.1 Overview and Historical Context

**Modbus** was invented by Modicon (now Schneider Electric) in 1979 as a serial communication protocol for PLCs. It is arguably the most widely deployed industrial protocol in existence.

**Modbus TCP** (also called Modbus TCP/IP) is the Ethernet adaptation of the original Modbus RTU serial protocol. It encapsulates Modbus frames inside standard TCP/IP packets, enabling communication over any standard Ethernet infrastructure.

### 2.2 Protocol Stack Position

Modbus TCP maps to the OSI model as follows:

```
OSI Layer 7 — Application:    Modbus Application Protocol (MBAP + PDU)
OSI Layer 6 — Presentation:   (data is raw binary, no encoding layer)
OSI Layer 5 — Session:        TCP connection management
OSI Layer 4 — Transport:      TCP (port 502)
OSI Layer 3 — Network:        IP (IPv4 / IPv6)
OSI Layer 2 — Data Link:      Ethernet (IEEE 802.3)
OSI Layer 1 — Physical:       Ethernet cable (Cat5e/Cat6) or Wi-Fi
```

The **registered TCP port for Modbus TCP is 502** (IANA-assigned). All Modbus TCP communication initiates on this port.

### 2.3 Client–Server Architecture

Modbus TCP uses a **Master–Slave** model (renamed **Client–Server** in modern specifications):

- **Client (Master):** Initiates requests (e.g., SCADA server, Node-RED, Raspberry Pi, a supervisory PC).
- **Server (Slave):** Responds to requests (e.g., LOGO! 8.4 PLC, ESP32 acting as a Modbus TCP server, a sensor gateway).

The relationship is strictly **request–response**; servers never transmit unsolicited data. Multiple clients may connect to one server, and one client may address multiple servers (distinguished by the **Unit Identifier** field).

### 2.4 Frame Structure and Formulas

A Modbus TCP frame consists of the **MBAP Header** (7 bytes) followed by the **PDU** (Protocol Data Unit):

```
┌──────────────────┬──────────────────┬──────────────────┬────────────────┬────────────────┬──────────────────────┐
│ Transaction ID   │ Protocol ID      │ Length           │ Unit ID        │ Function Code  │ Data                 │
│ (2 bytes)        │ (2 bytes)        │ (2 bytes)        │ (1 byte)       │ (1 byte)       │ (variable)           │
└──────────────────┴──────────────────┴──────────────────┴────────────────┴────────────────┴──────────────────────┘
←─────────────────────── MBAP Header (7 bytes) ───────────────────────→ ←──── PDU ─────→
```

**Field definitions:**

| Field | Size | Description |
|-------|------|-------------|
| **Transaction ID** | 2 bytes | Matches request to response; incremented per transaction |
| **Protocol ID** | 2 bytes | Always `0x0000` for Modbus |
| **Length** | 2 bytes | Number of remaining bytes (Unit ID + Function Code + Data) |
| **Unit ID** | 1 byte | Slave device address (0–255); `0xFF` = broadcast to all |
| **Function Code (FC)** | 1 byte | Specifies the operation to perform |
| **Data** | Variable | Request parameters or response data |

**Maximum PDU size:** 253 bytes → Maximum Modbus TCP frame: 260 bytes.

### 2.5 Function Codes (FC)

The most commonly used function codes are:

| FC (hex) | Name | Direction | Object Type |
|----------|------|-----------|-------------|
| `0x01` | Read Coils | Read | Digital Output (1-bit, R/W) |
| `0x02` | Read Discrete Inputs | Read | Digital Input (1-bit, RO) |
| `0x03` | Read Holding Registers | Read | 16-bit word, R/W |
| `0x04` | Read Input Registers | Read | 16-bit word, RO |
| `0x05` | Write Single Coil | Write | Digital Output |
| `0x06` | Write Single Register | Write | Holding Register |
| `0x0F` | Write Multiple Coils | Write | Multiple Digital Outputs |
| `0x10` | Write Multiple Registers | Write | Multiple Holding Registers |

**Error response:** If a server cannot fulfill a request, it responds with the function code ORed with `0x80` (i.e., `FC | 0x80`) and an **Exception Code** in the data field. Exception codes include: `0x01` (Illegal Function), `0x02` (Illegal Data Address), `0x03` (Illegal Data Value), `0x04` (Slave Device Failure).

### 2.6 Modbus Data Model

Modbus organizes data into four **primary tables (object types)**:

| Table | Address Range | Data Type | Access |
|-------|--------------|-----------|--------|
| **Coils** | 1–9999 (0x0000–0x270E) | 1-bit Boolean | Read/Write |
| **Discrete Inputs** | 10001–19999 | 1-bit Boolean | Read Only |
| **Holding Registers** | 40001–49999 | 16-bit unsigned int | Read/Write |
| **Input Registers** | 30001–39999 | 16-bit unsigned int | Read Only |

> **Convention:** PLC internal output coils (Q) map to Coils; sensor physical readings map to Input Registers; setpoints and configurations map to Holding Registers.

For the LOGO! 8 PLC, outputs (Q1–Q4) can be mapped to **Coils**, and analog measurement values can be mapped to **Input Registers**.

### 2.7 Modbus RTU vs. Modbus TCP Comparison

| Feature | Modbus RTU | Modbus TCP |
|---------|-----------|------------|
| **Physical Layer** | RS-485, RS-232 | Ethernet (10/100/1000 Mbps) |
| **Error Checking** | CRC-16 appended to frame | TCP checksum + CRC in payload |
| **Addressing** | 1-byte device address (1–247) | IP address + Unit ID |
| **Max Devices** | 247 per segment | Limited by network infrastructure |
| **Typical Speed** | 9600–115200 baud | 10–1000 Mbps |
| **Latency** | ~10–100 ms (baud-dependent) | ~1–10 ms (LAN) |
| **Topology** | Bus (multi-drop) | Star (switched Ethernet) |
| **Distance** | Up to 1200 m (RS-485) | Up to 100 m per segment (Cat5e) |

**CRC-16 formula for Modbus RTU** (not used in TCP but fundamental to understand the evolution):

$$CRC_{16}(M) = M(x) \cdot x^{16} \mod G(x)$$

where the generator polynomial is $G(x) = x^{16} + x^{15} + x^2 + 1$ (hex: `0x8005`), and *M* is the message. This is replaced in Modbus TCP by TCP's built-in checksum (TCP header checksum covers the entire segment).

### 2.8 Timing Analysis

For a single Modbus TCP **read holding register** transaction over LAN:

$$\tau_{transaction} = \tau_{propagation} + \tau_{server\_processing} + \tau_{propagation\_return}$$

$$\tau_{propagation} \approx \frac{d}{c_{cable}}$$

where *d* is cable length and $c_{cable} \approx 2 \times 10^8$ m/s (speed of signal in copper). Over a 10 m LAN cable this is ~50 ns — negligible. Server processing on a PLC like LOGO! typically takes 1–20 ms. So practical round-trip time (RTT) ≈ 2–20 ms on a local Ethernet.

---

## 3. MQTT

### 3.1 Overview and Fundamental Theory

**MQTT (Message Queuing Telemetry Transport)** is a lightweight, **publish–subscribe** messaging protocol designed for reliable and efficient communication between distributed devices over TCP/IP networks. It was originally developed by IBM (Andy Stanford-Clark and Arlen Nipper) in 1999 for monitoring oil pipelines via satellite — an environment with limited bandwidth and unreliable connections.

MQTT standardized by **OASIS** and published as **ISO/IEC 20922:2016**.

### 3.2 Publish–Subscribe Pattern vs. Request–Response

Modbus TCP uses **request–response** (client must poll repeatedly for updates). MQTT uses **publish–subscribe**, which decouples producers from consumers:

```
                    ┌──────────────────────┐
  Publisher ──────> │    MQTT Broker       │ ──────> Subscriber A
  (LOGO! PLC)       │  (Eclipse Mosquitto) │ ──────> Subscriber B
  (ESP32 sensor)    │                      │ ──────> Node-RED
                    └──────────────────────┘
```

- **Publisher:** Any client that sends a message tagged with a **topic string**.
- **Broker:** Central message router. It receives all published messages and distributes copies to all subscribers of the matching topic.
- **Subscriber:** Any client that has declared interest in one or more topic patterns.

The mathematical model of the broker is a **many-to-many message multiplexer**:

$$M_{out}(S_i) = \bigcup_{\{P_j : T(P_j) \in \text{subscriptions}(S_i)\}} M_{in}(P_j)$$

where $M_{out}(S_i)$ is the set of messages delivered to subscriber $S_i$, $T(P_j)$ is the topic of publisher $P_j$, and the union is over all publishers whose topic matches subscriber $S_i$'s subscription filter.

### 3.3 Topic Naming and Wildcards

Topics are **UTF-8 strings** with `/` as a level separator. Example hierarchy for this project:

```
factory/tank1/level         → Water level sensor reading
factory/tank1/inlet_valve   → Inlet valve state
factory/tank1/outlet_valve  → Outlet valve state
factory/logo8/Q1            → PLC digital output Q1
factory/esp32/temperature   → ESP32 sensor temperature
```

**Wildcard characters** allowed in subscription patterns:

| Wildcard | Matches | Example |
|----------|---------|---------|
| `+` | Single level | `factory/+/level` matches `factory/tank1/level` and `factory/tank2/level` |
| `#` | Multiple levels (must be last) | `factory/#` matches all topics under `factory/` |

### 3.4 MQTT Protocol Stack Position

```
OSI Layer 7 — Application:  MQTT (Control packets + payload)
OSI Layer 4 — Transport:    TCP (default port 1883, or 8883 for TLS)
OSI Layer 3 — Network:      IP
OSI Layer 2 — Data Link:    Ethernet / Wi-Fi (802.11)
OSI Layer 1 — Physical:     Copper / Wi-Fi radio
```

### 3.5 MQTT Packet Structure

Every MQTT message begins with a **Fixed Header** (2+ bytes):

```
Byte 1: [Control Packet Type (4 bits)] [Flags (4 bits)]
Byte 2+: Remaining Length (1–4 bytes, variable-length encoding)
```

**Control Packet Types** include:

| Code | Name | Direction | Purpose |
|------|------|-----------|---------|
| 1 | CONNECT | Client → Broker | Establish connection |
| 2 | CONNACK | Broker → Client | Connection acknowledgment |
| 3 | PUBLISH | Client ↔ Broker | Publish a message |
| 4 | PUBACK | Client ↔ Broker | QoS 1 acknowledgment |
| 8 | SUBSCRIBE | Client → Broker | Subscribe to topic(s) |
| 9 | SUBACK | Broker → Client | Subscription confirmation |
| 12 | PINGREQ | Client → Broker | Keep-alive ping |
| 14 | DISCONNECT | Client → Broker | Clean disconnection |

**Variable-length encoding** for the Remaining Length field uses a **multi-byte big-endian scheme** where each byte uses 7 bits for data and 1 bit as a continuation flag:

$$L_{encoded} = \begin{cases} L & \text{if } L \leq 127 \\ (L \mod 128 + 128) \| \lfloor L/128 \rfloor & \text{if } 128 \leq L \leq 16383 \end{cases}$$

This allows encoding lengths up to 268,435,455 bytes (≈256 MB) in 4 bytes.

### 3.6 Quality of Service (QoS) Levels

MQTT defines three delivery guarantees:

| QoS | Name | Guarantee | Mechanism | Overhead |
|-----|------|-----------|-----------|----------|
| **0** | At most once | No guarantee; fire-and-forget | No ACK, no retry | Lowest |
| **1** | At least once | Message delivered ≥1 time | PUBACK required; retried until ACK received | Medium |
| **2** | Exactly once | Message delivered exactly once | 4-way handshake (PUBLISH→PUBREC→PUBREL→PUBCOMP) | Highest |

**QoS 2 handshake state machine:**

```
Sender          Broker/Receiver
  │──PUBLISH──────────>│  (QoS=2, DUP=0, Packet ID=X)
  │<──PUBREC───────────│  (Packet ID=X)
  │──PUBREL──────────>│  (Packet ID=X)
  │<──PUBCOMP──────────│  (Packet ID=X)
```

For IoT sensor data (e.g., tank level), **QoS 1** is typically sufficient — occasional duplicates are acceptable, but dropped messages are not. For critical control commands (open/close valve), **QoS 2** may be used.

### 3.7 Keep-Alive and Last Will and Testament (LWT)

**Keep-Alive:** The client specifies a `keepAlive` interval *T_ka* (in seconds) during CONNECT. If the broker receives no packet from the client within $1.5 \times T_{ka}$, it treats the client as disconnected.

**Last Will and Testament (LWT):** At CONNECT time, a client can register a "will" message — a topic and payload to be published by the broker automatically if the client disconnects ungracefully. This is essential for fault detection in IIoT:

```
Will Topic:   factory/logo8/status
Will Payload: "OFFLINE"
Will QoS:     1
Will Retain:  true
```

### 3.8 Retained Messages

A **retained message** is stored by the broker and delivered immediately to any new subscriber of the matching topic. This solves the "late subscriber problem": a new dashboard connecting does not have to wait for the next published sensor update to know the current state.

Formally, for each topic *T*, the broker stores at most one retained message $M_{ret}(T)$. On subscription to *T*, the broker immediately delivers $M_{ret}(T)$ (if it exists) before any future publishes.

### 3.9 Bandwidth Efficiency

MQTT's minimum overhead is **2 bytes** (fixed header only). Compare with HTTP which requires hundreds of bytes of headers per request. The bandwidth saving ratio is approximately:

$$\eta = 1 - \frac{B_{MQTT}}{B_{HTTP}} \approx 1 - \frac{30\,\text{bytes}}{500\,\text{bytes}} = 94\%$$

This makes MQTT highly suitable for constrained devices (ESP32, microcontrollers) and low-bandwidth networks.

---

## 4. Node-RED

### 4.1 Overview and Fundamental Theory

**Node-RED** is an open-source, **flow-based visual programming platform** built on **Node.js** and designed for rapid development of IoT, industrial automation, and edge computing applications. It was originally created by IBM Emerging Technology in 2013 and is now a project of the **OpenJS Foundation**.

The computational model underlying Node-RED is the **Flow-Based Programming (FBP)** paradigm, formally defined by J. Paul Morrison in the 1970s. In FBP:

- A program is a **directed graph** where **nodes** are computational processes and **edges** are **message-passing channels**.
- Each node has zero or more **input ports** and zero or more **output ports**.
- Messages (called **msg objects** in Node-RED) flow along the wires connecting ports.

Formally, a Node-RED flow can be described as a **directed acyclic graph (DAG)** (though cycles are permitted for feedback loops):

$$G = (V, E)$$

where $V$ is the set of nodes and $E \subseteq V \times V$ is the set of directed wires. Each wire $(u, v) \in E$ carries a stream of **msg** objects from the output of node *u* to the input of node *v*.

### 4.2 Architecture

Node-RED runs as a **Node.js server process** and exposes a browser-based **flow editor** (UI) over HTTP (default port 1880). The runtime executes flows and manages the message-passing event loop.

```
┌────────────────────────────────────────────┐
│           Node-RED Runtime (Node.js)        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │ Flow     │  │ Node     │  │ Message  │  │
│  │ Engine   │  │ Registry │  │ Router   │  │
│  └──────────┘  └──────────┘  └──────────┘  │
│         ↕ HTTP/WebSocket                    │
│  ┌──────────────────────────────────────┐   │
│  │     Browser-Based Flow Editor        │   │
│  │     (Drag-and-drop UI on port 1880)  │   │
│  └──────────────────────────────────────┘   │
└────────────────────────────────────────────┘
```

### 4.3 The msg Object

The fundamental data unit in Node-RED is the **msg object** — a JavaScript object passed between nodes. Its structure:

```javascript
msg = {
    topic:   "factory/tank1/level",   // string — message subject/topic
    payload: 74.42,                   // any type — the actual data value
    _msgid:  "abc123",                // unique message ID (auto-assigned)
    // ... any additional user-defined properties
}
```

Nodes transform `msg.payload` as the data flows through the graph. For example:

```
[Modbus Read Node] → msg.payload = [74, 0, 1, 0, ...] (raw register array)
     ↓ [Function Node: convert to percent]
msg.payload = (msg.payload[0] / 1000) * 100 = 7.442%
     ↓ [MQTT Out Node] → publishes to broker
     ↓ [Dashboard Gauge Node] → displays on UI
```

### 4.4 Node Types and Categories

**Core built-in nodes:**

| Category | Nodes | Purpose |
|----------|-------|---------|
| **Input** | `inject`, `http in`, `mqtt in`, `tcp in`, `serial in` | Trigger flows or receive data |
| **Output** | `debug`, `http out`, `mqtt out`, `tcp out`, `file` | Send data or display output |
| **Function** | `function`, `change`, `switch`, `template`, `delay` | Transform or route messages |

**Community-installed nodes (npm packages) relevant to this project:**

| Package | Protocol | Purpose |
|---------|----------|---------|
| `node-red-contrib-modbustcp` | Modbus TCP | Read/write Modbus TCP registers (PLC ↔ Node-RED) |
| `node-red-node-serialport` | Serial/Modbus RTU | RS-485 communication |
| `node-red-dashboard` | HTTP/WebSocket | Build web-based dashboards (gauges, charts, buttons) |
| `node-red-contrib-influxdb` | InfluxDB API | Write time-series data to InfluxDB |

### 4.5 Node-RED as an OT/IT Bridge

In the project's architecture, Node-RED acts as the **middleware gateway** bridging two domains:

```
OT (Operational Technology) Domain:
  LOGO! 8 PLC ──[Modbus TCP]──> Node-RED ──[MQTT]──> IT Domain:
  ESP32 MCU ────[MQTT]────────> Node-RED             Grafana Dashboard
  Sensors/Actuators                                   InfluxDB
                                                      Cloud Services
```

This is the classical **IT/OT convergence** challenge in Industry 4.0. Node-RED handles **protocol translation** (Modbus TCP → MQTT), **data transformation** (raw register values → engineering units), **routing** (filtering, switching on tag), and **storage** (writing to InfluxDB).

### 4.6 Node-RED Flow — Mathematical Transformation Example

Consider a flow reading the LOGO! 8 tank level from a Modbus holding register and publishing it via MQTT:

1. **Modbus Read:** Function code 0x03, register address 40001, 1 register → raw 16-bit integer value *R* (e.g., R = 744).
2. **Scale to Engineering Units:** LOGO! scales analog values to the range 0–1000 (representing 0–100%). Conversion:

$$L_{percent} = \frac{R}{1000} \times 100 = \frac{744}{1000} \times 100 = 74.4\%$$

3. **Function Node code:**

```javascript
msg.payload = (msg.payload[0] / 1000) * 100;
msg.topic = "factory/tank1/level_percent";
return msg;
```

4. **MQTT Out:** Publishes `74.4` to topic `factory/tank1/level_percent`.

### 4.7 Dashboard and SCADA-like Visualization

Node-RED Dashboard (`node-red-dashboard`) provides a browser-based UI with widgets including gauges, line charts, buttons, and LED indicators — directly comparable to a traditional SCADA HMI. It updates in real-time via **WebSocket** (persistent bidirectional TCP connection), so the browser receives push notifications from Node-RED without polling:

$$\tau_{display\_update} = \tau_{WebSocket} + \tau_{render} \approx \text{5–50 ms}$$

This is far lower latency than traditional HTTP polling (which would require at minimum one RTT per update interval).

---

## 5. Siemens LOGO! 8.4

### 5.1 Overview

**Siemens LOGO! 8** (hardware version 8, firmware 8.4) is a compact, low-cost **micro-PLC (Programmable Logic Controller)** targeted at simple automation tasks, educational platforms, building automation, and small industrial applications. It is manufactured by Siemens AG under the product family "LOGO!".

The "8.4" in the briefing refers to the **firmware version 8.4**, the latest major release, which introduced native MQTT support in addition to the existing Modbus TCP capability — making it directly relevant to this IoT project.

### 5.2 PLC Fundamental Theory — Scan Cycle

A PLC operates on a **deterministic cyclic scan loop**:

```
┌──────────────────────────────────────────┐
│  PLC Scan Cycle (period T_scan):          │
│  1. Read all physical inputs → I memory  │
│  2. Execute user program (FBD/LD logic)  │
│  3. Write I/O image → physical outputs   │
│  4. Service communications               │
└──────────────────────────────────────────┘
```

The **scan time** $T_{scan}$ for LOGO! 8 is typically in the range of **0.1–10 ms** depending on program complexity. This determinism is the fundamental advantage of a PLC over a general-purpose computer (like Raspberry Pi or ESP32).

For a controlled process with dynamics having time constant $\tau_{process}$, Shannon's sampling theorem applied to control requires:

$$T_{scan} \leq \frac{\tau_{process}}{10} \text{ (rule of thumb for good control)}$$

For a water tank system with $\tau_{process} \approx$ several seconds, even a $T_{scan}$ = 100 ms is more than adequate.

### 5.3 LOGO! 8 Hardware Specifications

**Base unit: LOGO! 8 12/24RCE (6ED1052-1MD00-0BA8)**

| Specification | Value |
|--------------|-------|
| Supply voltage | 12 V / 24 V DC |
| Digital inputs | 8 (4 of which can be used as analog 0–10 V) |
| Digital outputs | 4 (relay type) |
| Relay output rating | 10 A, 250 V AC |
| Analog inputs (via AM2 module) | 0–10 V or 4–20 mA |
| Analog outputs (via AM2 AQ) | 0–10 V or 0/4–20 mA |
| Display | Integrated text display |
| Ethernet port | 1× RJ45, 10/100 Mbps |
| Programming software | LOGO! Soft Comfort (Windows/macOS) |
| Memory | 400 blocks |
| Timers | Up to 64 |
| Communication protocols | **Modbus TCP, MQTT** (v8.4), S7 protocol |

**Expansion modules:**

| Module | Function |
|--------|----------|
| LOGO! DM8 12/24R | +4 DI, +4 DO (relay), 12/24 V |
| LOGO! AM2 | +2 analog inputs (0–10 V / 4–20 mA) |
| LOGO! AM2 AQ | +2 analog outputs (0–10 V / 0/4–20 mA) |

### 5.4 Programming Languages — FBD and LD

The LOGO! 8 supports two IEC 61131-3 compliant programming languages (via LOGO! Soft Comfort):

#### 5.4.1 Ladder Diagram (LD)

Ladder Diagram is based on the electrical relay ladder circuit analogy:

```
   I1          I2          Q1
   ─┤ ├─────────┤/├──────( )─   → Q1 = I1 AND NOT(I2)
```

Logic relationships:
- **Series contacts:** AND logic — $Q = A \cdot B$ (both contacts must close)
- **Parallel contacts:** OR logic — $Q = A + B$ (either contact closes the path)
- **Normally closed contact (─┤/├─):** NOT logic — contact closes when coil is de-energized
- **Coil (─( )─):** Output energized when current path is complete

**Boolean algebra for tank level control (from briefing, slide 15 example):**

```
Ladder rung 2 (OUT VALVE logic):
  MASTER AND HIGH AND NOT(LOW) → OUT_VALVE

  Q_OUT_VALVE = M0 · I12 · /I16
```

where M0 = MASTER bit, I12 = HIGH switch, I16 = LOW switch.

#### 5.4.2 Function Block Diagram (FBD)

FBD represents programs as interconnected **function blocks** — graphical blocks with defined input/output behaviors:

```
    I1 ───┐
          │ AND ├──────── Q1
    I2 ───┘
```

LOGO! Soft Comfort provides special function blocks (SFBs):

| Block | Symbol | Function |
|-------|--------|----------|
| **On-delay timer** | T_ON | Output activates *t* seconds after input goes high |
| **Off-delay timer** | T_OFF | Output stays on *t* seconds after input goes low |
| **Pulse relay** | RS | Set-Reset flip-flop with memory |
| **Counter** | CTU | Counts rising edges of input signal |
| **Analog comparator** | AC | Compares two analog values; outputs digital result |
| **PI controller** | PI | Proportional-Integral control for analog loops |

**On-delay timer equations:**

$$Q(t) = \begin{cases} 1 & \text{if } I(t) = 1 \text{ and } (t - t_{rise}) \geq T_{delay} \\ 0 & \text{otherwise} \end{cases}$$

### 5.5 Modbus TCP on LOGO! 8

The LOGO! 8 can act as a **Modbus TCP Server** (slave). The PLC's I/O and memory areas are mapped to Modbus addresses according to Siemens documentation:

| Modbus Address | LOGO! Resource | Type |
|---------------|---------------|------|
| 1–8 (Coils) | Q1–Q8 (Digital Outputs) | R/W |
| 1–24 (Discrete Inputs) | I1–I24 (Digital Inputs) | RO |
| 40001–40008 | AM1–AM8 (Analog Values × 10) | RO |
| 40011–40018 | AQ1–AQ8 (Analog Outputs) | R/W |

To read Q1 status from Node-RED via Modbus TCP:
- FC = 0x01 (Read Coils)
- Start address = 0x0000 (coil 1)
- Quantity = 1

### 5.6 MQTT on LOGO! 8 (Firmware v8.4)

LOGO! v8.4 introduced native MQTT **client** support. The PLC can:
- Connect to any MQTT broker (e.g., Eclipse Mosquitto on Raspberry Pi)
- **Publish** I/O status and variable values to configured topics
- **Subscribe** to topics and use received payloads to set output values or variables

**Configuration parameters in LOGO! Soft Comfort v8.4:**
- Broker IP address and port (default 1883)
- Client ID
- Username / password (optional)
- Keep-alive interval
- Topic mappings (I/O variable ↔ MQTT topic string)
- QoS level (0 or 1)
- Retain flag

This native MQTT capability means that the LOGO! 8 can send sensor data directly to the Raspberry Pi broker without needing Node-RED as an intermediary for data acquisition — simplifying the architecture for some use cases.

### 5.7 4–20 mA Analog Input Interface

As shown in the briefing (slide 17), the LOGO! analog input receives 4–20 mA signals through a **500 Ω shunt resistor**, converting current to voltage:

$$V_{AI} = I_{sensor} \times R_{shunt}$$

| Sensor Current | Shunt Voltage | LOGO! Raw Value | Engineering % |
|---------------|--------------|-----------------|---------------|
| 4 mA | 2 V | 0 | 0% |
| 12 mA | 6 V | 500 | 50% |
| 20 mA | 10 V | 1000 | 100% |

LOGO! represents the analog value internally as an integer in the range **0–1000**, proportional to the 0–10 V input range. The full conversion formula:

$$x_{engineering} = x_{min} + \frac{V_{AI} - 2}{8} \cdot (x_{max} - x_{min}) = x_{min} + \frac{I - 4\,\text{mA}}{16\,\text{mA}} \cdot (x_{max} - x_{min})$$

---

## 6. System Integration: How the Technologies Interconnect

### 6.1 Full System Architecture

The complete system proposed in the project integrates all five technologies into the following layered architecture:

```
┌─────────────────────────────────────────────────────────────────┐
│  LAYER 3: Visualization & Analytics (SBC — Raspberry Pi)         │
│   Grafana Dashboard ←──────── InfluxDB (Time-series DB)          │
│   Node-RED Dashboard (WebSocket/HTTP)                            │
└────────────────────────┬────────────────────────────────────────┘
                         │ MQTT pub/sub (port 1883)
┌────────────────────────▼────────────────────────────────────────┐
│  LAYER 2: Edge Gateway / Broker (SBC — Raspberry Pi)             │
│   Eclipse Mosquitto (MQTT Broker)                                │
│   Node-RED (Flow Engine: Protocol Translation + Logic)           │
└───────┬───────────────────────────────────────────┬─────────────┘
        │ Modbus TCP (port 502)                      │ MQTT (port 1883)
┌───────▼───────────────┐                ┌───────────▼─────────────┐
│  LAYER 1: Controllers  │                │  LAYER 1: Microcontroller│
│  Siemens LOGO! 8.4    │                │  ESP32 (WiFi/Ethernet)  │
│  (PLC — FBD/LD logic) │                │  (MQTT client + Modbus  │
└───────┬───────────────┘                │   protocol converter)   │
        │ 24 V DC wiring                 └───────────┬─────────────┘
┌───────▼───────────────────────────────────────────▼─────────────┐
│  LAYER 0: Field Devices                                          │
│  Sensors: Float switches, 4–20 mA level sensor, temp sensors    │
│  Actuators: Relay-controlled valves, pumps, motors              │
└─────────────────────────────────────────────────────────────────┘
```

### 6.2 Data Flow — Tank Level Control Example

**Scenario:** Water tank with float switches (HIGH/LOW) and a 4–20 mA level sensor, controlled by the LOGO! 8 PLC, monitored via Node-RED dashboard.

**Step-by-step data flow:**

1. **Sensor → PLC:** High/Low float switches → LOGO! digital inputs I12, I16. 4–20 mA level sensor → 500 Ω shunt → 2–10 V → LOGO! analog input AI1 → internal value 0–1000.

2. **PLC Logic:** FBD/LD executes on every scan cycle (~1 ms). Valve control:
   - IN VALVE open: if `MASTER AND LOW AND NOT(HIGH) AND START`
   - OUT VALVE open: if `MASTER AND HIGH AND NOT(LOW)`

3. **PLC → Node-RED (Modbus TCP):** Node-RED Modbus client polls LOGO! every 500 ms. Reads coils Q1–Q4 (valve states), input registers AI1 (level raw 0–1000).

4. **Node-RED Processing:** Function node converts raw register:
   ```javascript
   msg.payload = (msg.payload[0] / 1000) * 100; // → 0.0 to 100.0 %
   ```
   Routes to MQTT Out node and Dashboard gauge node simultaneously.

5. **Node-RED → MQTT Broker:** Publishes `74.4` to topic `factory/tank1/level_percent` on Mosquitto.

6. **Mosquitto → Subscribers:** Grafana (via InfluxDB), mobile dashboards, any ESP32 subscribers receive the update instantly (push model — no polling).

7. **InfluxDB:** Node-RED writes data point:
   ```
   measurement: tank_level, field: percent, value: 74.4, time: 2026-03-06T10:30:00Z
   ```
   Grafana queries InfluxDB for time-series chart.

### 6.3 Protocol Comparison Summary

| Feature | Modbus TCP | MQTT |
|---------|-----------|------|
| **Paradigm** | Request–Response (polling) | Publish–Subscribe (event-driven) |
| **Coupling** | Tight (master knows slave address) | Loose (publishers/subscribers unaware of each other) |
| **Typical use in project** | PLC ↔ Node-RED (local LAN) | Node-RED ↔ dashboards, cloud, ESP32 |
| **Guaranteed delivery** | TCP (reliable transport) | QoS 0, 1, or 2 (selectable) |
| **Header overhead** | 7 bytes (MBAP) | 2+ bytes (fixed header) |
| **Scalability** | Limited (poll loop grows with devices) | High (broker routes to many subscribers) |
| **IoT suitability** | Moderate (OT-centric) | Excellent (designed for IoT) |
| **Native LOGO! 8 support** | ✅ Yes (server mode) | ✅ Yes (v8.4, client mode) |
| **Node-RED support** | ✅ Via `node-red-contrib-modbustcp` | ✅ Built-in nodes |

### 6.4 Related Work Summary

| Paper | Year | Architecture | Key Findings |
|-------|------|-------------|-------------|
| "Development of a Remote Industrial Lab for Automatic Control based on Node-RED" | 2020 | Node-RED ↔ MQTT broker ↔ Modbus TCP server (Schneider M340 PLC) | Students access lab remotely via MQTT; Node-RED bridges MQTT ↔ Modbus |
| "Cost-Effective IIoT Gateway Development Using ESP32 for Industrial Applications" | 2024 | ESP32 (Modbus TCP server) ↔ Siemens S7-1200 PLC ↔ ThingSpeak/Blink (MQTT) | ESP32 replaces Siemens IOT2050 gateway at fraction of cost; ENC28J60 Ethernet module for ESP32 |
| "Implementation of Industrial IoT Integration Using Node-RED and PLC on Cascade Control Level and Flow Plant" | 2025 | Node-RED + PLC for cascade loop control | Node-RED implements supervisory cascade logic integrating multiple PLCs |

---

## 7. References

1. **Professor's Briefing Document** — *Design of a Low-Cost Industrial IoT Laboratory Platform Using PLC, Microcontrollers, and Single-Board Computers*, 2026.

2. Modbus Organization. *Modbus Application Protocol Specification V1.1b3*. 2012. [modbus.org](http://www.modbus.org/docs/Modbus_Application_Protocol_V1_1b3.pdf)

3. OASIS Standard. *MQTT Version 3.1.1*. 2014. ISO/IEC 20922:2016. [mqtt.org](https://mqtt.org/mqtt-specification/)

4. OpenJS Foundation. *Node-RED Documentation*. [nodered.org/docs](https://nodered.org/docs/)

5. Siemens AG. *LOGO! 8 Manual — Communication*. Siemens Industry Support, 2023.

6. J. Paul Morrison. *Flow-Based Programming: A New Approach to Application Development*, 2nd ed., 2010.

7. Ruano-Ruano, I. et al. *Development of a Remote Industrial Laboratory for Automatic Control based on Node-RED*. IFAC-PapersOnLine, 2020. [DOI:10.1016/S2405-8963(20)323478](https://www.sciencedirect.com/science/article/pii/S2405896320323478)

8. "Cost-Effective IIoT Gateway Development Using ESP32 for Industrial Applications" (2024). [engj.org/index.php/ej/article/view/4584](https://engj.org/index.php/ej/article/view/4584)

9. "Implementation of Industrial IoT Integration Using Node-RED and PLC on Cascade Control Level and Flow Plant" (2025). [jppipa.unram.ac.id/index.php/jppipa/article/view/11623](https://jppipa.unram.ac.id/index.php/jppipa/article/view/11623)

10. RedPLC — Node-RED nodes for Soft-PLC with Ladder Logic. [github.com/redplc/redplc](https://github.com/redplc/redplc)

11. ISA-95 Standard. *Enterprise-Control System Integration*, International Society of Automation, 2018.

---

*End of Research Document*
