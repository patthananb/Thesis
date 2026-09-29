# Interfacing with LOGO! 8 using Modbus TCP
> Source: https://blog.pundurs.lv/2019/05/13/interfacing-with-logo-8-using-modbus-tcp/

## Overview

Smart home project using Siemens LOGO! 8 with Modbus TCP. Uses Python `uModbus` library to communicate with LOGO! over Ethernet.

## Hardware Setup

- Siemens LOGO! 8 controller
- 24V power supply
- Ethernet to TP 10/100 switch
- Connected devices: Raspberry Pi, laptop
- 7 input buttons + one analog input (variable resistor)
- Relay outputs for testing

## Code Examples

### Reading Analog Values (FC4 — Input Registers)

```python
import socket
from umodbus import conf
from umodbus.client import tcp
from time import sleep as wait

conf.SIGNED_VALUES = True

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('192.168.0.3', 502))

# Read AI1 (analog input 1) — address 0
message = tcp.read_input_registers(slave_id=1, starting_address=0, quantity=1)

for i in range(1, 100000):
    response = tcp.send_message(message, sock)
    print(response, i)
    wait(0.01)

sock.close()
```

### Writing Coil Values (FC15 — Write Multiple Coils)

```python
import socket
from umodbus import conf
from umodbus.client import tcp

conf.SIGNED_VALUES = True

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('192.168.0.3', 502))

# Write M1–M4 markers: M1=ON, M2=OFF, M3=OFF, M4=OFF
# M1 starts at address 8256
message = tcp.write_multiple_coils(slave_id=1, starting_address=8256, values=[1, 0, 0, 0])
response = tcp.send_message(message, sock)
print(response)
sock.close()
```

## Key Takeaways

- LOGO! IP: `192.168.0.3`, Port: `502`, Unit ID: `1`
- AI1 analog input → FC4, address `0`
- M1 marker coil → FC15, starting address `8256`
- Uses Python `uModbus` library (also works with `pymodbus`)

## Resources

- uModbus library: https://pypi.org/project/uModbus/
