# Siemens LOGO! 8 Ethernet Communication: Protocol Support and Configuration
> Source: https://industrialmonitordirect.com/blogs/knowledgebase/siemens-logo-8-ethernet-communication-protocol-support-and-configuration

## Overview

The LOGO! 8 integrated Ethernet port supports two industrial protocols simultaneously — no manual selection needed.

## Supported Protocols

| Protocol | Standard | Primary Use | Concurrent |
|----------|----------|-------------|------------|
| SIMATIC S7 | Siemens Proprietary | Siemens HMIs, SCADA, PLCs | Yes |
| Modbus TCP/IP | RFC 793 | Third-party SCADA, HMIs | Yes |

**Connection Limit:** ~8 concurrent connections total (combined S7 + Modbus TCP)

## Configuration Steps

1. Configure static IP address, subnet mask, and gateway in Device Configuration
2. Define Data Blocks in LOGO! Soft Comfort for S7 communication
3. Map identical data blocks to Modbus register addresses automatically
4. No separate Modbus configuration required beyond variable programming

## Address Mapping Reference

| Data Type | S7 Access Area | Modbus Register Type | Notes |
|-----------|----------------|----------------------|-------|
| Digital Inputs (I) | Process Input Image | Discrete Inputs (1x): 10001–10128 | Read-only |
| Digital Outputs (Q) | Process Output Image | Coils (0x): 00001–00128 | Read/Write |
| Analog Inputs (AI) | Process Input Image | Input Registers (3x): 30001–30064 | Read-only |
| Flags/Memory (M) | Memory Area | Holding Registers (4x): 40001–40320 | Read/Write |
| User Data Blocks | Data Blocks (DB) | Holding Registers (4x): 40401–40999 | Program-defined |

> Note: These are 1-based addresses. Subtract 1 when using 0-based tools like node-red-contrib-modbus.

## Troubleshooting

| Problem | Solution |
|---------|---------|
| Connection failure | Verify static IP and subnet; ping device |
| S7 timeout | Confirm rack=0, slot=1 in client config |
| Modbus errors | Check register type and offset (0-based vs 1-based) |
| Data mismatch | Verify data types (Word vs DWord); confirm big-endian |
| Resource exhaustion | Monitor active client count — limit is ~8 combined |
