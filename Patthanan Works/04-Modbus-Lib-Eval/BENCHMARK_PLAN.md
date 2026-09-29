# Modbus TCP Gateway Library Benchmark Plan

**Target:** ESP32-S3
**Goal:** Compile each of 9 candidate projects under a single PlatformIO workspace, run the same test fixture on identical hardware, capture comparable metrics, and auto-populate `evaluation_template.xlsx`.

---

## 1. Scope

### 1.1 Projects in scope (9)

| # | Project | Class | Framework | Form on disk |
|---|---|---|---|---|
| 1 | `Rob2011/ESP32.Modbus-TCP-gateway` | A | Arduino | single `.ino` sketch |
| 2 | `vwetter/esp32-modbus-gateway` | A | Arduino | `.ino` + `libraries.txt` |
| 3 | `zivillian/esp32-modbus-gateway` | P | Arduino + PlatformIO | full PIO project |
| 4 | `harihanv/esp32-modbus-gateway` | A | Arduino | multi-tab `.ino` (5 files) |
| 5 | `tobiasfaust/SolaxModbusGateway` | P | Arduino + PlatformIO | full PIO project |
| 6 | `eModbus/eModbus` | L | Arduino library | `library.json` library |
| 7 | `NamNamIoT/ESP32` | A | Arduino | examples using `emelianov/modbus-esp8266` |
| 8 | `maxx-ukoo/esp32-modbus-tcp2rtu` | I | ESP-IDF | full IDF project |
| 9 | `espressif/esp-modbus` | L | ESP-IDF | IDF component |

**Class legend:**

- **L** — Reusable library; bench firmware can be written against its API directly.
- **P** — Pre-existing PlatformIO project; build as-is, patch only what is needed for ESP32-S3 and the test fixture.
- **A** — Arduino `.ino` sketch(es); wrap into a PIO env (copy sources into `src/<env>/`).
- **I** — Pre-existing ESP-IDF project; build via `platform = espressif32, framework = espidf` or external `idf.py`.

### 1.2 Out of scope

- `rosenrot00/esphome_modbus_bridge` — ESPHome YAML toolchain; not part of this sweep.
- TLS/secure Modbus.
- Modbus ASCII (rare in deployed gateways; not common in candidate set).
- Power consumption measurement (no instrumentation available).

---

## 2. Test Fixture

### 2.1 Topology

```
+--------------------+   TCP/502    +-------------+   UART/RS485   +--------------+
| Host PC            | <----------> | ESP32-S3    | <------------> | RTU slave    |
| - pymodbus client  |    WiFi      | (DUT)       |   half-duplex  | (USB-RS485   |
| - pymodbus RTU     |              | Modbus      |                |  dongle on   |
|   slave            |              | gateway     |                |  host)       |
| - metrics logger   |              |             |                |              |
+--------------------+              +-------------+                +--------------+
                                           ^
                                           | USB serial (logs, JTAG)
                                           v
                                     host metrics collector
```

The host PC plays both roles: TCP client driving the bench, and RTU slave answering the gateway over a second USB-RS485 dongle. This keeps the topology to one ESP32-S3 board and one host PC.

### 2.2 Hardware

| Item | Part | Notes |
|---|---|---|
| DUT | ESP32-S3-DevKitC-1 (N16R8 or N8R8) | Single board reused across all envs |
| RS485 transceiver | MAX3485 (3.3 V) | Half-duplex; DE/RE tied together |
| RTU slave side | USB ↔ RS485 dongle on host | Driven by pymodbus |
| Bus termination | 120 Ω across A/B | Both ends if length > 1 m |
| Power | USB 5 V | No external supply |

### 2.3 Pin assignment (single config across all envs)

| Signal | GPIO | Reason |
|---|---|---|
| UART1 TX | GPIO17 | Free on S3, no strapping conflict |
| UART1 RX | GPIO18 | Same |
| DE/RE | GPIO5 | Easy to reach on DevKitC-1 |
| Status LED | GPIO48 (on-board RGB) | Boot-ready signal |
| Debug UART0 | USB CDC | Default S3 console |

Per-env overrides via `build_flags = -DBENCH_TX=17 -DBENCH_RX=18 -DBENCH_DE=5`.

### 2.4 Software fixture

- **Host RTU slave**: pymodbus 3.x, register map below, runs on `/dev/tty.usbserial-*` at 9600 8N1.
- **Host TCP client**: pymodbus 3.x async client, target DUT IP:502.
- **Coordinator script**: Python, invokes client, polls DUT serial console for boot timestamps / heap snapshots, writes `metrics_<env>.json`.

### 2.5 Register map (RTU slave)

| Range | Type | Count | Purpose |
|---|---|---|---|
| `40001–40010` | Holding (R/W) | 10 | Short read/write |
| `40011–40110` | Holding (R/W) | 100 | Medium read/write |
| `40111–40235` | Holding (R/W) | 125 | Max single-PDU read (FC03 limit) |
| `30001–30010` | Input (R) | 10 | FC04 path |
| `00001–00016` | Coil (R/W) | 16 | FC01/05/15 path |

Slave UID = `1`.

---

## 3. Test Cases

All cases run against the same register map, same UID, same baud rate. Each case writes one JSON record per env.

### 3.1 Sanity (must pass before any timing)

| Case | Action | Expected |
|---|---|---|
| `boot` | Power-up DUT, wait WiFi+RTU ready | Ready within 10 s |
| `read_one` | FC03 read 1 reg at 40001 | Correct value, no exception |
| `write_one` | FC06 write reg 40001, read back | Round-trip match |
| `exception` | FC03 read of unmapped reg 49999 | Modbus exception `0x02` returned |

A failure here marks the env "non-functional" and skips perf cases.

### 3.2 Latency (sequential)

For each (FC, count): 1000 sequential requests, single client, idle bus between requests.

| Case | FC | Reg count |
|---|---|---|
| `lat_fc03_10` | 03 | 10 |
| `lat_fc03_100` | 03 | 100 |
| `lat_fc03_125` | 03 | 125 |
| `lat_fc06_1` | 06 | 1 |
| `lat_fc16_10` | 16 | 10 |

Metrics: mean, p50, p95, p99, max, min, stddev.

### 3.3 Throughput (sustained)

60 s at fixed rate, FC03 of 10 regs, single client.

| Case | Target rate |
|---|---|
| `tput_10rps` | 10 req/s |
| `tput_50rps` | 50 req/s |
| `tput_100rps` | 100 req/s (likely saturates non-async libs) |

Metrics: achieved rate, drop count, error count, p99 latency under load.

### 3.4 Concurrency (multi-client)

Ramp simultaneous TCP clients 1 → 16 in steps of 2. Each client issues FC03 of 10 regs every 200 ms for 30 s.

Metrics: max sustained client count before error rate > 1 %, p99 latency per N.

### 3.5 Stress / robustness

| Case | Action | Expected |
|---|---|---|
| `bad_crc` | Inject corrupt frame from a side channel | Gateway rejects, no crash |
| `slow_slave` | Slave delays 500 ms | Gateway returns timeout exception, recovers |
| `slave_off` | RTU slave dropped mid-test | Gateway reports timeout, recovers when slave returns |
| `wifi_drop` | Disable AP for 10 s | Gateway reconnects, no reboot |

Pass/fail per env; recorded as boolean in the matrix.

---

## 4. Metrics Captured

### 4.1 Build-time / static

Captured by build scripts; available for all 9 envs regardless of functional pass.

| Metric | Source |
|---|---|
| Flash bytes used | `pio run -t size` (Arduino), `idf.py size` (IDF) |
| Flash bytes total | partition table / chip variant |
| Flash % used | derived |
| RAM `.data + .bss` bytes | size output |
| RAM total | chip RAM (SRAM + PSRAM if used) |
| RAM % used | derived |
| Build time (s) | `time pio run -e <env>` |
| Compiler warnings count | parse `pio run` output |
| Toolchain version | `xtensa-esp32s3-elf-gcc --version` |

### 4.2 Runtime / on-target

Captured by bench firmware over USB CDC. The bench firmware in classes L exposes these directly. For classes P/A/I, the firmware may not expose all of them; missing values logged as `null`.

| Metric | API |
|---|---|
| Free heap at idle | `esp_get_free_heap_size()` |
| Minimum free heap | `esp_get_minimum_free_heap_size()` |
| TCP task stack high-water | `uxTaskGetStackHighWaterMark()` |
| RTU task stack high-water | same |
| Boot-to-ready time (ms) | `esp_timer_get_time()` between reset and "ready" log line |
| WiFi connect time (ms) | timestamp delta |

### 4.3 Host-side perf

| Metric | Source |
|---|---|
| Latency mean / p50 / p95 / p99 / max | client wall clock per request |
| Throughput achieved (req/s) | counter / 60 s |
| Error count | response code != 0 OR no response |
| Dropped TCP connections | client socket error count |

---

## 5. PlatformIO Workspace Layout

```
modbus_bench/
├── platformio.ini             # 9 envs, shared [env] base
├── include/
│   └── bench_common.h         # pin defines, WiFi creds via -D, JSON log helpers
├── src/
│   ├── bench_eModbus/         # class L
│   │   └── main.cpp
│   ├── bench_espModbus/       # class L
│   │   └── main.c
│   ├── app_Rob2011/           # class A wrap
│   │   └── main.cpp           # adapted from modbus_gateway.ino
│   ├── app_vwetter/
│   ├── app_harihanv/
│   └── app_NamNamIoT/         # adapted from Modbus_Bridge example
├── ext_projects/              # class P + I, build via their own platformio.ini / CMake
│   ├── zivillian/             # symlink or copy
│   ├── tobiasfaust/
│   └── maxx-ukoo/
├── host/
│   ├── rtu_slave.py           # pymodbus serial slave
│   ├── bench_client.py        # TCP client, runs all test cases
│   ├── metrics_collector.py   # parses serial logs + client output → JSON
│   └── requirements.txt
├── scripts/
│   ├── build_all.sh           # iterate envs, capture sizes
│   ├── run_one.sh             # flash + run + collect for one env
│   ├── run_all.sh             # sweep
│   └── fill_excel.py          # JSON → evaluation_template.xlsx
└── results/
    └── metrics_<env>.json
```

### 5.1 `platformio.ini` skeleton

```ini
[platformio]
default_envs = bench_eModbus

[env]
platform = espressif32@~6.7.0
board = esp32-s3-devkitc-1
framework = arduino
monitor_speed = 115200
build_flags =
    -DBENCH_TX=17
    -DBENCH_RX=18
    -DBENCH_DE=5
    -DBENCH_BAUD=9600

[env:bench_eModbus]
build_src_filter = +<bench_eModbus/>
lib_deps = emelianov/eModbus

[env:bench_espModbus]
framework = espidf
build_src_filter = +<bench_espModbus/>
; esp-modbus pulled via idf_component.yml or manifest

[env:app_Rob2011]
build_src_filter = +<app_Rob2011/>
lib_deps = emelianov/modbus-esp8266

[env:app_vwetter]
build_src_filter = +<app_vwetter/>
lib_deps =
    ; from libraries.txt

[env:app_harihanv]
build_src_filter = +<app_harihanv/>

[env:app_NamNamIoT]
build_src_filter = +<app_NamNamIoT/>
lib_deps = emelianov/modbus-esp8266

[env:ext_zivillian]
extra_configs = ext_projects/zivillian/platformio.ini
; or driven via wrapper script

[env:ext_tobiasfaust]
extra_configs = ext_projects/tobiasfaust/platformio.ini

[env:ext_maxx_ukoo]
framework = espidf
board_build.cmake_extra_args = -DEXTRA_COMPONENT_DIRS=ext_projects/maxx-ukoo
```

The class P and I entries above are placeholders; in practice each external project is built via its own root `platformio.ini` or `idf.py` invocation, with output normalized by `scripts/build_all.sh` into the same JSON shape.

### 5.2 Common bench firmware shape (classes L)

```cpp
// pseudocode shared by class L envs
setup() {
  log("boot");
  wifi_connect();
  log("wifi_ready,%lu", millis());
  rtu_master_init(BENCH_TX, BENCH_RX, BENCH_DE, BENCH_BAUD);
  tcp_server_start(502);
  log("ready,%lu", millis());
}

loop() {
  poll_modbus();
  if (heartbeat_due()) {
    log_json({"heap":..., "min_heap":..., "stack_tcp":..., "stack_rtu":...});
  }
}
```

The host coordinator parses lines prefixed `LOG ` and `JSON ` over the USB CDC monitor.

---

## 6. Build / Run / Collect Loop

For each env in the matrix:

1. `pio run -e <env> -t size` → capture size JSON.
2. `pio run -e <env> -t upload` → flash DUT.
3. Start `host/rtu_slave.py`.
4. Open `pio device monitor -e <env>` → stream into a log file.
5. Run `host/bench_client.py --env <env> --cases sanity,latency,throughput,concurrency,stress` → writes per-case results.
6. Stop monitor + RTU slave.
7. `host/metrics_collector.py --env <env>` → merges size + serial log + client output → `results/metrics_<env>.json`.

`scripts/run_all.sh` automates this for all 9 envs, with a 30 s settle delay between runs.

---

## 7. Excel Integration

Add one new sheet to `evaluation_template.xlsx`:

**Sheet `Benchmark Results`** — one row per env, columns:

| Col | Field |
|---|---|
| A | Project |
| B | Class (L/P/A/I) |
| C | Flash used (bytes) |
| D | Flash % |
| E | RAM used (bytes) |
| F | RAM % |
| G | Free heap idle |
| H | Min free heap |
| I | Boot-to-ready (ms) |
| J | Lat FC03/10 mean (ms) |
| K | Lat FC03/10 p99 (ms) |
| L | Lat FC03/125 mean (ms) |
| M | Throughput @ 50 rps (achieved) |
| N | Max concurrent clients |
| O | Stress pass count (of 4) |
| P | Functional bench (Y/N) |
| Q | Notes |

Conditional formatting: 3-color scale on C, E, J, K, L (lower = green); top-N highlight on M, N.

`scripts/fill_excel.py` opens the workbook with `openpyxl`, writes one row per env from `results/metrics_*.json`, then runs `python scripts/recalc.py` to refresh formulas.

The existing `Summary & Score` sheet picks up these columns via cross-sheet references for the final weighted ranking.

---

## 8. Risks and Mitigations

| Risk | Mitigation |
|---|---|
| Class P/A projects target classic ESP32 (LAN8720, GPIO numbering) | Bench over WiFi only on S3; patch pin defines per env; if no clean patch, fall back to size-only |
| `tobiasfaust/SolaxModbusGateway` is Solax-specific, may not behave as a generic gateway | Mark functional bench N/A; report size + boot only |
| `esp-modbus` requires ESP-IDF, mixed framework workspace | Use `framework = espidf` env; isolated `sdkconfig` |
| Different libs use different RS485 DE/RE conventions (auto vs manual) | Bench firmware sets DE/RE per-lib in adapter layer |
| WiFi credentials in source | Inject via `build_flags = -DWIFI_SSID=\"...\" -DWIFI_PASS=\"...\"`, or `include/secrets.h` git-ignored |
| Host RTU slave timing jitter on USB-RS485 dongle | Use FT232R or CP2102N with low-latency mode; document dongle model in results |
| Non-deterministic latency across runs | Run each case 3× and report median of the per-run p99 |

---

## 9. Acceptance

The benchmark sweep is considered complete when:

- [ ] All 9 envs produce a `metrics_<env>.json` file (functional or size-only).
- [ ] At least the 2 class-L envs pass sanity + full perf suite.
- [ ] `Benchmark Results` sheet in `evaluation_template.xlsx` is populated for all 9 rows.
- [ ] `Summary & Score` sheet rankings reflect the new metrics.
- [ ] This document, the project's `README.md`, and `TODO.md` are updated to reflect actual versus planned results.

---

## 10. Open Decisions

These need user input before Phase 2 (host harness) starts:

1. **Board variant** — confirm `esp32-s3-devkitc-1`, or specify exact part number (N4R2, N8R8, N16R8).
2. **RS485 transceiver model** — MAX3485 / SP3485 / other; confirm DE/RE wiring.
3. **RTU slave hardware** — host USB-RS485 dongle (specify chipset) or dedicated second ESP.
4. **WiFi creds delivery** — `build_flags` or `secrets.h`?
5. **Scope of functional bench for classes P/A/I** — attempt for every env, or fall back to size-only when the default firmware behavior doesn't match the test fixture?
6. **ESP32-S3 patch budget** — willing to patch each env for S3 (pin defines, board target), or skip envs that require >1 hour of porting?

Answers to these unblock the build phase.
