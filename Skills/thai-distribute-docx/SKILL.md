---
name: thai-distribute-docx
description: Fix loose/ugly Thai Distributed (thaiDistribute, กระจายแบบไทย) justification in .docx files edited with python-docx. Use when Thai paragraphs in a Word document stretch space between individual characters instead of between words, when the user says Thai justification "looks loose", asks to "distribute" Thai paragraphs full-line, or after programmatic docx edits fragment runs. Rebuilds runs Word-style with the <w:cs/> complex-script flag and applies thaiDistribute.
---

# Thai Distribute for docx (กระจายแบบไทย)

## Problem

Word justifies Thai text well only when it can find word boundaries (Thai has no
spaces between words — Word uses a dictionary). Two things break this:

1. **Fragmented runs.** Programmatic edits (python-docx span replacements) split a
   paragraph into many `<w:r>` runs. Run boundaries block Thai word segmentation, so
   `thaiDistribute` falls back to stretching space **between characters** — the
   paragraph looks "loose" (ภ า ค ผ น ว ก ...).
2. **Missing `<w:cs/>` flag.** When Word itself writes Thai text (e.g. after the
   copy-plain-text-and-repaste trick), it puts Thai segments in runs whose `rPr`
   contains `<w:cs/>` (complex script) and keeps Latin segments in separate plain
   runs. Runs without `<w:cs/>` may not get dictionary word-breaking.

## Fix (what the script does)

For each target body paragraph:

1. Concatenate all run text.
2. Delete the old runs.
3. Re-emit runs **segmented by script**: contiguous Thai (U+0E00–U+0E7F, spaces
   inherit the current segment) → run with `<w:cs/>`; Latin/ASCII → plain run.
   Both get `w:sz`/`w:szCs` matching the document body size.
4. Set paragraph justification `w:jc = thaiDistribute`.

Skip paragraphs containing fields (`fldChar`/`instrText`), drawings, tabs, or line
breaks — rebuilding those destroys captions (SEQ/TC fields) and images. Skip
headings, captions, and short lines (default < 60 chars: section titles, spec
bullets).

## Usage

```bash
python3 scripts/thai_distribute.py THESIS.docx                       # whole document body
python3 scripts/thai_distribute.py THESIS.docx --start "ภาคผนวก ก"    # from this Heading-0 onward
python3 scripts/thai_distribute.py THESIS.docx --start "บทที่ 4" --end "บทที่ 5"
python3 scripts/thai_distribute.py THESIS.docx --min-len 80 --size 32
```

`--start`/`--end` match the beginning of heading text (any Heading style level).
`--size` is the half-point font size written into rebuilt runs (32 = 16 pt,
Angsana New thesis default).

## Checklist after running

- Reopen in Word (close first if open!) and check a pure-Thai paragraph — spacing
  should now stretch between words, not characters.
- Fields, captions, images are untouched by design; verify figure captions survive.
- Commit before and after (binary docx — no merge rescue).
