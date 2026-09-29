# Siemens LOGO! 8 as Modbus TCP Slave with Node-RED
> Research compiled: 2026-03-31

---

## 1. Prerequisites & Firmware Requirements

- **Firmware minimum:** LOGO! 8 **FS:04** (firmware 1.81.2+). Earlier versions FS:01–03 do **NOT** support Modbus TCP.
- **Software:** LOGO! Soft Comfort **V8.2 or later** (V8.3.1+ recommended for v8.4 hardware)
- **Port:** TCP **502** — permanently reserved for Modbus TCP, cannot be changed
- **Both protocols active simultaneously:** Modbus TCP and Siemens S7 run on the same Ethernet port at the same time
- **Max concurrent connections:** ~8 total (shared across S7 + Modbus TCP)

---

## 2. Complete Modbus Register Address Map

> All addresses are **zero-based** (PDU addressing) — this matches how `node-red-contrib-modbus` addresses registers.

### Digital I/O — Coil / Discrete Area

| LOGO! Variable | Modbus Type | Address (0-based) | Count | Access | Function Code |
|---|---|---|---|---|---|
| I1–I24 (Digital Inputs) | Discrete Inputs | 0 – 23 | 24 | Read-only | FC2 |
| Q1–Q20 (Digital Outputs) | Coils | 8192 – 8211 | 20 | Read/Write | FC1, FC5, FC15 |
| M1–M64 (Markers/Flags) | Coils | 8256 – 8319 | 64 | Read/Write | FC1, FC5, FC15 |
| V0.0–V850.7 (VM Bit Memory) | Coils | 0 – 6807 | 6808 | Read/Write | FC1, FC5, FC15 |

**Quick reference — Q output coil addresses:**

| Output | Address |
|--------|---------|
| Q1 | 8192 |
| Q2 | 8193 |
| Q3 | 8194 |
| Q4 | 8195 |
| Q5 | 8196 |
| Q6 | 8197 |
| Q7 | 8198 |
| Q8 | 8199 |

**Quick reference — M marker coil addresses:**

| Marker | Address |
|--------|---------|
| M1 | 8256 |
| M2 | 8257 |
| M3 | 8258 |
| M4 | 8259 |

### Analog Values — Register Area

| LOGO! Variable | Modbus Type | Address (0-based) | Count | Access | Function Code |
|---|---|---|---|---|---|
| AI1–AI8 (Analog Inputs) | Input Registers | 0 – 7 | 8 | Read-only | FC4 |
| AQ1–AQ8 (Analog Outputs) | Holding Registers | 512 – 519 | 8 | Read/Write | FC3, FC6, FC16 |
| AM1–AM64 (Analog Markers) | Holding Registers | 528 – 591 | 64 | Read/Write | FC3, FC6, FC16 |
| VW0–VW850 (VM Word Memory) | Holding Registers | 0 – 424 | 425 | Read/Write | FC3, FC6, FC16 |

> All analog values are **16-bit integers**. No native float support.
> Endianness: **Big-endian (Motorola/network byte order)**.

---

## 3. LOGO! Soft Comfort Configuration Steps

1. Open **LOGO! Soft Comfort V8.2+** and open your project
2. Assign a **static IP address** via front panel menu: `Network → IP address`
3. Go to **Tools → Transfer → Network View** — verify the device appears
4. Drag a **"Modbus TCP Server"** block into network configuration:
   - Unit ID: **1**
   - Port: fixed at **502**
5. Modbus TCP server is essentially automatic on FS:04+ — LOGO! will respond to Modbus requests without any extra program logic
6. Upload the program to the LOGO! device

---

## 4. Node-RED Setup

### Install the palette

In Node-RED: **Menu → Manage Palette → Install**
Search: `node-red-contrib-modbus` → install latest **v5.x**

### Key nodes

| Node | Purpose |
|------|---------|
| `modbus-client` | Shared config node: holds IP, port, Unit ID |
| `modbus-read` | Polls registers at an interval |
| `modbus-write` | Writes coils or registers |
| `modbus-flex-write` | Write with dynamic address from payload |

### Modbus Client configuration

| Setting | Value |
|---------|-------|
| Type | TCP |
| IP | LOGO! IP (e.g. `192.168.0.3`) |
| Port | `502` |
| Unit-Id | `1` |
| Timeout | `5000 ms` |
| Reconnect period | `5000 ms` |

---

## 5. Node-RED Read/Write Examples

### Read Digital Outputs Q1–Q8
```
Node: modbus-read
FC:       FC1 – Read Coil Status
Address:  8192   (= Q1)
Quantity: 8
Poll:     1s
Output:   msg.values → [true/false, ...]
```

### Read Digital Inputs I1–I8
```
Node: modbus-read
FC:       FC2 – Read Discrete Input
Address:  0   (= I1)
Quantity: 8
```

### Write to Q1 (turn ON)
```
Node: modbus-write
FC:      FC5 – Write Single Coil
Address: 8192
Payload: true  (or 1 to turn ON, false/0 to turn OFF)
```

### Write to Marker M1
```
Node: modbus-write
FC:      FC5
Address: 8256
```

### Read Analog Inputs AI1–AI8
```
Node: modbus-read
FC:       FC4 – Read Input Registers
Address:  0
Quantity: 8
Output:   msg.values → [int, int, ...]   (16-bit)
```

### Read Analog Markers AM1–AM8
```
Node: modbus-read
FC:       FC3 – Read Holding Registers
Address:  528
Quantity: 8
```

### Write Analog Output AQ1
```
Node: modbus-write
FC:      FC6 – Write Single Register
Address: 512
Payload: 0–32767 (integer)
```

---

## 6. Minimal Example Node-RED Flow (Import this)

```json
[
  {
    "id": "modbus-client",
    "type": "modbus-client",
    "name": "LOGO!8",
    "clienttype": "tcp",
    "tcpHost": "192.168.0.3",
    "tcpPort": "502",
    "unit_id": "1",
    "clientTimeout": 5000,
    "reconnectTimeout": 5000
  },
  {
    "id": "read-Q1-Q8",
    "type": "modbus-read",
    "name": "Read Q1-Q8",
    "server": "modbus-client",
    "dataType": "Coil",
    "adr": "8192",
    "quantity": "8",
    "rate": "1",
    "rateUnit": "s",
    "wires": [["debug-out"], []]
  },
  {
    "id": "debug-out",
    "type": "debug",
    "active": true,
    "complete": "payload"
  }
]
```

---

## 7. Critical Gotchas

| Issue | Detail |
|-------|--------|
| **Zero-based addressing** | node-red-contrib-modbus uses 0-based PDU addresses. If a doc says Q1 = 8193 (1-based), enter **8192** in Node-RED. Off-by-one is the #1 mistake. |
| **Firmware FS:04 required** | Check via LOGO! Soft Comfort on connect — it shows firmware. FS:01–03 will not respond to Modbus TCP. |
| **16-bit integers only** | No native float. Apply scale factor in a Node-RED function node (e.g., `321 → 32.1°C`). |
| **I and Q are different Modbus types** | I (inputs) = Discrete Inputs → use FC2. Q (outputs) = Coils → use FC1/FC5. Do not mix them up. |
| **VM memory dual view** | V bit memory (coils FC1/FC5, addr 0–6807) and VW word memory (holding registers FC3/FC6, addr 0–424) share address space but are different data types. |
| **Big-endian byte order** | Multi-register values: use `msg.payload.buffer.readInt16BE(0)` or `readFloatBE(0)` in function nodes. |
| **Unit ID = 1** | Some Modbus masters default to Unit ID 0. LOGO! requires **1**. |
| **Port 502 is fixed** | Cannot be configured to a different port. |
| **Sleeping nodes** | If poll interval > 2 min, modbus-read may sleep. Use watchdog/trigger pattern for long-interval polling. |

---

## 8. Scaling Analog Values (Function Node Example)

```javascript
// AI1 raw integer → engineering value (e.g. 0-27648 → 0-100%)
const raw = msg.payload[0];  // 16-bit int from LOGO!
const scaled = (raw / 27648) * 100;
msg.payload = scaled.toFixed(1);
return msg;
```

For 4-20mA sensors wired through a 500Ω resistor (2-10V) to LOGO! analog input:
```javascript
// LOGO! analog input range: 0 = 0V, 27648 = 10V
// 4mA = 2V = 5530 counts, 20mA = 10V = 27648 counts
const raw = msg.payload[0];
const percent = ((raw - 5530) / (27648 - 5530)) * 100;
msg.payload = Math.max(0, Math.min(100, percent)).toFixed(1);
return msg;
```

---

## 9. Official Documentation & References

### Siemens Official PDFs
| Document | URL |
|----------|-----|
| LOGO! Modbus/TCP with SENTRON PAC (app example) | https://support.industry.siemens.com/cs/attachments/109779762/109779762_LOGO_ModbusTCP_DOC_en.pdf |
| LOGO! 8.3 Modbus/TCP with 7KN Powercenter | https://support.industry.siemens.com/cs/attachments/109813923/109813923_7KN_Powercenter1000_LOGO_DOC_V1_0_en.pdf |
| LOGO! Soft Comfort Online Help PDF | https://cache.industry.siemens.com/dl/files/807/100782807/att_924632/v1/Help_en-US_en-US.pdf |

### Tutorials & Community
| Resource | URL |
|----------|-----|
| Databoom – LOGO! 8.1 Modbus TCP (step-by-step) | https://support.databoom.com/hc/en-us/articles/360010716880 |
| blog.pundurs.lv – LOGO! 8 Modbus TCP (with Python examples) | https://blog.pundurs.lv/2019/05/13/interfacing-with-logo-8-using-modbus-tcp/ |
| Industrial Monitor Direct – LOGO! 8 Ethernet Protocol | https://industrialmonitordirect.com/blogs/knowledgebase/siemens-logo-8-ethernet-communication-protocol-support-and-configuration |
| NETIO AN60 – LOGO! + Modbus TCP integration | https://www.netio-products.com/en/application-notes/an60-how-to-integrate-plc-siemens-logo-with-netio-pdu-using-modbustcp |
| Home Assistant Community – LOGO! Modbus real-world examples | https://community.home-assistant.io/t/creating-modbus-configuration-for-a-siemens-logo/535762 |
| GitHub: hacs-modbus-logo (authoritative address table) | https://github.com/nos86/hacs-modbus-logo |
| Infoneva – Configuring LOGO! 8 Modbus TCP | https://infoneva.com/en/knowledge/configuring-logo-8-modbus-tcp-communication |

### Node-RED Resources
| Resource | URL |
|----------|-----|
| node-red-contrib-modbus (flows.nodered.org) | https://flows.nodered.org/node/node-red-contrib-modbus |
| FlowFuse – Using Modbus with Node-RED | https://flowfuse.com/node-red/protocol/modbus/ |
| Steve's Node-RED Guide – Modbus | https://stevesnoderedguide.com/node-red-modbus |
