# Thesis Kit — KMUTNB ECE Senior Project

Everything you need to write a **KMUTNB Electrical & Computer Engineering bachelor
thesis (ปริญญานิพนธ์)** with the help of Claude — plus a complete, approved example
thesis to copy from.

> ชุดเครื่องมือสำหรับรุ่นน้องที่กำลังทำปริญญานิพนธ์ — มี **Skills** ให้ Claude ช่วยเขียน
> และ **ตัวอย่างปริญญานิพนธ์ที่ผ่านการตรวจแล้ว** ไว้ดูเป็นแนวทาง

## What's inside

| Folder | What it is | Start here if… |
|--------|------------|----------------|
| [`Skills/`](Skills/) | Claude skills used to write the thesis: template rules, Thai fonts in Word, Thai justification, Thai technical wording, defense slides | You want Claude to help you write |
| [`Patthanan Works/`](Patthanan%20Works/) | Patthanan's full senior project: approved thesis, IEEE article, slides, poster, code, benchmarks, research notes | You want to see a finished example |

## Quick start (5 minutes)

1. **Get the files** — clone or *Code → Download ZIP*:
   ```bash
   git clone --recurse-submodules https://github.com/patthananb/Thesis.git
   ```
2. **Install the skills** — copy each folder in `Skills/` into your Claude skills folder:
   ```bash
   mkdir -p ~/.claude/skills
   for d in Thesis/Skills/*/; do cp -R "${d%/}" ~/.claude/skills/; done
   ```
   (Using claude.ai instead? See [Skills/README.md](Skills/README.md#install) — zip each folder and upload it.)
3. **Open the blank template** — `Skills/kmutnb-thesis/template/Thai_Template_Bachelor Thesis May2023_EE.dotx`.
4. **Ask Claude** — for example:
   - `/kmutnb-thesis` then *"Help me write Chapter 1 for my project on …"*
   - *"Check my thesis.docx against the KMUTNB template"*
   - *"เขียนบทที่ 2 ส่วนทฤษฎี Modbus ให้เป็นภาษาไทยที่อ่านเป็นธรรมชาติ"*
   - *"Make 15 defense slides from my thesis"*
5. **Compare with the example** — open
   [`Patthanan Works/01-Thesis/final/`](Patthanan%20Works/01-Thesis/final/) to see what an
   approved thesis looks like.

## Recommended workflow

```
Plan outline ──▶ Write chapters ──▶ Build .docx ──▶ Fix Thai typography ──▶ Advisor review ──▶ Defense slides
 kmutnb-thesis    kmutnb-thesis      docx (built-in)  thai-docx                kmutnb-thesis      academic-pptx
                  rsp-wording                         thai-distribute-docx     (pre-submission    pptx (built-in)
                                                                                checklist)
```

1. **Outline first.** Agree chapter titles with your advisor, then let `kmutnb-thesis` draft section by section.
2. **Thai prose.** Run drafts through `rsp-wording` so Thai sentences sound natural and technical terms stay consistent.
3. **Word file.** Write straight into the template (or let Claude edit it with python-docx).
   After *any* programmatic edit, run `thai-docx` (fonts) and `thai-distribute-docx` (justification).
4. **Before every submission**, walk the *Pre-submission checklist* in
   [`THESIS_TEMPLATE_GUIDE.md`](Skills/kmutnb-thesis/reference/THESIS_TEMPLATE_GUIDE.md) §13 —
   every item there is a mistake that actually happened.
5. **In Word:** `Ctrl+A` then `F9` to refresh the Table of Contents / List of Figures / List of Tables.

## Tips learned the hard way

- **Commit (or copy) the `.docx` before every big edit.** Word files can't be merged — a backup is the only undo.
- **Close the file in Word before letting a script edit it**, or your changes get overwritten.
- **Don't trust LibreOffice/Google Docs previews for Thai.** Check in real Microsoft Word; floating tone marks only show there.
- **Headings, TOC and captions are fields.** Edit headings in the body, then refresh fields — never type into the TOC.

## License / credits

- Thesis content, code and slides in `Patthanan Works/` © Patthanan Bhandhumanee. Use them as reference; don't copy them into your own thesis.
- `Skills/academic-pptx/` is a third-party skill — see its own [README](Skills/academic-pptx/README.md).
- Vendored Modbus libraries under `04-Modbus-Lib-Eval/.../lib/` are git submodules pointing to their original authors.
