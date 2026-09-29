# node-red-contrib-modbus — Official Documentation
> Source: https://flows.nodered.org/node/node-red-contrib-modbus

## Overview

"The all in one Modbus TCP, UDP and Serial contribution long term supported package for Node-RED."

- **Current Version:** 5.45.2
- **Install:** `npm install node-red-contrib-modbus`

## Available Nodes (14 total)

| Node | Purpose |
|------|---------|
| `modbus-client` | Shared config: IP, port, Unit ID |
| `modbus-read` | Poll registers at fixed interval |
| `modbus-getter` | One-shot read triggered by message |
| `modbus-flex-getter` | Dynamic read — config from payload |
| `modbus-write` | Write coils or registers |
| `modbus-flex-write` | Dynamic write — config from payload |
| `modbus-server` | Act as a Modbus slave (for testing) |
| `modbus-queue-info` | Monitor queue status |
| `modbus-flex-connector` | Dynamic connection switching |
| `modbus-io-config` | I/O configuration mapping |
| `modbus-response` | Handle raw responses |
| `modbus-response-filter` | Filter response messages |
| `modbus-flex-sequencer` | Sequence multiple operations |
| `modbus-flex-fc` | Custom function codes |

## Supported Transports

- **TCP** (standard Modbus TCP/IP)
- **Serial RTU buffered**
- **Serial ASCII**
- **C701** and **Telnet** protocols

## Per-Unit Queueing

Supports per-unit queueing and round-robin scheduling — important when polling multiple devices.

## Debug Output

```bash
DEBUG=contribModbus*,modbus-serial node-red -v
```

## Requirements

- Node.js LTS versions
- Source: ES2019, Deployment: ES2015
