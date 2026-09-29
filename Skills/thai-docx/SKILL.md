---
name: thai-docx
description: >-
  Fix broken Thai-language rendering in Word (.docx) files generated with
  python-docx. Use this skill WHENEVER you generate, edit, or assemble a .docx
  that contains any Thai text — contracts, สัญญา, คำให้การ, บันทึก, government
  forms, reports, letters, or mixed Thai/English documents — even if the user
  only says "make a Word doc" without mentioning fonts. python-docx writes only
  the Latin font slot, so Thai silently breaks in real Microsoft Word: floating
  tone marks (วรรณยุกต์ลอย), Thai shrinking to ~10pt while Latin stays 16pt,
  bold not applying to Thai, and letters smeared across justified lines. The bug
  is invisible in LibreOffice and previewers because they guess the font; it
  only appears in the Word the recipient opens. Trigger on TH Sarabun New,
  ฟอนต์ไทยเพี้ยน, Thai legal/official documents, or any task that calls
  doc.save() with Thai content. Also use to clean Thai text pasted from a PDF.
---

# thai-docx — correct Thai rendering in python-docx output

## The one rule

Generate the `.docx` with python-docx exactly as normal. **Right before
`doc.save()`, call `enforce_thai(doc)`.** Then run the verifier on the saved
file. That is the whole workflow.

```python
import sys
sys.path.insert(0, "<this-skill>/scripts")   # or copy thai_docx.py next to your script
from thai_docx import enforce_thai

doc = Document()
doc.add_paragraph("สัญญาฉบับนี้ทำขึ้นระหว่างผู้ขายและผู้ซื้อ")
# ... build the whole document ...

enforce_thai(doc)            # <-- the fix, one line, just before save
doc.save("contract.docx")
```

Then, always:

```bash
python <this-skill>/scripts/verify_thai_docx.py contract.docx
```

Exit 0 = safe to send. Do **not** judge correctness from a preview or from
LibreOffice — they guess a Thai font and hide the bug. Believe the scanner.

## Why this is needed (so you apply it sensibly, not by rote)

Word does not choose a font per run. Within a single run it keeps several *font
slots* and picks one **per character** by script:

| Slot | Attribute | Script it serves |
|------|-----------|------------------|
| Latin | `w:rFonts/@w:ascii`, `@w:hAnsi` | English, Latin-1 |
| **Complex Script** | `w:rFonts/@w:cs` | **Thai**, Arabic, Hebrew |
| East Asian | `w:rFonts/@w:eastAsia` | CJK |

python-docx's `run.font` only ever writes the **Latin** slot and its Latin
twins — `w:sz` (size), `w:b` (bold), `w:i` (italic). It never writes the
**complex-script twins** that Thai actually obeys:

- `w:cs` — Thai font name → missing ⇒ Thai falls back, wrong glyphs, floating marks
- `w:szCs` — Thai size → missing ⇒ Thai collapses to the ~10pt default while Latin stays 16pt
- `w:bCs` / `w:iCs` — Thai bold/italic → missing ⇒ bold/italic ignored on Thai
- `w:lang/@w:bidi` — complex-script language → missing ⇒ bad shaping / mark stacking

`enforce_thai(doc)` walks **every** run — body, tables, headers, footers — plus
every **style** and the **document defaults**, and mirrors each Latin property
into its complex-script twin so the slots agree.

This is not a python-docx bug to report; python-docx simply was not designed for
complex scripts. The handling has to live on our side. This skill is only a font
and rendering layer — it does not write or review the document's content.

## Common tasks

### Mixed Thai + English fonts in the same run

Official style is often Thai in TH Sarabun New but English in Times New Roman,
inside the same sentence. Don't split text into multiple runs by hand — pass
`latin_font` and let the font slots do it:

```python
enforce_thai(doc, thai_font="TH Sarabun New", latin_font="Times New Roman")
```

Every run then renders Thai with the Thai font and Latin characters with the
Latin font automatically. (Omit `latin_font` to let the Thai font cover Latin
too.)

For one specific run where you want explicit control — e.g. different sizes,
since TH Sarabun looks smaller than Latin faces at equal point size:

```python
from thai_docx import set_run_fonts
set_run_fonts(run, thai_font="TH Sarabun New", latin_font="Times New Roman",
              thai_size_pt=18, latin_size_pt=16)
```

### Headings shrinking

`enforce_thai` is deliberately careful here: a run with **no explicit size**
inherits from its style, so the skill does **not** stamp `w:szCs` on it (that
would freeze the size and stop headings from scaling). It fixes the *styles*
instead, so headings keep their size and still get a Thai font slot. You don't
need to do anything special — just call `enforce_thai` once.

### Letters smeared across justified lines (อักษรห่างเป็นช่องๆ)

With `both`/`thaiDistribute` justification and long Thai text, some Word builds
lack a Thai dictionary, break **mid-word**, and stretch the gaps across the
whole line. Insert legal break points at real word boundaries:

```python
from thai_docx import apply_thai_linebreaks
apply_thai_linebreaks(doc)   # inserts U+200B (ZWSP) at word boundaries
enforce_thai(doc)
doc.save(...)
```

This needs `pythainlp` for word segmentation (`pip install pythainlp`). If it is
not installed the function warns and does nothing — the document is still valid,
just without break hints, so it never breaks the build.

### Thai text pasted from a PDF

PDF extraction splits tone marks off their consonants, injects zero-width junk,
and sprinkles spaces between Thai characters. Clean strings **before** putting
them in the document:

```python
from thai_docx import clean_pdf_thai
para.add_run(clean_pdf_thai(text_from_pdf))
```

It normalises to NFC, strips invisible characters, re-glues combining marks, and
removes spaces sitting between two Thai characters — without touching spacing
around English words or numbers.

## Scripts

- `scripts/thai_docx.py` — the engine. `enforce_thai`, `set_run_fonts`,
  `clean_pdf_thai`, `apply_thai_linebreaks`. Import it or copy it beside your
  generation script.
- `scripts/verify_thai_docx.py` — the QA scanner. Run on every saved file; it
  reports, per Thai run, which complex-script property is missing and the
  symptom it causes. Exit 0 = pass.

## Definition of done

1. `enforce_thai(doc)` called immediately before `doc.save()`.
2. `verify_thai_docx.py <file>` exits 0.
3. Output is a **draft** — Thai legal/official content still needs human review.
