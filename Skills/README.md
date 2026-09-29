# Skills used to write the thesis

A **skill** is a folder with a `SKILL.md` file that teaches Claude how to do one job
well. Claude loads it automatically when your request matches the skill's
description, or you can call it by name (e.g. `/kmutnb-thesis`).

> Skill = คู่มือที่ Claude อ่านก่อนทำงาน ติดตั้งครั้งเดียว แล้ว Claude จะใช้เองเมื่อเจองานที่ตรงกัน

## Skills in this folder

| Skill | What it does | Use it when… |
|-------|--------------|--------------|
| [`kmutnb-thesis`](kmutnb-thesis/) | Thesis writing assistant for the **KMUTNB EE template**: chapter structure, 5-paragraph intro, abstract < 200 words, IEEE references, quality checklist. Ships the blank `.dotx` template and the strict [template guide](kmutnb-thesis/reference/THESIS_TEMPLATE_GUIDE.md) (page margins, fonts, styles, TOC rules, known pitfalls, pre-submission checklist). | Writing or reviewing any section; checking format before submission |
| [`rsp-wording`](rsp-wording/) | Writes Thai technical prose in the style of the KMUTNB IoT Engineering Education blog (อ.RSP) — natural Thai, English term in parentheses on first mention, glossary of IoT/embedded terms. | Writing/translating Thai chapters about IoT, MCU, Modbus, MQTT, sensors, etc. |
| [`thai-docx`](thai-docx/) | Fixes broken Thai in Word files made with python-docx: floating tone marks, Thai shrinking to 10 pt, bold not applying. Includes `thai_docx.py` (`enforce_thai(doc)`) and a verifier. | After **any** script/Claude edit of a Thai `.docx` |
| [`thai-distribute-docx`](thai-distribute-docx/) | Fixes "loose" Thai justification (ภ า ค ผ น ว ก) by rebuilding runs Word-style and applying *Thai Distributed* (กระจายแบบไทย). Includes `scripts/thai_distribute.py`. | Thai paragraphs stretch between letters instead of words |
| [`academic-pptx`](academic-pptx/) | Academic presentation rules: action titles, one idea per slide, argument structure, conclusion slide stays up during Q&A. Third-party skill — see its README. | Making defense / progress slides |

### Built-in skills also used (no install needed)

These come with Claude (claude.ai: *Settings → Capabilities*; Claude Code desktop: already enabled).
They are not copied here.

| Skill | Used for |
|-------|----------|
| `docx` | Reading/editing the thesis `.docx`, tracked changes, TOC fields |
| `pptx` | Building the defense deck and A1 poster |
| `pdf` | Exporting/reading PDFs, merging the approval certificate |
| `skill-creator` | Making or improving your own skills |

## Install

### Claude Code (terminal or desktop app)

Copy each skill folder into `~/.claude/skills/` (all projects) or `<your-project>/.claude/skills/` (one project):

```bash
mkdir -p ~/.claude/skills
for d in Skills/*/; do cp -R "${d%/}" ~/.claude/skills/; done
```

Restart Claude Code, then type `/` — the skills should appear in the list.

### claude.ai (web / desktop chat)

1. Zip one skill folder so that `SKILL.md` is at the top of the zip, e.g.
   ```bash
   cd Skills && zip -r kmutnb-thesis.zip kmutnb-thesis
   ```
2. claude.ai → **Customize → Skills → Upload skill** → pick the zip.
3. Repeat for each skill you want.

### Python scripts (thai-docx, thai-distribute-docx)

```bash
pip install python-docx
python3 Skills/thai-docx/scripts/verify_thai_docx.py MyThesis.docx
python3 Skills/thai-distribute-docx/scripts/thai_distribute.py MyThesis.docx --start "บทที่ 1"
```

`verify_thai_docx.py` checks run-level font slots. A Word-authored file whose Thai
fonts come from styles (like the template) reports FAIL even when it renders
correctly — use it on files *you generated with python-docx*.

## Example prompts

- `/kmutnb-thesis` → *"Write the abstract for my thesis on …, Thai and English."*
- *"Review Chapter 3 against the KMUTNB template guide and list every violation."*
- *"Rewrite this paragraph in natural Thai using RSP wording."*
- *"I edited thesis.docx with python-docx — fix the Thai fonts and justification."*
- *"Create a 15-minute defense deck from my thesis using academic-pptx."*

## Make your own

Found a rule your advisor keeps correcting? Add it to
`kmutnb-thesis/reference/THESIS_TEMPLATE_GUIDE.md` §12 *Known pitfalls* and commit it —
the next student gets it for free. For a brand-new skill, ask Claude to use `skill-creator`.
