# Benchmark TODO

## Done

- Initialized a local Git repository for this project.
- Preserved the existing manual ESP32-S3 master / ESP32-C6 slave connectivity test.
- Added fixed upload ports for the current boards.
- Added a two-board benchmark scaffold:
  - `bench_slave_c6`
  - `bench_rob2011_master`
  - `bench_vwetter_master`
  - `bench_zivillian_master`
  - `bench_harihanv_master`
  - `bench_tobiasfaust_master`
  - `bench_emodbus_master`
  - `bench_namnam_iot_master`
  - `bench_maxx_ukoo_master`
  - `bench_esp_modbus_master`
- Added shared RTU conformance cases for FC03, FC06, FC16, illegal-address
  exception handling, and a small latency sample.
- Verified the benchmark slave and all nine master envs build successfully.
- Split each master benchmark into its own source folder under
  `src/bench_masters/<candidate>/` and pointed each PlatformIO env at its
  candidate folder.
- Added a real eModbus master adapter using `ModbusClientRTU`.
- Added a capture script that writes monitor JSON lines to
  `results/metrics_<env>.json`.
- Exported observed benchmark results into `../evaluation_template.xlsx`.
- Added `tcp_rtu_gateway_s3` for Modbus TCP/WiFi to Modbus RTU/RS485 gateway
  testing.
- Added `scripts/benchmark_tcp_rtu_gateway.py` for Python-native and `mbpoll`
  host polling benchmarks.

## Next

- Replace each remaining manual-wrapper master env with a true candidate-specific
  adapter where the upstream project exposes a reusable RTU API.
- For gateway projects that are not reusable libraries, decide whether to:
  - wrap their gateway firmware directly,
  - extract their RTU transaction layer,
  - or mark them size-only / architecture-only.
- Add full latency distributions instead of the current 20-sample smoke metric.
- Run TCP/RTU gateway benchmark on hardware after connecting the host computer
  to the S3 access point or configuring the S3 for station-mode WiFi.

## Notes

- `../BENCHMARK_PLAN.md` describes a host-PC TCP gateway benchmark. This project
  currently uses the requested two-board RTU topology: ESP32-S3 master and
  ESP32-C6 slave.
- The current benchmark env separation is intentional. It lets each library or
  upstream gateway project be ported independently without changing the hardware
  fixture or result format.
