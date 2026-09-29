# References Index — LOGO! 8 + Node-RED + Modbus TCP

## Siemens Official PDFs (Downloaded)

| # | File | Description |
|---|------|-------------|
| 1 | `siemens_logo_modbus_tcp_sentron_pac.pdf` | LOGO! Modbus/TCP app example with SENTRON PAC — register tables |
| 2 | `siemens_logo_modbus_tcp_7kn_powercenter.pdf` | LOGO! 8.3 Modbus/TCP with 7KN Powercenter |
| 3 | `siemens_logo_soft_comfort_help.pdf` | LOGO! Soft Comfort full online help (22 MB) |

## Tutorials & Community (Saved as Markdown)

| # | File | Description |
|---|------|-------------|
| 4 | `04_databoom_logo8_modbus_tcp_stepbystep.md` | Databoom step-by-step LOGO! Modbus TCP guide |
| 5 | `05_pundurs_logo8_modbus_tcp_python.md` | Python code examples reading LOGO! via Modbus TCP |
| 6 | `06_industrial_monitor_logo8_ethernet_protocol.md` | Protocol support and address mapping reference |
| 7 | `07_netio_an60_logo_modbus_tcp.md` | LOGO! as Modbus master (client) — application note |
| 8 | `08_home_assistant_logo_modbus_community.md` | Real-world config examples, off-by-one fix |
| 9 | `09_github_hacs_modbus_logo_address_table.md` | **Best address table** — community verified |
| 10 | `10_infoneva_logo8_modbus_tcp_config.md` | LOGO! Soft Comfort server/client config steps |

## Node-RED Resources (Saved as Markdown)

| # | File | Description |
|---|------|-------------|
| 11 | `11_nodered_contrib_modbus_docs.md` | node-red-contrib-modbus all nodes reference |
| 12 | `12_flowfuse_modbus_nodered_guide.md` | FlowFuse complete Modbus + Node-RED guide |
| 13 | `13_steve_nodered_modbus_guide.md` | Buffer reading, flex getter, sleeping node fix |

---

## Quick Cheat Sheet

| Goal | FC | Address (0-based) |
|------|----|-------------------|
| Read I1–I8 | FC2 | 0–7 |
| Read Q1–Q8 | FC1 | 8192–8199 |
| Write Q1 ON/OFF | FC5 | 8192 |
| Read AI1–AI8 | FC4 | 0–7 |
| Write AQ1 | FC6 | 512 |
| Read/Write M1–M8 | FC1/FC5 | 8256–8263 |
| Read AM1–AM8 | FC3 | 528–535 |

**Unit ID:** 1 | **Port:** 502 | **Endian:** Big-endian
