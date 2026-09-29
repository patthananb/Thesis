# How to Use Node-RED with Modbus — Steve's Node-RED Guide
> Source: https://stevesnoderedguide.com/node-red-modbus

## Overview

Practical guide for reading and controlling Modbus devices over TCP/IP using Node-RED.

## Installation

1. Node-RED menu → **Manage Palette**
2. Install: `node-red-contrib-modbus` (11+ nodes)

## Key Nodes

| Node | Use |
|------|-----|
| `modbus-getter` | Fixed reads (config inside node) |
| `modbus-flex-getter` | Dynamic reads (config from message) |
| `modbus-write` | Write to server |

## Server Configuration (modbus-client)

| Setting | Value |
|---------|-------|
| IP address | Device IP |
| Port | 502 |
| TCP type | DEFAULT |
| Unit ID | 1 |

## Supported Function Codes

| FC | Operation |
|----|-----------|
| FC1 | Read Coils |
| FC2 | Read Discrete Inputs |
| FC3 | Read Holding Registers |
| FC4 | Read Input Registers |

## Reading Buffer Data

### 16-bit Integer
```javascript
const buf = Buffer.from(msg.payload.buffer);
const value = buf.readUInt16BE();
msg.value = value;
return msg;
```

### 32-bit Integer
```javascript
const buf = Buffer.from(msg.payload.buffer);
const value = buf.readUInt32BE();
msg.value = value;
return msg;
```

### 32-bit Float
```javascript
const buf = Buffer.from(msg.payload.buffer);
const value = buf.readFloatBE();
msg.value = value;
return msg;
```

## Flex Getter Config Pattern

```javascript
var fc = 3;       // FC3 = holding registers
var sa = 0;       // start address
var qty = 2;      // quantity
msg.payload = {
  value: msg.payload,
  fc: fc,
  unitid: 1,
  address: sa,
  quantity: qty
};
return msg;
```

## Endianness

| Format | Methods |
|--------|---------|
| Big Endian (standard) | `readUInt16BE()`, `readUInt32BE()`, `readFloatBE()` |
| Little Endian | `readUInt16LE()`, `readUInt32LE()`, `readFloatLE()` |

> LOGO! 8 uses **Big Endian**

## Common Problem: Sleeping Nodes

When poll intervals are long (~2+ min), nodes enter "sleep" state and silently fail.

**Fix:** Send read signals via dual paths. Check message IDs to detect failures and trigger retries.

## Quick Reference — Address and FC Combinations

| Goal | FC | Address | Quantity |
|------|----|---------|----------|
| 4× 16-bit int from addr 0 | FC3 | 0 | 4 |
| 4× 16-bit int from addr 8 | FC3 | 8 | 4 |
| 4× 32-bit int from addr 0 | FC3 | 0 | 8 |
| 4× 32-bit float from addr 0 | FC3 | 0 | 8 |
| 8 coils from addr 0 | FC1 | 0 | 8 |
