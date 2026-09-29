# Configuring LOGO! 8 for Modbus TCP Communication
> Source: https://infoneva.com/en/knowledge/configuring-logo-8-modbus-tcp-communication

## Requirements

- LOGO! 8 firmware: **FS04, version 1.81.2 or higher**
- LOGO! Soft Comfort: **V8.2 or later**

## Network Setup

1. Connect LOGO! 8 to Ethernet network
2. Assign static IP via device web server or LOGO! Soft Comfort

## Configure LOGO! as Modbus TCP Server (Slave)

1. Open LOGO! Soft Comfort
2. Navigate to **Network** tab in function block palette
3. Insert **"Modbus TCP Server"** block
4. Configure:
   - Device address (Unit ID): **1**
   - Port: **502** (default, fixed)
5. Connect block to program logic
6. Download configuration to LOGO! 8

## Configure LOGO! as Modbus TCP Client (Master)

1. Insert **"Modbus TCP Client"** block
2. Configure:
   - Target device IP address
   - Port: **502**
   - Polling interval and timeout
   - Function code (e.g., FC03 read holding, FC06 write single)
   - Starting address and quantity
   - Variable mapping

## Testing

- Use **Modbus Poll** or **ModScan** to test from PC
- Monitor via LOGO! web server or Soft Comfort diagnostics

## Troubleshooting

| Issue | Detail |
|-------|--------|
| Max connections | 16 concurrent client connections |
| Register limit | Limited registers per transaction — check manual |
| Data type | 16-bit integer only; combine registers for 32-bit |
| Firewall | Verify port 502 is accessible |
