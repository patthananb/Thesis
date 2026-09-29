# Creating Modbus Configuration for a Siemens LOGO! — Home Assistant Community
> Source: https://community.home-assistant.io/t/creating-modbus-configuration-for-a-siemens-logo/535762

## Thread Summary

Real-world community experience connecting LOGO! 8 via Modbus TCP. Key lessons and working configurations.

## The #1 Lesson: Off-By-One Addressing

**Problem:** Getting 0.0 values when reading registers.

**Root cause:** Off-by-one addressing error.

> "Registers are addressed starting at zero. Therefore input registers numbered 1-16 are addressed as 0-15."

- Documented address `529` → request address `528`
- Documented address `8193` (Q1) → request address `8192`

## Working Configuration Example (YAML — adaptable to Node-RED)

```yaml
modbus:
  - name: "LOGO PLC"
    type: tcp
    host: 192.168.x.x
    port: 502
    binary_sensors:
      - name: "Output Q1"
        slave: 1
        address: 8192        # Q1 coil (0-based)
        input_type: coil
      - name: "Output Q2"
        slave: 1
        address: 8193        # Q2 coil
        input_type: coil
      - name: "Output Q3"
        slave: 1
        address: 8194        # Q3 coil
        input_type: coil
    sensors:
      - name: "Temperature"
        slave: 1
        address: 528         # AM1 analog marker (0-based)
        input_type: holding
        scale: 0.1           # Scale factor if needed
        swap: word
```

## Community Tips

- **Unit ID must be 1** (not 0)
- LOGO! 8.4+ has native MQTT — slightly easier than Modbus for simple monitoring
- Use `swap: word` for multi-register 32-bit values
- Scale factor: if LOGO! sends `321` for 32.1°C, use `scale: 0.1`

## Verified Working Coil Addresses

| Output | Address (0-based) |
|--------|------------------|
| Q1 | 8192 |
| Q2 | 8193 |
| Q3 | 8194 |
| Q8 | 8199 |
| Q9 | 8200 |
| Q10 | 8201 |
