# Using Modbus with Node-RED — FlowFuse Guide
> Source: https://flowfuse.com/node-red/protocol/modbus/

## Overview

Node-RED can create web-based dashboards displaying production data from industrial equipment via Modbus TCP.

## Installation

1. Node-RED menu → **Manage Palette**
2. Search: `node-red-contrib-modbus` → Install
3. Also install: `@flowfuse/node-red-dashboard` for visualization

## Modbus Data Types

| Type | Bits | FC Read | FC Write |
|------|------|---------|----------|
| Output Coil | 1-bit | FC1 | FC5/FC15 |
| Discrete Input | 1-bit | FC2 | Read-only |
| Input Register | 16-bit | FC4 | Read-only |
| Holding Register | 16-bit | FC3 | FC6/FC16 |

## Building a Modbus Server (for testing)

Add a `modbus-server` node configured for:
- Up to 1000 coils
- Up to 1000 discrete inputs
- Up to 1000 holding registers
- Up to 1000 input registers

## Sending Test Data

**Coils:** quantity=5, boolean payload, inject every 20s

**Registers:** quantity=4, numerical payload (`random() * 200`)

Use join nodes to combine inject messages into arrays before writing.

## Reading Data

`modbus-read` node settings:
- Start address (0-based)
- Quantity
- Poll interval (e.g., 1 second)
- FC1 for coils, FC3 for holding registers

## Splitting Array Output

```javascript
// Change node or function node to extract individual values
msg.payload = msg.payload[0]  // Get first coil/register
```

## Dashboard Styling

Apply conditional colors:
- Green for `true`/ON
- Red for `false`/OFF

Use dashboard text widgets with template styling.

## Real-World Example Tags

| Tag | Type |
|-----|------|
| isEStopReleased | Coil |
| isMotorSwitchedOn | Coil |
| isMotorRunning | Coil |
| MotorAmps | Register |
| motorHourMeter | Register |
| beltTonsPerHour | Register |

## Best Practices

- Group consecutive addresses to minimize communication overhead
- Set poll rates based on data criticality (fast for safety signals, slow for totals)
