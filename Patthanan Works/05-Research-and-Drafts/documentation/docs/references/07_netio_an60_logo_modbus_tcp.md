# AN60: Integrating Siemens LOGO! PLC with NETIO PDU via Modbus TCP
> Source: https://www.netio-products.com/en/application-notes/an60-how-to-integrate-plc-siemens-logo-with-netio-pdu-using-modbustcp

## Overview

Demonstrates LOGO! 8 as a Modbus TCP **master (client)** controlling a NETIO PDU (slave/server). Useful reference for understanding how LOGO! acts as a Modbus master.

## Hardware

- Siemens LOGO! 8 Basic (24CE model tested) — 8 digital inputs, 4 outputs, Ethernet
- LOGO! Soft Comfort V8.2+
- NETIO PowerBOX/PowerPDU (Modbus TCP slave)

## Configuration Steps

### 1. Set Static IPs on Both Devices
- LOGO! via front panel: `Network → IP address`
- NETIO PDU via web interface

### 2. Enable Modbus TCP on the Slave Device
- Modbus TCP is **disabled by default** on many devices
- Enable in the device's web interface
- Port: **502**

### 3. Create Ethernet Connection in LOGO! Soft Comfort (LOGO! as Master)
`Tools → Create Ethernet connection` → configure:
- Target device IP
- Port 502
- Variable mappings to Modbus registers

### 4. Program PLC Logic
Use Modbus TCP Client block in LOGO! Soft Comfort:
- FC codes for read/write
- Action functions: 0=off, 1=on, 2=short off, 3=short on, 4=toggle

## Key Notes for Your Project

- This AN shows LOGO! as **master** — same principle applies when LOGO! reads from ESP32 slave
- LOGO! Soft Comfort uses "Ethernet connection" blocks to define Modbus TCP client connections
- Each connection block maps LOGO! variables to remote Modbus registers
