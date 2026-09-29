# Session Handover — Senior Project Thesis

**Author:** พัทธนันท์ พันธุมณี (Patthanan Bhandhumanee), KMUTNB — Electrical & Computer Engineering
**Title (EN):** Design and Implementation of an Educational Industrial IoT Platform Combining SBC, MCU, and PLC
**Title (TH):** การออกแบบและสร้างแพลตฟอร์มไอโอทีเชิงอุตสาหกรรมเพื่อการศึกษา โดยผสานคอมพิวเตอร์บอร์ดเดี่ยว ไมโครคอนโทรลเลอร์ และพีแอลซี
**Template:** KMUTNB EE Bachelor Thesis (May 2023), Angsana New throughout
**Last updated:** 2026-07-03
**Git branch:** `thesis-figures-qa-fixes` (in the `Thesis paper/` repo)

---

## The two deliverables (single sources of truth)

| File | Edition | Length |
|------|---------|--------|
| `thesis_en.docx` | English | ~43 pp |
| `thesis_th.docx` | Thai (primary edition being polished) | ~71 pp |

Everything else is **derived** from these two files:
- `chapters/en/` and `chapters/th/` — per-chapter splits (frontmatter, ch1–5, backmatter).
- The Word **TOC / List of Figures / List of Tables** are live fields — they refresh when
  you open the file and press **Ctrl+A, then F9**. Always do this after opening.

> ⚠️ **Edit the `.docx` directly, then re-split.** Do **not** run a clean rebuild from
> `build_thesis_v2.py` expecting to reproduce the current state — several late edits (see
> "Scripts vs. inline" below) live only in the committed `.docx`, not in the build scripts.
> The committed `thesis_en.docx` / `thesis_th.docx` are authoritative.

---

## Current structure (both editions, unless noted)

**Objectives — 4 (consolidated):** (1) build the IIoT lab platform integrating SBC + MCU + PLC;
(2) demonstrate IT/OT integration on an open-source stack (MQTT, Node-RED, TIG); (3) implement &
evaluate the ESP32-S3 Modbus gateway libraries and measure the gateway; (4) build the IoT-Sniffer
for wire-level observation + network-performance measurement.

**Chapter 2 — Background:** 2.1 IT/OT Convergence · 2.2 Common HW/SW (2.2.1 IT, 2.2.2 OT) ·
2.3 Protocols (2.3.1 Modbus RTU, 2.3.2 Modbus TCP, 2.3.3 MQTT) · 2.4 Controllers (MCU/SBC/PLC) ·
2.5 Open-source vs proprietary · **2.6 Time-Series Dashboard Stack (TIG)** ·
**2.7 MQTT Broker (Mosquitto)** · **2.8 Related Work**.

**Chapter 3 — Design (software-framed):** 3.1 Overall Architecture · 3.2 Hardware Selection
(MCU/SBC/PLC) · 3.3 OT-Layer Software (PLC + LOGO! Soft Comfort) · 3.4 Edge-Gateway Firmware ·
3.5 IT-Layer Software (containerised MQTT + TIG) · 3.6 IoT-Sniffer.

**Chapter 4 — Evaluation:** 4.1 Modbus Gateway Library Evaluation (4.1.1 setup, 4.1.2 results,
4.1.3 recommendation) · 4.2 Gateway Performance Measurement. **(Study B / Node-RED-vs-Telegraf
was removed.)**

**Chapter 5 — Discussion:** 5.1 System Overview (keeps the MCU/SBC/PLC comparison table) ·
5.2 Problems, Obstacles, and Solutions · 5.3 Recommendations.

**Removed entirely:** the Purdue reference model (whole discussion, figure, table row); all
cybersecurity content (§2.7 security, §4.4 demo, refs [9]–[10]); Study B.

---

## §5.2 — filled with the author's real content (2026-07-04)

**§5.2 (Problems, Obstacles, Solutions) — both editions** now contains four real problems
confirmed by the author: library selection, RS-485 wiring, the **Pi 4 2 GB RAM constraint**,
and **Node-RED initially outside the Compose stack breaking Modbus TCP** (fixed by moving it
into the same docker-compose.yml). The draft review note has been deleted.

---

## Figures (Thai edition only; the English edition has no inline figures)

Chapter 2 has **no figures** (2.1–2.4 were removed on request). Present: **3.1** architecture,
**3.2** hardware photo, **3.3** LOGO! wiring, **3.4** PLC panel, **3.5** data-flow, **3.6** Pi
photo, **3.7** IoT-Sniffer UI, **4.1** Study-A bench, **4.2** Grafana temp/humidity, **4.3**
Grafana SDM120, **4.4** Pi telemetry dashboard, **4.5** touchscreen kiosk (4.4/4.5 live under
§4.2), **จ.1** ESP32-S3 board, **จ.2** LOGO! 24CE, **จ.3** RPi 4, **จ.4** XY-MD02.
Source images: `assets/figures/`. Phone photos need EXIF-rotation before insertion (the
finalize script does this).

> The §3.5 data-flow image still shows a "Node-RED" node in the diagram; the caption no longer
> lists it. Regenerate `assets/figures/data flow.png` if you want it gone from the picture too.

---

## Wording — KMUTNB IoT blog (RSP) voice

The background/technical sections were rewritten in the style of
`iot-kmutnb.github.io/blogs` (author "RSP"): **§2.3.1, §2.3.2, §2.3.3, §2.4.1, §2.4.2, §2.7**,
plus appendix **จ.4/จ.5** terminology. Key terms adopted: มาสเตอร์/สเลฟ (master/slave),
รหัสคำสั่ง (Function Code), 16-bit CRC, big-endian, MBAP, เอดจ์เกตเวย์, ผู้เผยแพร่/ผู้สมัครรับข้อความ,
โบรกเกอร์ (ตัวกลาง), ข้อความที่เก็บรักษาไว้ (retained message), การส่งครั้งสุดท้าย (last will),
เพาเวอร์มิเตอร์, รางปีกนก (DIN Rail). **Decision on file:** the analytical/results/discussion
chapters keep an academic register (RSP's tutorial tone is only for background material).

---

## Hardware (as documented in the thesis)

- **MCU:** Waveshare ESP32-S3-Relay-6CH (ESP32-S3-WROOM-1; RS-485 transceiver; 6× SPDT relays; PSRAM).
- **PLC:** Siemens LOGO! 24CE, part № 6ED1052-1CC08-0BA2, 24 V DC, 4× transistor outputs.
- **SBC:** Raspberry Pi 4 Model B (**2 GB** — corrected 2026-07-04, was wrongly documented as 4 GB), Docker Compose host for Mosquitto + TIG.
- **Field devices:** XY-MD02 (SHT20, RS-485 Modbus RTU); Eastron SDM120 single-phase power meter.
- Selected gateway library after benchmarking 8: **emelianov/modbus-esp8266** (72.2% flash, 14.8% RAM).

---

## Build pipeline (`build_scripts/`, run in this order)

```bash
python3 build_scripts/build_thesis_v2.py            # thesis_en.docx from the .dotx template
python3 build_scripts/build_thesis_th.py            # translate EN -> thesis_th.docx
python3 build_scripts/thai_typography.py            # enforce Angsana New
python3 build_scripts/finalize_thesis_th.py         # TH figures + TOC/LoF/LoT fields + template fixes
python3 build_scripts/drop_security.py              # remove security content (EN+TH)
python3 build_scripts/rewrite_objectives.py         # 4 objectives + conclusion (EN+TH)
python3 build_scripts/finalize_thesis_en.py         # EN continuous numbering + List of Tables
python3 build_scripts/drop_purdue.py                # remove Purdue (EN+TH)
python3 build_scripts/split_tig_mqtt.py             # split §2.6 -> TIG + MQTT (EN+TH)
python3 build_scripts/restructure_ch345_th.py       # TH ch3/4/5 restructure + เอดจ์เกตเวย์
python3 build_scripts/restructure_ch345_en.py       # EN ch3/4/5 restructure + dashboard term
python3 build_scripts/split_editions.py             # per-chapter docx -> chapters/en, chapters/th
```

After **any** manual `.docx` edit, the only step you normally need is:
`python3 build_scripts/split_editions.py` (regenerate the chapter splits), then commit.

### Scripts vs. inline (important)
These late edits were applied **directly to the `.docx`** and are **not** reproduced by the
pipeline above, so a from-scratch rebuild would lose them: the RSP-voice rewrites of
§2.3.1/2.3.2/2.3.3/2.4.1/2.4.2/2.7, the สมัครสมาชิก→สมัครรับข้อความ swap, the appendix จ.4/จ.5
terminology, and the removal of the leftover "Node-RED vs Telegraf" line in the ch2 structure
paragraph. Treat the committed `.docx` as truth; edit it directly rather than rebuilding.

---

## Environment notes

- **Render to PDF:** `soffice --headless --convert-to pdf <file>.docx` (cold start can time out
  at ~45 s — retry once). Set `HOME` to a writable dir if `impl_store` errors.
- **Thai font in headless render:** LibreOffice substitutes Angsana New; install a Thai font
  (e.g. Norasi) and map Angsana New → Norasi via fontconfig, or page counts/wrapping will be
  wrong (DejaVu fallback inflates length). Word on the author's machine renders correctly.
- **Small/rotated JPEGs** that python-docx rejects: normalize with PIL (EXIF-transpose + re-encode)
  before insertion.
- **Delete permission:** the mounted folder blocks `rm` by default; if git leaves `.lock` files,
  re-enable deletion for the folder before retrying git.

---

## Open items

- Fill author placeholders: **advisor name, student ID, academic year** (approval page);
  **ภูมิลำเนา / bio details** (biography).
- Refresh Word fields (**Ctrl+A, F9**) so TOC/LoF/LoT and section numbering update.
- Optional: align the remaining appendix hardware entries (จ.1 ESP32-S3, จ.2 LOGO!, จ.3 RPi 4)
  to RSP wording; regenerate the §3.5 data-flow diagram without the Node-RED node.
- The **English surname** is intentionally kept as "Bhandhumanee" (author's choice), even though
  the Thai name was corrected to พันธุมณี.
