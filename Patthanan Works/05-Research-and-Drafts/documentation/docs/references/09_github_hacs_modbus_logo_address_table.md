# hacs-modbus-logo — Authoritative LOGO! 8 Address Table
> Source: https://github.com/nos86/hacs-modbus-logo

## Overview

Custom Home Assistant integration for Modbus communication with Siemens LOGO! 8. Contains the most community-verified and complete address reference table.

## Complete Register Address Reference

| LOGO! Variable | Modbus Type | Address (0-based) | Notes |
|---|---|---|---|
| I1–I24 (Digital Inputs) | Discrete Input | 0 – 23 | Read-only, FC2 |
| Q1–Q20 (Digital Outputs) | Coil | 8192 – 8211 | Read/Write, FC1/FC5 |
| M1–M64 (Markers) | Coil | 8256 – 8319 | Read/Write, FC1/FC5 |
| V0.0–V850.7 (VM Bit) | Coil | 0 – 6807 | Read/Write, FC1/FC5 |
| AI1–AI8 (Analog Inputs) | Input Register | 0 – 7 | Read-only, FC4 |
| VW0–VW850 (VM Word) | Holding Register | 0 – 424 | Read/Write, FC3/FC6 |
| AQ1–AQ8 (Analog Outputs) | Holding Register | 512 – 519 | Read/Write, FC3/FC6 |
| AM1–AM64 (Analog Markers) | Holding Register | 528 – 591 | Read/Write, FC3/FC6 |

## Example Configuration

```yaml
modbus_logo:
  - name: plc
    type: tcp
    host: 10.148.0.32
    port: 502
    lights:
      - name: corridor
        address: 16          # V2.0 bit coil
        write_type: coil
        scan_interval: 1
        verify:
          input_type: coil
          address: 8192      # Q1 — verify output state
          sync: true
```

## sync Flag (v0.2.0+)

The `sync: true` flag synchronizes HA UI state with physical PLC output changes — prevents mismatch when hardware buttons change state externally.

> Warning: Monitor for feedback loops when using sync.

## Installation (Home Assistant HACS)

1. HACS → Custom repositories → add `https://github.com/nos86/hacs-modbus-logo`
2. Category: Integration
3. Restart Home Assistant
