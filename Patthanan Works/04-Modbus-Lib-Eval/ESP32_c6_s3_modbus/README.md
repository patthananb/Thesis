# ESP32-S3 DUT Modbus Library Evaluation

ESP32-C6 runs the mock Modbus RTU slave. ESP32-S3 is the device under test (DUT). Each PlatformIO environment flashes one candidate library's RTU master code onto the S3 and exercises it against the C6 mock for FC3 / FC6 / FC16.

Inputs and write-ups live in [docs/](docs/) — survey PDF, generated DOCX report, evaluation XLSX.

```text
Test path: ESP32-S3 DUT -> RS485 -> ESP32-C6 mock slave
```

## Hardware

| Role | Board |
|------|-------|
| RTU slave fixture | ESP32-C6 DevKitC-1 |
| DUT | ESP32-S3 4D Systems Gen4 R8N16 |

## RS485 Wiring

Use an auto-direction RS485 transceiver (e.g. MAX13487). No DE/RE wiring needed.

| Board | Signal | GPIO |
|-------|--------|------|
| ESP32-S3 DUT | TX to RS485 DI/TXD | 9 |
| ESP32-S3 DUT | RX from RS485 RO/RXD | 8 |
| ESP32-C6 fixture | TX to RS485 DI/TXD | 4 |
| ESP32-C6 fixture | RX from RS485 RO/RXD | 5 |

Connect RS485 A-to-A, B-to-B, and common GND between both boards.

## Evaluation policy

- Each DUT env is a small Arduino sketch (or ESP-IDF `app_main`) that uses that candidate's own Modbus master code path to poll the C6 mock.
- Code style is intentionally Arduino-IDE-flat: no project-level OOP, no shared harness, no FreeRTOS tasks beyond what the library starts internally. Calling into a library's own classes is fine — those are upstream.
- When a candidate exposes a usable Modbus master library (eModbus, emelianov/modbus-esp8266, 4-20ma/ModbusMaster, esp-modbus), the DUT uses it directly.
- When the candidate is a gateway sketch that hand-rolls RTU on raw `HardwareSerial` (vwetter, harihanv, tobiasfaust), the DUT mirrors that approach.
- Candidates that are not Arduino- or ESP-IDF-buildable on the S3 (ESPHome, ArduinoRS485 ESP32 incompatibility, zivillian's PIO/AsyncWebServer clash on Arduino core 3) are evaluated either with their underlying library on a clean DUT sketch, or excluded with a documented reason.

## PlatformIO environments

10 envs total — 1 C6 fixture, 7 Arduino S3 DUT envs, 2 ESP-IDF S3 DUT envs.

| Env | Framework | DUT source | Library exercised |
|-----|-----------|------------|-------------------|
| `esp32-c6-fixture` | arduino | [src/ESP32C6/main.cpp](src/ESP32C6/main.cpp) | raw RTU slave (fixture only) |
| `dut_rob2011_arduino_s3` | arduino | [src/dut/rob2011/main.cpp](src/dut/rob2011/main.cpp) | emelianov/modbus-esp8266 `ModbusRTU` |
| `dut_vwetter_arduino_s3` | arduino | [src/dut/vwetter/main.cpp](src/dut/vwetter/main.cpp) | raw `HardwareSerial` (vwetter has no library) |
| `dut_zivillian_arduino_s3` | arduino | [src/dut/zivillian/main.cpp](src/dut/zivillian/main.cpp) | eModbus `ModbusClientRTU` (the lib their gateway wraps) |
| `dut_harihanv_arduino_s3` | arduino | [src/dut/harihanv/main.cpp](src/dut/harihanv/main.cpp) | raw `HardwareSerial` (ArduinoRS485 unusable on ESP32) |
| `dut_tobiasfaust_arduino_s3` | arduino | [src/dut/tobiasfaust/main.cpp](src/dut/tobiasfaust/main.cpp) | raw `HardwareSerial` (Solax gateway lib not reusable) |
| `dut_emodbus_arduino_s3` | arduino | [src/dut/emodbus/main.cpp](src/dut/emodbus/main.cpp) | eModbus `ModbusClientRTU` (direct) |
| `dut_namnam_iot_arduino_s3` | arduino | [src/dut/namnam_iot/main.cpp](src/dut/namnam_iot/main.cpp) | 4-20ma/ModbusMaster (used by NamNamIoT's `Modbus_RTU.ino`) |
| `dut_esp_modbus_espidf_s3` | espidf | [src/dut/esp_modbus/main.c](src/dut/esp_modbus/main.c) | esp-modbus v2 `mbc_master_send_request` |
| `dut_maxx_ukoo_espidf_s3` | espidf | [src/dut/maxx_ukoo/main.c](src/dut/maxx_ukoo/main.c) | esp-modbus (same lib maxx-ukoo wraps in their gateway) |

## Excluded from PlatformIO

| Candidate | Native framework | Reason for exclusion |
|-----------|------------------|----------------------|
| `rosenrot00/esphome_modbus_bridge` | ESPHome | ESPHome is its own toolchain (`esphome compile`), not a PlatformIO framework. Evaluate with `esphome` directly. |

## Testing

Build all 8 Arduino envs from the project directory:

```bash
pio run \
  -e esp32-c6-fixture \
  -e dut_rob2011_arduino_s3 \
  -e dut_vwetter_arduino_s3 \
  -e dut_zivillian_arduino_s3 \
  -e dut_harihanv_arduino_s3 \
  -e dut_tobiasfaust_arduino_s3 \
  -e dut_emodbus_arduino_s3 \
  -e dut_namnam_iot_arduino_s3
```

ESP-IDF envs (`dut_esp_modbus_espidf_s3`, `dut_maxx_ukoo_espidf_s3`) require a build path with no whitespace. See [ESP-IDF build path requirement](#esp-idf-build-path-requirement) below.

Expected build status on 2026-05-13 with PlatformIO Core 6.1.19 and pioarduino `platform-espressif32` 55.3.38:

```text
Environment                 Status    Duration
--------------------------  --------  ------------
esp32-c6-fixture            SUCCESS   00:00:07
dut_rob2011_arduino_s3      SUCCESS   00:00:09
dut_vwetter_arduino_s3      SUCCESS   00:00:08
dut_zivillian_arduino_s3    SUCCESS   00:00:14
dut_harihanv_arduino_s3     SUCCESS   00:00:08
dut_tobiasfaust_arduino_s3  SUCCESS   00:00:08
dut_emodbus_arduino_s3      SUCCESS   00:00:12
dut_namnam_iot_arduino_s3   SUCCESS   00:00:08
dut_esp_modbus_espidf_s3    SUCCESS   00:00:49  (from /tmp/modbus_eval_real, see below)
dut_maxx_ukoo_espidf_s3     SUCCESS   00:00:49  (from /tmp/modbus_eval_real, see below)
```

## ESP-IDF build path requirement

The pioarduino `platform-espressif32` espidf builder appends an unquoted `-fmacro-prefix-map=$PROJECT_DIR=.` to the compiler command. The current project lives under `/Users/bean/work/Senior Project/modbus_lib_eval/ESP32_c6_s3_modbus`, and the unescaped space in `Senior Project` makes `gcc` split the flag and fail with `invalid argument '/Users/bean/work/Senior' to '-fmacro-prefix-map'`. A second early check in `espidf.py` also rejects build paths that contain whitespace.

Workaround: build the two ESP-IDF envs from a no-space copy of the project. The `build_dir = /tmp/pio_modbus_build` line in `platformio.ini` already moves PlatformIO's `.pio/build` tree to a no-space path, but `PROJECT_DIR` itself still needs to be space-free.

```bash
rsync -a --delete \
  --exclude='.pio' --exclude='.git' \
  --exclude='lib/esp-modbus/test_apps' \
  --exclude='lib/esp-modbus/docs' \
  --exclude='lib/esp32-modbus-tcp2rtu/front/node_modules' \
  "/Users/bean/work/Senior Project/modbus_lib_eval/ESP32_c6_s3_modbus/" \
  /tmp/modbus_eval_real/

cd /tmp/modbus_eval_real
pio run -e dut_esp_modbus_espidf_s3 -e dut_maxx_ukoo_espidf_s3
```

A permanent fix is to relocate or rename the parent directory so it contains no whitespace (e.g. `Senior_Project`); the Arduino envs work either way.

## Resource usage

Measured on 2026-05-13 with PlatformIO Core 6.1.19, pioarduino `platform-espressif32` 55.3.38, and ESP-IDF 5.5.4. Arduino envs use the `4d_systems_esp32s3_gen4_r8n16` board (3 MB app partition, 320 KB RAM). The C6 fixture uses `esp32-c6-devkitc-1` (1.25 MB app partition, 320 KB RAM). ESP-IDF envs use the same S3 board with default IDF partitions (16 MB app slot). Runtime column captured on 2026-05-14 hardware run against the C6 fixture; each cycle reports `>>` step results and a `CYCLE SUMMARY: n/m PASS` line — see `results/runtime_*.txt`.

| Env | Build | Flash used | Flash total | Flash % | RAM used | RAM total | RAM % | Runtime |
|-----|-------|------------|-------------|---------|----------|-----------|-------|---------|
| `esp32-c6-fixture` | SUCCESS | 252882 B | 1310720 B | 19.3% | 13852 B | 327680 B | 4.2% | fixture (no test) |
| `dut_rob2011_arduino_s3` | SUCCESS | 310437 B | 3145728 B | 9.9% | 22156 B | 327680 B | 6.8% | PASS 20/20 |
| `dut_vwetter_arduino_s3` | SUCCESS | 300501 B | 3145728 B | 9.6% | 21996 B | 327680 B | 6.7% | PASS 20/20 |
| `dut_zivillian_arduino_s3` | SUCCESS | 384105 B | 3145728 B | 12.2% | 22932 B | 327680 B | 7.0% | PASS 20/20 |
| `dut_harihanv_arduino_s3` | SUCCESS | 300213 B | 3145728 B | 9.5% | 21996 B | 327680 B | 6.7% | PASS 24/24 |
| `dut_tobiasfaust_arduino_s3` | SUCCESS | 300157 B | 3145728 B | 9.5% | 21996 B | 327680 B | 6.7% | PASS 20/20 |
| `dut_emodbus_arduino_s3` | SUCCESS | 384033 B | 3145728 B | 12.2% | 22940 B | 327680 B | 7.0% | PASS 20/20 |
| `dut_namnam_iot_arduino_s3` | SUCCESS | 301573 B | 3145728 B | 9.6% | 22292 B | 327680 B | 6.8% | PASS 20/20 |
| `dut_esp_modbus_espidf_s3` | SUCCESS¹ | 269553 B | 16777216 B | 1.6% | 14448 B | 327680 B | 4.4% | PASS 24/24 |
| `dut_maxx_ukoo_espidf_s3` | SUCCESS¹ | 269517 B | 16777216 B | 1.6% | 14448 B | 327680 B | 4.4% | PASS 24/24 |

¹ ESP-IDF envs built from `/tmp/modbus_eval_real` (no-space path) — see workaround above.

The three "raw RTU" sketches (vwetter, harihanv, tobiasfaust) sit at the Arduino core baseline (≈300 KB flash) because they pull in nothing beyond `HardwareSerial`. The two eModbus envs (zivillian, emodbus) cost ≈84 KB extra for the async stack. Rob2011's emelianov library and NamNamIoT's ModbusMaster are middleweights at ≈10 KB above the baseline. The two ESP-IDF envs are smaller because the ESP-IDF startup path is leaner than the Arduino-on-IDF startup. All nine DUT envs exercised the C6 fixture for ≥5 cycles of FC3 / FC6 / FC16 with zero failed steps.

## Latency / round-trip performance

Each DUT now times every Modbus call with `micros()` (Arduino) or `esp_timer_get_time()` (ESP-IDF) and prints `>> Tx ...: PASS [us=N]`. Captured 30 s of serial per env on 2026-05-14 against the same C6 fixture at 9600 8N1. Each env produced ~7 cycles, so 31–32 timed samples per env. Raw logs in `results/runtime_*.txt`; per-step stats in `results/latency_summary.json`.

Wire-time minimums at 9600 8N1 (1 char = 1.042 ms) with a 3.5-char (~3.65 ms) inter-frame silence:

| Step | Req bytes | Resp bytes | Minimum (ms) |
|------|---------:|----------:|-------------:|
| FC3 read 5 regs | 8 | 15 | ~27.6 |
| FC6 write 1 reg | 8 | 8 | ~20.3 |
| FC3 read 1 reg | 8 | 7 | ~19.3 |
| FC16 write 3 regs | 14 | 8 | ~26.6 |

### Round-trip across all 4 steps (per env)

| Env | N | min (ms) | mean (ms) | p50 (ms) | p95 (ms) | max (ms) |
|-----|--:|---------:|----------:|---------:|---------:|---------:|
| `dut_rob2011_arduino_s3` | 31 | 27.97 | 33.39 | 29.97 | 39.97 | 39.97 |
| `dut_vwetter_arduino_s3` | 31 | 22.16 | 27.90 | 24.16 | 34.16 | 34.16 |
| `dut_zivillian_arduino_s3` | 32 | 24.00 | 32.88 | 28.99 | 36.00 | 132.34 |
| `dut_harihanv_arduino_s3` | 31 | 22.18 | 28.01 | 24.18 | 34.18 | 34.18 |
| `dut_tobiasfaust_arduino_s3` | 31 | 22.15 | 27.73 | 24.16 | 34.16 | 34.16 |
| `dut_emodbus_arduino_s3` | 31 | 24.00 | 30.25 | 26.00 | 36.00 | 36.00 |
| `dut_namnam_iot_arduino_s3` | 31 | 19.16 | 24.45 | 20.79 | 30.62 | 30.75 |
| `dut_esp_modbus_espidf_s3` | 32 | 22.28 | 27.97 | 27.54 | 34.14 | 34.27 |
| `dut_maxx_ukoo_espidf_s3` | 32 | 22.34 | 27.82 | 27.29 | 34.40 | 34.53 |

### Mean / max per step (ms)

| Env | T1 FC3 (5 regs) | T2 FC6 | T3 FC3 (1 reg) | T4 FC16 (3 regs) |
|-----|----------------:|-------:|---------------:|-----------------:|
| `dut_rob2011_arduino_s3` | 35.95 / 35.95 | 29.97 / 29.97 | 27.97 / 27.97 | 39.97 / 39.97 |
| `dut_vwetter_arduino_s3` | 31.14 / 31.14 | 23.91 / 24.16 | 22.91 / 23.16 | 34.03 / 34.16 |
| `dut_zivillian_arduino_s3` | 45.52 / 132.34 | 26.00 / 26.00 | 24.00 / 24.00 | 36.00 / 36.00 |
| `dut_harihanv_arduino_s3` | 31.16 / 31.16 | 24.05 / 24.18 | 23.05 / 23.18 | 34.18 / 34.18 |
| `dut_tobiasfaust_arduino_s3` | 31.14 / 31.14 | 23.66 / 24.16 | 22.53 / 23.16 | 34.03 / 34.16 |
| `dut_emodbus_arduino_s3` | 33.98 / 33.98 | 26.00 / 26.00 | 25.50 / 26.00 | 36.00 / 36.00 |
| `dut_namnam_iot_arduino_s3` | 27.80 / 28.06 | 20.49 / 20.79 | 19.45 / 19.74 | 30.45 / 30.75 |
| `dut_esp_modbus_espidf_s3` | 31.23 / 31.52 | 23.80 / 24.14 | 22.86 / 23.20 | 33.98 / 34.27 |
| `dut_maxx_ukoo_espidf_s3` | 31.02 / 31.60 | 23.59 / 23.89 | 22.64 / 22.93 | 34.03 / 34.53 |

### Observations

- **`namnam_iot` (4-20ma `ModbusMaster`)** is fastest end-to-end (19.16 ms FC3-1reg minimum, only ~0 ms over the wire-time floor of 19.3 ms). Smallest, most direct sync RTU implementation.
- **Raw-RTU sketches** (`vwetter`, `harihanv`, `tobiasfaust`) all land ~2-3 ms over wire-time because the receive loop uses a 4 ms `FRAME_GAP_MS` silence detector instead of byte-counting from the FC.
- **ESP-IDF `esp-modbus` and `maxx-ukoo`** (same library underneath) match the raw RTU latency within noise (22-34 ms per step). Confirms the official Espressif library is at wire-speed.
- **eModbus envs** (`emodbus`, `zivillian`) sit ~2 ms higher per step. The async client polls the result with a 2 ms `delay(2)`, which gives the quantized 24/26/36 ms values.
- **`rob2011`** (`emelianov/modbus-esp8266` sync API) is the slowest, ~6-8 ms above the wire-time floor — the `mb.task()` polling loop sleeps in 2 ms ticks _and_ adds another internal 1 ms quantum, hence the clean 28/30/36/40 ms numbers.
- **Outlier**: `zivillian` T1 has one 132 ms sample (first cycle right after the eModbus FreeRTOS worker task is scheduled). Subsequent cycles are at the 33 ms baseline. p95 stays under 100 ms.

## Flash test plan

Flash the C6 fixture once:

```bash
pio run -e esp32-c6-fixture --target upload
```

Then flash one DUT env at a time and monitor:

```bash
pio run -e dut_rob2011_arduino_s3 --target upload && pio device monitor -e dut_rob2011_arduino_s3
pio run -e dut_vwetter_arduino_s3 --target upload && pio device monitor -e dut_vwetter_arduino_s3
pio run -e dut_zivillian_arduino_s3 --target upload && pio device monitor -e dut_zivillian_arduino_s3
pio run -e dut_harihanv_arduino_s3 --target upload && pio device monitor -e dut_harihanv_arduino_s3
pio run -e dut_tobiasfaust_arduino_s3 --target upload && pio device monitor -e dut_tobiasfaust_arduino_s3
pio run -e dut_emodbus_arduino_s3 --target upload && pio device monitor -e dut_emodbus_arduino_s3
pio run -e dut_namnam_iot_arduino_s3 --target upload && pio device monitor -e dut_namnam_iot_arduino_s3
```

For the two ESP-IDF envs, upload from `/tmp/modbus_eval_real`:

```bash
cd /tmp/modbus_eval_real
pio run -e dut_esp_modbus_espidf_s3 --target upload && pio device monitor -e dut_esp_modbus_espidf_s3
pio run -e dut_maxx_ukoo_espidf_s3 --target upload && pio device monitor -e dut_maxx_ukoo_espidf_s3
```

Each cycle on the serial monitor should look like (Arduino DUTs):

```text
=== DUT: <candidate> ===
[DUT] ... ready

--- Cycle 1 ---
T1: FC3 read regs 0..4
  reg[0]=100
  reg[1]=200
  reg[2]=300
  reg[3]=400
  reg[4]=500
>> T1 FC3 read 0..4: PASS
T2: FC6 write reg 0 = 4242
>> T2 FC6 write reg 0: PASS
T3: FC3 read reg 0 (verify)
  reg[0]=4242
>> T3 FC3 verify write: PASS
T4: FC16 write regs 0..2 = 100,200,300 (restore)
>> T4 FC16 restore: PASS
CYCLE SUMMARY: 4/4 PASS
```

For the ESP-IDF DUTs the same content appears via `ESP_LOGI` lines tagged `DUT_ESP_MODBUS` / `DUT_MAXX_UKOO`.

## Notes on Arduino source guarding

All Arduino sources in `src/` are wrapped with `#ifdef ARDUINO ... #endif`. The Arduino core defines `ARDUINO` automatically, so these files compile normally under the arduino envs. Under `framework = espidf`, the same files become empty translation units, so the IDF envs don't fail trying to find `<Arduino.h>`.

The two ESP-IDF `main.c` files use the matching guards `#ifdef DUT_ESP_MODBUS` and `#ifdef DUT_MAXX_UKOO`. Only the env that defines the right macro emits an `app_main`, which keeps both files in the IDF `main` component without symbol collisions.
