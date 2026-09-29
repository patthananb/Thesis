# Patthanan Works — example senior project

**Title (EN):** Design and Implementation of an Educational Industrial IoT Platform Combining SBC, MCU, and PLC
**Title (TH):** การออกแบบและสร้างแพลตฟอร์มไอโอทีเชิงอุตสาหกรรมเพื่อการศึกษา โดยผสานคอมพิวเตอร์บอร์ดเดี่ยว ไมโครคอนโทรลเลอร์ และพีแอลซี
**Author:** พัทธนันท์ พันธุมณี (Patthanan Bhandhumanee) — KMUTNB, Electrical & Computer Engineering, 2026
**Status:** Thesis approved for signature (ผ่านการตรวจ ขอลายเซ็นได้), August 2026

Use this folder as a **reference** for what each deliverable looks like. The files most
worth opening are marked ⭐.

## Layout

| Folder | Contents |
|--------|----------|
| [`01-Thesis/`](01-Thesis/) | The thesis itself (see below) |
| [`02-Presentations/`](02-Presentations/) | ⭐ `SeniorProjectPresentation.pptx` / `.pdf` — final defense deck · `SeniorProjectPresentation_draft_2026-06-22.pptx` — earlier draft · `Senior_Project_Summary.pptx` — progress talk (May) · ⭐ `Senior_Project_Poster_A1.pptx` — A1 poster · `presentation_plan.md` — how the deck was planned |
| [`03-Code/`](03-Code/) | ESP32-C6 (Modbus TCP master) ↔ ESP32-S3 (slave) Arduino sketches. Copy `secrets.h.example` → `secrets.h` and fill in Wi-Fi before building. |
| [`04-Modbus-Lib-Eval/`](04-Modbus-Lib-Eval/) | PlatformIO benchmark of 9 open-source ESP32 Modbus gateway libraries (thesis §4.1). Libraries are git submodules → clone with `--recurse-submodules`. |
| [`05-Research-and-Drafts/`](05-Research-and-Drafts/) | `research/` literature notes · `documentation/` datasheets, manuals, architecture diagrams, project plan · `drafts/` early outline and report drafts |

## `01-Thesis/`

| Path | Contents |
|------|----------|
| ⭐ `final/47_thesis_th_fixed_patthanan.docx` | Final Thai thesis (Word source) |
| ⭐ `final/47_thesis_th_fixed_patthanan_ผ่านการตรวจขอลายเซ็นได้.pdf` | Final PDF approved for signatures |
| `final/AppcertTH.pdf`, `AppcertEN.pdf`, `approval_certificate_single_paper.pdf` | Approval certificate pages |
| ⭐ `academic-article/Academic_Article_EN_IEEE_6pg.docx` | 6-page IEEE-format article from the thesis (`_eqfix` = equation fixes) |
| `advisor-review/` | Copy reviewed by พี่ต้น with comments — shows the kind of feedback to expect |
| `template/` | KMUTNB `.dotx` template, [`THESIS_TEMPLATE_GUIDE.md`](01-Thesis/template/THESIS_TEMPLATE_GUIDE.md), and a previously approved thesis used as a format reference |
| `chapters/th/`, `chapters/en/` | Per-chapter `.docx` splits (Thai and English editions, July 2026) |
| `build_scripts/` | python-docx scripts used to assemble/restructure the thesis (historical; paths refer to the old `Thesis paper/` layout) |
| `assets/figures/` | All figures used in the thesis |
| `docs/` | `HANDOVER.md` (session notes: structure decisions, what was removed and why), TODO lists |
| `archive/` | Superseded drafts and backups (kept on Patthanan's machine only — not uploaded) |

## What happened, in order

1. **Mar–Apr 2026** — research IIoT stack, plan hardware (SBC + ESP32 + Siemens LOGO! PLC) → `05-Research-and-Drafts/`
2. **Apr–May** — Modbus TCP master/slave firmware, 9-library benchmark → `03-Code/`, `04-Modbus-Lib-Eval/`
3. **May–Jun** — English draft built with python-docx into the KMUTNB template → `01-Thesis/build_scripts/`
4. **Jun** — defense → `02-Presentations/`
5. **Jul** — Thai edition, advisor feedback passes, IEEE article, poster
6. **Aug** — TOC/list-of-figures fixes, approved for signature → `01-Thesis/final/`
