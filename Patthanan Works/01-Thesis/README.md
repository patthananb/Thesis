# Thesis — Educational IIoT Platform (SBC + MCU + PLC)

> **Final state (Aug 2026):** the approved thesis is `final/47_thesis_th_fixed_patthanan.docx`
> (+ signed-off PDF in `final/`). The IEEE article is in `academic-article/`, พี่ต้น's
> review copy in `advisor-review/`. The notes below describe the **July 2026 build
> workflow** and refer to the old `Thesis paper/thesis_en.docx` / `thesis_th.docx` files,
> which were superseded by the `final/` files.

**Title:** Design and Implementation of an Educational Industrial IoT Platform Combining SBC, MCU, and PLC
**Author:** Patthanan Bhandhumanee — KMUTNB, Electrical and Computer Engineering
**Active document:** `thesis_en.docx` — **English edition** (KMUTNB template).
A Thai edition (`thesis_th.docx`) will be produced as a translation pass once the
English content is locked.

This is a full rewrite. The previous report (`archive/senior_project_report.docx`) is
retained only as a backup and is **not** the source of truth. The English edition is
**fully English** — the template's duplicate Thai cover/approval/abstract paragraphs are
dropped and the Thai section headings are translated; the Thai edition will reintroduce
Thai as a translation pass.

## Folder layout

| Path | Contents |
|------|----------|
| `thesis_en.docx` | **Active thesis (English edition)** — single source of truth |
| `README.md` | This file |
| `template/` | KMUTNB `.dotx` template + `THESIS_TEMPLATE_GUIDE.md` |
| `build_scripts/` | Build tooling. `build_thesis_v2.py` assembles the thesis from the template |
| `assets/` | `figures/`, `iiot_comparison.xlsx` (source for Appendix F) |
| `docs/` | `HANDOVER.md`, `TODO_complete_report.md`, `frontmatter_keys.json` (old-workflow notes) |
| `archive/` | Old disliked report (`senior_project_report.*`), old `chapters/`, `chapter_thai/`, defense `.pptx` |

## Build

```bash
python3 build_scripts/build_thesis_v2.py            # regenerates thesis_en.docx from template/
# Thai edition (three passes, in order):
python3 build_scripts/build_thesis_th.py            # translate thesis_en.docx -> thesis_th.docx
python3 build_scripts/thai_typography.py            # enforce Angsana New typography
python3 build_scripts/finalize_thesis_th.py         # figures + TOC fields + KMUTNB template fixes
python3 build_scripts/drop_security.py              # remove security content (EN+TH)
python3 build_scripts/rewrite_objectives.py         # 4 consolidated objectives + matching conclusion (EN+TH)
python3 build_scripts/finalize_thesis_en.py         # EN: continuous numbering + populate List of Tables
python3 build_scripts/drop_purdue.py                # remove all Purdue-model content (EN+TH)
python3 build_scripts/split_tig_mqtt.py             # split §2.6 into TIG + MQTT sections (EN+TH)
python3 build_scripts/restructure_ch345_th.py       # TH: restructure ch3/4/5 + เกตเวย์ขอบ->เอดจ์เกตเวย์
python3 build_scripts/restructure_ch345_en.py       # EN: mirror the ch3/4/5 restructure + dashboard term
python3 build_scripts/split_editions.py             # per-chapter docx files -> chapters/en, chapters/th
python3 ~/.claude/skills/thai-docx/scripts/verify_thai_docx.py thesis_v2.docx   # must exit 0
```

The script patches the `.dotx` content-type to a readable `.docx`, fills the cover /
approval / abstract / acknowledgements, truncates the template's example chapters, and
appends the 5-chapter body. Thai fonts are enforced (Angsana New) before save.

## Structure

Ch1 Introduction · Ch2 Background & Related Work · Ch3 System Design & Implementation ·
Ch4 Evaluation & Results (4.1 Modbus library eval · 4.2 gateway performance · 4.3
Node-RED vs Telegraf · 4.4 security demo) · Ch5 Discussion & Conclusion ·
Appendices A–F.

## Status

- [x] Cover / approval / abstract (EN+TH) / acknowledgements
- [x] Chapter 1 — full (English)
- [x] Chapter 2 — full (English)
- [x] Chapter 3 — full (English)
- [x] Chapter 4 — Evaluation (real 9-library benchmark + gateway perf + Study B + security)
- [x] Chapter 5 — Discussion & Conclusion (incl. MCU/SBC/PLC comparison table)
- [x] References [1]–[9]
- [ ] Appendices A–F content (stubs)
- [ ] Figures (architecture, dataflow, sniffer captures, plots) — none placed yet
- [ ] Front-matter TOC / List of Figures / List of Tables regeneration
- [ ] Thai edition (`thesis_th.docx`) — translation pass
