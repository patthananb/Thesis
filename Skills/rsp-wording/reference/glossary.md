# RSP Terminology Glossary (KMUTNB IoT blog)

First-mention form is `Thai (English gloss)`. After first mention, use either alone.
Product names, part numbers, pins, registers, units, and code stay in English/ASCII.

## Protocols & communication

| Concept | RSP Thai wording |
|---|---|
| protocol | โพรโทคอล |
| messaging protocol | โพรโทคอลสำหรับการส่งข้อความ (messaging protocol) |
| request–response | แบบร้องขอ-ตอบสนอง (request–response) |
| publish–subscribe | รูปแบบผู้เผยแพร่-ผู้สมัครรับข้อความ (publisher–subscriber pattern) |
| publish (a message) | เผยแพร่ข้อความ / การส่งข้อความ (Message Publication) |
| subscribe | สมัครรับข้อความ  *(never "สมัครสมาชิก")* |
| publisher | ผู้เผยแพร่ข้อความ (publisher) |
| subscriber | ผู้สมัครรับข้อความ (subscriber) |
| broker | โบรกเกอร์ (broker หรือ ตัวกลาง / นายหน้า) |
| client | ไคลเอนต์ (client) |
| topic | หัวข้อ (topic); ตัวแบ่งระดับ (Topic Level Separator) `/` |
| QoS | ระดับคุณภาพการให้บริการ (Quality of Service, QoS) — ระดับ 0/1/2 |
| retained message | ข้อความที่เก็บรักษาไว้ (retained message) |
| last will & testament | การส่งข้อความครั้งสุดท้าย (last will and testament) |
| keep-alive | ข้อความ Keep-Alive (แพ็กเกต `PINGREQ`/`PINGRESP`) |
| packet | แพ็กเกต (packet) |
| MQTT | MQTT (เอ็ม-คิว-ที-ที) ย่อมาจาก MQ Telemetry Transport |

## Modbus

| Concept | RSP Thai wording |
|---|---|
| master / slave | มาสเตอร์ (master) / สเลฟ (slave) |
| poll | สำรวจ (poll) |
| slave address / device address | หมายเลขอุปกรณ์สเลฟ (slave address) / หมายเลขอุปกรณ์ (Device Address) |
| function code | รหัสคำสั่ง (Function Code, FC) — เช่น FC=0x03/0x04/0x06/0x10 |
| input registers | รีจิสเตอร์อินพุต (Input Registers) — อ่านด้วย FC=0x04 |
| holding registers | รีจิสเตอร์สำหรับการตั้งค่า (Holding Registers) — อ่านด้วย FC=0x03 |
| register (2 bytes) | รีจิสเตอร์ ขนาด 2 ไบต์ (16 บิต) |
| big-endian | เข้ารหัสแบบ big-endian (คงคำภาษาอังกฤษ) |
| CRC | การตรวจสอบความถูกต้องแบบ 16-bit CRC (cyclic redundancy check) |
| request/response frame | เฟรมข้อมูล (Request Frame / Response Frame) |
| MBAP header | ส่วนหัว MBAP (Modbus Application Protocol Header) |
| Modbus RTU / TCP | Modbus RTU (ผ่านบัส RS-485) / Modbus TCP (พอร์ต 502) |
| edge gateway | เอดจ์เกตเวย์ (edge gateway) |

## RS-485 / electronics

| Concept | RSP Thai wording |
|---|---|
| RS-485 bus | บัส RS-485 (TIA-485 / EIA-485) |
| differential signaling | การสื่อสารแบบดิฟเฟอเรนเชียล (Differential Signaling) |
| multi-drop / multi-point | เชื่อมต่อแบบหลายจุด (Multi-point / Multi-drop) |
| half/full duplex | ครึ่งดูเพล็กซ์ (Half-Duplex) / เต็มดูเพล็กซ์ (Full-Duplex) |
| A+/B- pair | สายสัญญาณหนึ่งคู่ A+ (non-inverting) และ B- (inverting) |
| transceiver | ตัวรับส่งสัญญาณ (Transceiver) — ตัวส่ง (Driver) / ตัวรับ (Receiver) |
| termination resistor | ตัวต้านทานปิดปลายสาย (Termination Resistor) 120 Ω |
| failsafe biasing | การไบแอสแบบ Failsafe |
| USB-to-Serial bridge | วงจร USB-to-Serial Bridge (เช่น FT232RL, CH340) |

## Controllers & compute

| Concept | RSP Thai wording |
|---|---|
| microcontroller (MCU) | ไมโครคอนโทรลเลอร์ (Microcontroller: MCU) |
| embedded systems | ระบบสมองกลฝังตัว (Embedded Systems) |
| single-board computer (SBC) | คอมพิวเตอร์บอร์ดเดี่ยว (Single-Board Computer: SBC) |
| multi-core | หลายแกน (Multi-Core) — 32/64 บิต |
| SoC | ชิป …SoC (เช่น ชิป Espressif ESP32-S3) |
| ESP32-S3 CPU | ตัวประมวลผล Xtensa LX7 แบบสองแกน (32-bit dual-core) สูงสุด 240 MHz |
| wireless | Wi-Fi (IEEE 802.11 b/g/n, 2.4 GHz) และ Bluetooth / BLE 5.0 |
| flash / PSRAM / SRAM | หน่วยความจำแฟลช (Flash) / PSRAM / SRAM |
| UART | พอร์ตสื่อสารอนุกรม (UART) |
| firmware | เฟิร์มแวร์ |
| RTOS | ระบบปฏิบัติการเวลาจริง (RTOS, Real-Time OS) |
| multi-threading | การเขียนโปรแกรมแบบมัลติเธรด (Multi-Threading) |
| PLC | ตัวควบคุมโปรแกรมได้ (Programmable Logic Controller: PLC) |
| Arduino core / PlatformIO | Arduino core; ซอฟต์แวร์ PlatformIO (PIO) |

## Sensors, power meters, instruments

| Concept | RSP Thai wording |
|---|---|
| digital power meter | เพาเวอร์มิเตอร์แบบดิจิทัล (Digital Power Meter) |
| single/3-phase | แบบเฟสเดียว (Single-Phase) / แบบสามเฟส (3-Phase) |
| real power | กำลังไฟฟ้าที่ใช้งานจริง (Real Power: kW) |
| apparent power | กำลังไฟฟ้าที่ปรากฏ (Apparent Power: kVA) |
| reactive power | กำลังไฟฟ้ารีแอคทีฟ (Reactive Power: kVAr) |
| power factor | ค่าตัวประกอบกำลังไฟฟ้า (Power Factor) |
| active energy | พลังงานไฟฟ้าที่ใช้ (Active Energy: kWh) |
| voltage/current/frequency | แรงดันไฟฟ้า (V) / กระแสไฟฟ้า (I) / ความถี่ (Hz) |
| temperature & humidity sensor | โมดูลเซนเซอร์วัดอุณหภูมิและความชื้นสัมพัทธ์ |
| DIN rail mounting | ติดตั้งบนรางปีกนก (DIN Rail) |
| baud rate | ค่า Baudrate (บอด) |
| oscilloscope | ออสซิลโลสโคป (Oscilloscope) |
| multimeter | มัลติมิเตอร์ (Multimeter) |
| breadboard | เบรดบอร์ด / แผงต่อวงจร (Breadboard) |
| logic analyzer | เครื่องวิเคราะห์สัญญาณดิจิทัล (Logic Analyzer) |

## Software / IT layer

| Concept | RSP Thai wording |
|---|---|
| Linux / OS | ระบบปฏิบัติการ Linux |
| container / Docker | คอนเทนเนอร์ Docker; Docker Compose |
| database | ฐานข้อมูล; ฐานข้อมูลอนุกรมเวลา (time-series database) |
| dashboard | แดชบอร์ด |
| headless | การใช้งานแบบ Headless (ไม่ต่อจอแสดงผล) |
