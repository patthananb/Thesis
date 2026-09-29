# TODO — Complete the Thesis Report
**File:** `senior_project_report.docx` (English) | `senior_project_report_thai.docx` (Thai)  
**Current page count:** ~53 pages (target: 60–80)  
**Branch:** `master` (English) | `thai-translation` (Thai, not yet synced)  
**Last scanned:** 2026-06-18 (559 paragraphs)

---

## ⚠️ Known Issue to Fix

- [ ] **Table 4.2 mislabel** — Table 4.2 (para 333) is in Section 4.2.2 (Node-RED vs Telegraf) but contains Study A Flash/RAM data. Either move it back to Section 4.1.2 or replace it with actual Study B Node-RED vs Telegraf comparison data and rename the Flash/RAM table to Table 4.1b or similar.

---

## STEP 1 — Photos ✅ ALL INSERTED

| File | Inserted as |
|---|---|
| `piscreen.jpg` | Figure 3.7 — Grafana touchscreen |
| `plc.jpg` | Figure E.4 — LOGO! 8.4 panel |
| `raspberrypi.jpg` | Figure E.8 — Raspberry Pi 4 |
| `waveshareesp32s3 xymd sdm.jpg` | Figure 3.2 — ESP32-S3 + XY-MD02 + SDM120 testbed |
| `MODBUS GATEWAY testbench.png` | Figure 4.0 — Study A breadboard bench |
| `ESP32-S3-Relay-6CH-details-1.jpg` | Figure E.1 — ESP32-S3-Relay-6CH board detail |
| `xymd02.jpg` | Figure E.7 — XY-MD02 sensor module (Appendix E.4) |
| `pi4.jpg` | Figure E.10 — Pi 4 Grafana kiosk |

---

## STEP 2 — Screenshots Still Needed (Take from Running System)

- [ ] **Figure 3.3** (para 251) — LOGO! Soft Comfort: Ladder Program 1 (pump start/stop, Q1 relay, VW4 counter)
- [ ] **Figure 3.8** (para 274) — Grafana: SDM120 Power Monitoring panel (voltage, current, active power)
- [x] **Figure 3.9** (Section 3.6) — IoT-Sniffer packet inspector (Modbus TCP Write Multiple Registers decode) ✅ (2026-06-18, real screenshot from iot-sniffer/docs, §3.6 description rewritten)
- [ ] **Figure 4.3** (para 340) — IoT-Sniffer capture: FC05 Write Single Coil 12-byte plaintext frame
- [ ] **Figure 4.4** (para 342) — Terminal: `mosquitto_pub` spoofing command + Grafana showing injected spike
- [ ] **Figure E.6** (para 507) — LOGO! Soft Comfort: ladder program screenshot (duplicate of 3.3, for Appendix E.2)

---

## STEP 3 — Diagrams to Draw

Use draw.io (app.diagrams.net) or PowerPoint. All are `[placeholder]` in the doc.

- [x] **Figure 2.1** ✅ Purdue/ISA-95 layer diagram
- [x] **Figure 3.1** ✅ System architecture diagram
- [ ] **Figure 2.2** (para 119) — Modbus RTU ADU byte layout: `[Addr][FC][Data...][CRC-L][CRC-H]`
- [ ] **Figure 2.3** (para 177) — MQTT QoS 1 handshake: Publisher→Broker PUBLISH/PUBACK, Broker→Subscriber PUBLISH/PUBACK
- [ ] **Figure 2.4** (para 138) — Modbus address space: 4 spaces × FC codes table
- [ ] **Figure 2.5** (para 187) — MQTT CONNECT/CONNACK sequence + Connect Flags byte breakdown
- [ ] **Figure 3.5** (para 254) — ESP32-S3 cooperative `loop()` flowchart: RTU poll → register update → MQTT publish → TCP slave service
- [ ] **Figure 3.6** (para 262) — Docker Compose service dependency graph: Mosquitto→Telegraf→InfluxDB←Grafana
- [ ] **Figure E.2** (para 456) — ESP32-S3 relay driver block diagram: SoC ↔ optocoupler ↔ relay
- [ ] **Figure E.3** (para 476) — GPIO-to-relay pin-out diagram for ESP32-S3-Relay-6CH
- [ ] **Figure E.5** (para 481) — LOGO! 8.4 internal architecture block diagram
- [ ] **Figure E.9** (para 512) — Raspberry Pi 4 block diagram

---

## STEP 4 — Tables Still Missing (placeholders in doc)

- [x] **Table 2.2** (para 171) — MQTT 5.0 control packet type table: Type, Code, Direction, Purpose ✅ (2026-06-18, all 15 packet types 0x01-0x0F)
- [x] **Table 3.1** (para 271) — Purdue Level Assignment: L0=field instruments, L1=LOGO! 8.4/STM32, L2=ESP32-S3, L3=RPi/TIG ✅ (2026-06-18, 5-row level map incl. L4-5 out-of-scope)
- [x] **Table 3.2** (para 248) — Hardware inventory: device, role, cost (THB), key specs ✅ (2026-06-18, 11 items + total, indicative Thai retail prices)
- [x] **Table 4.3** (para 348) — MCU vs SBC vs PLC comparison: determinism, OS, I/O, cost, certification, Purdue role ✅ (2026-06-18, 13-row comparison matrix)

---

## STEP 5 — Data / Experiment Figures Still Missing

- [x] **Table 4.1** ✅ 9-library latency scorecard (real hardware data 2026-05-14)
- [x] **Table 4.2** ✅ Flash/RAM usage (PlatformIO build) — ⚠️ see mislabel issue above
- [ ] **Figure 4.1** (para 312) — FC03 latency box plots per library — generate from benchmark CSV
- [ ] **Figure 4.2** (para 313) — Flash/RAM usage bar chart per library — generate from build output
- [ ] **Study B data** (Section 4.2) — Node-RED vs Telegraf actual latency/memory numbers over 1,000 messages; currently only a one-line summary exists

---

## STEP 6 — Text Sections Still Incomplete

- [x] **Section 2.7 — Hardware Platforms** (Chapter 2) — new background section on MCU/SBC/PLC + field instruments with fundamentals/formulas (ADC quantisation, PLC scan cycle, RMS power/energy, optocoupler isolation); Related Work renumbered to 2.8 ✅ (2026-06-18)
- [ ] **Abstract** (para 32) — currently one paragraph; finalize word count < 200 words, add specific numbers
- [ ] **Section 3.3** — LOGO! 8.4 Modbus TCP configuration: IP address setup in LOGO! Soft Comfort, connection table, register mapping (VW addresses → HR), Modbus TCP server enable steps
- [ ] **Section 3.3** — Simple ladder program explanation: annotate Figure 3.3 with rung-by-rung description (start contact I1, stop contact I2, self-latch Q1, VW4 counter)
- [ ] **Section 3.4** — Actual firmware code snippets (RTU master function ~80 lines, MQTT publish call, TCP slave init) from `PlatformIO/Projects/ESP32S3CAN/src/`
- [ ] **Appendix A** (para 411) — Full code listings: RTU master function, MQTT publisher, Modbus TCP slave init
- [ ] **Appendix B** (para 416) — `compose.yml` + `telegraf.conf` full listings (port table already done ✅)
- [ ] **Appendix C** (para 419) — Full library scorecard from `Documentation/docs/modbus_lib_eval_2026-05-11.pdf`
- [ ] **Appendix D** (para 448) — Insert actual FC05 pcap capture + MQTT spoof capture screenshots from IoT-Sniffer (dashboard screenshots done ✅)
- [ ] **Biography** (para 406-408) — Author photo, birthdate, hometown, education history, contact email
- [ ] **Chapter 5** — Strengthen conclusions with specific numbers (latency, library choice rationale, Study B numbers)

---

## STEP 7 — Formatting / Final Polish

- [ ] Resolve figure number conflicts (Figure 3.3 appears twice: Ch3 and Appendix E.2/E.6)
- [ ] Number all figures/tables consistently — audit for duplicates after all insertions
- [ ] Update Table of Contents (Word: Ctrl+A → F9 → Update entire table)
- [ ] Update List of Figures and List of Tables
- [ ] Verify page numbers / header/footer match KMUTNB template
- [ ] Sync Thai version (`senior_project_report_thai.docx`) — currently ~38 pages, far behind
- [ ] Run spell check on English version
- [ ] Verify all references [1]–[20] are cited inline in text

---

## Page Count Progress

| Version | Now | Target |
|---|---|---|
| English (`master`) | **~53 pages** | 60–80 pages |
| Thai (`thai-translation`) | ~38 pages (not synced) | 60–80 pages |

**Remaining biggest page gains:**

1. Appendix A code listings (~8–10 pages)
2. Appendix B compose.yml + telegraf.conf (~4–6 pages)
3. Diagrams — Steps 3 figures (~4–6 pages)
4. LOGO! Modbus TCP config + ladder explanation (~2–3 pages)
5. Table 3.2 hardware inventory + Table 3.1 Purdue table (~1–2 pages)
6. Biography + finalized abstract + conclusions (~2–3 pages)

---

## Quick Commands

```bash
# Count current pages
cd "/sessions/clever-amazing-cray/mnt/Thesis paper"
libreoffice --headless --writer --convert-to pdf senior_project_report.docx --outdir /tmp/
pdfinfo /tmp/senior_project_report.pdf | grep Pages

# Detect paragraph boundaries (run after any edit)
python3 -c "
from docx import Document
doc = Document('senior_project_report.docx')
keywords = ['CHAPTER 2','CHAPTER 3','CHAPTER 4','CHAPTER 5',
            'APPENDIX A','APPENDIX B','APPENDIX C','APPENDIX D','APPENDIX E','REFERENCES']
for i, p in enumerate(doc.paragraphs):
    t = p.text.strip()
    for k in keywords:
        if t.startswith(k) and len(t) < 80: print(f'{i:4d}: {t[:60]}'); break
print('Total:', len(doc.paragraphs))
"

# Re-run chapter split (update CHAPTERS boundaries first if changed)
python3 /tmp/split_v3.py

# Git
cd "/sessions/clever-amazing-cray/mnt" && git log --oneline -5
```

---

*Last updated: 2026-06-18 (full scan of 559-para document)*
