# KMUTNB EE Bachelor Thesis — Strict Template Specification

**Template of record:** `Thai_Template_Bachelor Thesis May2023_EE.dotx`
**Institution:** King Mongkut's University of Technology North Bangkok (KMUTNB)
**Department:** Electrical and Computer Engineering, Faculty of Engineering
**Language:** Thai body with embedded English technical terms; bilingual front matter

> **Rule of authority.** Where the .dotx *style definitions* and the .dotx *example document* disagree, the **example document governs**, because that is what the department sees on paper. Every rule below states the effective (rendered) requirement first, and the underlying XML mechanics second. All sizes are stated as `pt (half-points)`. Measurements in twips (1 pt = 20 twips, 1 inch = 1440 twips).

---

## 1. Page geometry (MUST match exactly)

| Property | Value | Twips |
|---|---|---|
| Paper | A4 portrait | 11906 × 16838 |
| Margin top | 3.81 cm (1.5") | 2160 |
| Margin left | 3.81 cm (1.5") | 2160 |
| Margin right | 2.54 cm (1.0") | 1440 |
| Margin bottom | 2.54 cm (1.0") | 1440 |
| Header from edge | 2.54 cm (1.0") | 1440 |
| Footer from edge | 1.25 cm | 706 |
| Text column width | — | 8306 |

Never change `pgSz`/`pgMar` in any section. All sections of the document use the same geometry.

---

## 2. Fonts and the Thai/Latin size split (CRITICAL)

Word stores **two sizes per run**: `w:sz` (Latin/ASCII) and `w:szCs` (complex script = Thai). **Thai text renders with `szCs`, not `sz`.** Nearly every formatting bug in this template family comes from setting one and forgetting the other.

- Default complex-script font (docDefaults): **Angsana New**. Thai text must always resolve to Angsana New.
- The template's docDefaults Latin font is Times New Roman with `Normal sz=24` (12 pt), but the example document overrides **every content run to `sz=32` (16 pt)** with theme font `majorBidi`. Effective rule: **Latin text inside Thai paragraphs is 16 pt, same face as the Thai text.**
- **STRICT RULE: whenever you set a size on a run, set BOTH `sz` and `szCs` to the same value.** A run with `sz=32` and no `szCs` renders its Thai at whatever the style inherits (in a broken document that can be 12 pt).

### 2.1 Effective size table (what must appear on paper)

| Element | Effective size | Weight | Notes |
|---|---|---|---|
| Body text (Normal) | 16 pt (32/32) | regular | justified |
| Heading 0 (unnumbered chapters) | **18 pt (36/36)** | bold | see §3.2 — requires run override |
| Heading 1 (บทที่ N) | 24 pt (48/48) | bold | centered |
| Heading 2 (N.N) | 16 pt (32/32) | bold | |
| Heading 3 (N.N.N) | 16 pt (32/32) | bold | |
| Heading 4 | 16 pt (32/32) | bold | maximum depth — never deeper |
| Caption (ภาพที่ / ตารางที่) | 16 pt (32/32) | bold | |
| TOC / list entries (all 3 lists) | 16 pt (32/32) | regular | |
| สารบัญ column headers (หน้า / ภาพที่ / ตารางที่) | 16 pt (32/32) | regular | |
| Thesisname (cover title) | 18 pt (36/36) | regular | centered |
| Firstpage (cover degree text) | 10/12 pt (20/24) | regular | fixed cover block |
| Abstract, Acknowledgement, Nomenclature, Bibliography, Biography | 16 pt (32/32) | regular | all based on Normal |

---

## 3. Paragraph styles — exact definitions

### 3.1 Normal
- `sz=24, szCs=32` (Latin 12 default / Thai 16 — but see §2: content runs carry 32/32)
- spacing `before=120 after=120`, line `480 exact` (24 pt exact line height)
- first-line indent `562` twips
- **justified** (`jc=both`; Thai-distributed `thaiDistribute` on individual paragraphs is an acceptable equivalent)

### 3.2 Heading0 — the trap
- Style definition: bold, centered, `spacing before=0 after=720`, firstLine 0, **sz/szCs = 40/40 (20 pt)**.
- **The example document overrides every single Heading0 run to 36/36 (18 pt).** Therefore: every Heading0 paragraph you create MUST carry explicit `sz=36 szCs=36` run properties. A bare Heading0 paragraph renders 20 pt and is WRONG.
- Used for: ใบรับรองปริญญานิพนธ์, บทคัดย่อ, Abstract, กิตติกรรมประกาศ, สารบัญ, สารบัญ (ต่อ), สารบัญภาพ(+ต่อ), สารบัญตาราง(+ต่อ), ศัพท์เฉพาะ, เอกสารอ้างอิง(+ต่อ), ประวัติผู้แต่ง, ภาคผนวก ก/ข/ค/…
- Major-section Heading0 paragraphs carry `pageBreakBefore` so each section starts a fresh page.

### 3.3 Heading1 (numbered chapters)
- bold, centered, `spacing after=480`, line `600 exact`, outline level 0.
- Effective size 24 pt both scripts (`szCs=48` run override in the example; the style's szCs=40 is never used bare).
- Chapter format is two lines: `บทที่ N` line-break `ชื่อบท` inside one Heading1 paragraph.
- After pressing Enter, style returns to Normal automatically (`next=Normal`).

### 3.4 Heading2 / Heading3 / Heading4
- bold, keepNext + keepLines, Heading2 line `520 exact`, spacing `before=200 after=0`.
- Effective 16 pt both scripts — **run override `szCs=32` required** (style szCs=28 = 14 pt is never used bare).
- Numbering "N.N", "N.N.N" followed by a tab, then the title. Numbers must be consistent with the chapter.
- **Maximum heading depth = 4 levels.** Content below that is prose, not headings.

### 3.5 Caption
- Based on Normal: bold + bCs, firstLine 0, centered.
- Figure captions: centered under the figure. Table captions: above the table; left alignment (`jc=left` paragraph override) is the accepted variant for long table captions in this thesis.
- Never use the Caption style for ordinary prose. If a paragraph is body text, it is `Normal` — a Caption-styled paragraph with bold/center switched off manually is still a defect.

### 3.6 Other styles (all based on Normal unless noted)
| Style | Extra properties |
|---|---|
| Abstract | none (plain Normal look) |
| Acknowledgement | none |
| ListParagraph | firstLine 0, contextualSpacing (single spacing, 0 pt between same-style items) |
| Nomenclature | `jc=left`, spacing 0/0, `ind left=1701 hanging=1701`, left tab @1701 — term column then definition |
| Bibliography | spacing 0/0, `ind left=567 hanging=567`, left tab @720 — hanging indent for `[n]` markers |
| Biography | plain Normal look; photo floats left (wrapSquare/wrapTight allowed here only) |
| Thesisname | centered, firstLine 0, 36/36 |
| Firstpage | centered, `line 100 atLeast`, sz 20 / szCs 24 |
| TOC1 | firstLine 0, spacing 0/0, line 240 auto, `jc=left` |
| TOC2 | left indent 720, tabs left@1260 + right@8280 |
| TOC3 | left indent 1260, `jc=left`, tabs left@2070 + right@8280 |
| TableofFigures | firstLine 0, spacing 0/0 |

---

## 4. Document structure — exact order and heading text

1. หน้าปก (cover) — styles `Thesisname`, `Firstpage`; no page number
2. ใบรับรองปริญญานิพนธ์ (approval certificate)
3. บทคัดย่อ (Thai abstract)
4. Abstract (English abstract)
5. กิตติกรรมประกาศ
6. สารบัญ (+ สารบัญ (ต่อ) continuation pages)
7. สารบัญภาพ (+ ต่อ)
8. สารบัญตาราง (+ ต่อ)
9. ศัพท์เฉพาะ (Nomenclature)
10. บทที่ 1 … บทที่ N
11. เอกสารอ้างอิง (+ ต่อ)
12. **ประวัติผู้แต่ง** ← exact wording; NOT ประวัติผู้เขียน
13. ภาคผนวก ก, ข, ค, … (each starts on a new page with Heading0; a descriptive title after the letter is permitted, e.g. "ภาคผนวก ก ภาพรวมการออกแบบ…")

Front matter is one Word section with **Thai-letter page numbers (ก ข ค ง จ ฉ ช ซ ฌ ญ ฎ …)** in the header, right-aligned. The body (บทที่ 1 onward) restarts at **Arabic 1**. The cover shows no number.

**NEVER delete section breaks.** The page-number system collapses without them. There are breaks at minimum: end of cover, start of บทที่ 1.

---

## 5. Tables of contents — construction rules (STRICT)

### 5.1 Field codes
- สารบัญ: `TOC \o "1-3" \h \z \t "Heading 0,1"` — pulls Heading1–3 plus Heading0 as level 1.
- สารบัญภาพ / สารบัญตาราง: either caption-based (`TOC \h \z \c "Figure"` / `\c "Table"`) or TC-field-based (`TOC \h \z \f F` / `\f T` with `TC "…" \f F` fields embedded in each caption). This thesis uses the TC mechanism — keep it; do not mix mechanisms.
- All three must be **live fields**, never retyped static text.

### 5.2 Entry format
- สารบัญ entries: heading text, right-aligned page number via right tab at the margin (leaderless, per template example).
- **สารบัญภาพ / สารบัญตาราง entries contain ONLY the number and title — NO "ภาพที่"/"ตารางที่" prefix.** Correct: `2.1 สถาปัตยกรรม…    9`. Wrong: `ภาพที่ 2.1 สถาปัตยกรรม…    9`. The word ภาพที่/ตารางที่ appears only once, in the column-header line. (If using TC fields, the TC text itself must omit the prefix.)
- List entries also **exclude the source note** — the `(ที่มา: …)` part stays in the caption only. Entry text = caption title truncated before `(ที่มา:`.
- Entry runs: 16 pt both scripts (32/32).
- **Completeness: EVERY caption in the document appears in its list — including appendix figures AND appendix tables** (ภาพที่ ง.1, ตารางที่ ก.1, …). Passed-thesis convention: body entries first in chapter order, then appendix entries in appendix-letter order. Each listed caption also carries a matching `TC` field (`\f F` for figures, `\f T` for tables) so field regeneration stays complete.

### 5.3 Page furniture — every list page, including continuations
- First page of each list: `Heading0` title (สารบัญ / สารบัญภาพ / สารบัญตาราง) at 18 pt (36/36 override).
- **Every continuation page** starts with `<title> (ต่อ)` as Heading0 18 pt, followed by the column-header line.
- Column-header line: `ภาพที่` (or `ตารางที่`; nothing for สารบัญ — just `หน้า`) + right tab to **8280** + `หน้า`. 16 pt (32/32 — BOTH values, see §2). Spacing 0/0, line 240 auto, firstLine 0.
- The (ต่อ) heading paragraph carries `pageBreakBefore` to pin it to its page top. If the list reflows (entries added/removed/resized), **re-check that no entry is stranded alone before a pinned (ต่อ) page** and move the heading pair to the correct entry boundary.

### 5.4 Maintenance rule
- To refresh after edits: right-click each list → Update Field → **"Update page numbers only"**.
- **NEVER choose "Update entire table"** — it regenerates entries from the TOC styles and **deletes the manual (ต่อ) headings and column-header lines**. If a full rebuild is unavoidable, re-insert every (ต่อ) heading + header line afterwards and re-verify sizes (regenerated runs may drop szCs).
- After any front-matter reflow (a list gaining/losing a page), the Thai-letter references inside สารบัญ (for สารบัญภาพ ฯลฯ) also change — update numbers again.
- Final verification must be against the **exported PDF**, page by page, not the editing view (screen pagination can differ from print pagination).

---

## 6. Figures

- Insert **inline, in a dedicated centered paragraph** (zero indent, jc center). This is the standard; anchored/floating images are allowed ONLY on the cover and in ประวัติผู้แต่ง (photo), matching the template's own usage. If an image must float, wrapping must be **Top and Bottom** — never square/tight/through/behind.
- Caption **below** the figure: `ภาพที่ X.Y <title>` — Caption style, bold, 16 pt (32/32). Chapter-based numbering (X = chapter or appendix letter). Source line convention: `(ที่มา: <source>)` appended to the caption.
- Appendix figures: `ภาพที่ ก.1`, `ภาพที่ ง.2`, …
- Every figure must be referenced in the text (as `ภาพที่ X.Y`) **before** it appears.
- Keep caption on the same page as its figure (keepNext on the image paragraph or caption).
- **The list entry (TC text) and the caption must say exactly the same thing.** Any edit to a caption must be mirrored in its TC field.

## 7. Tables

- Caption **above** the table: `ตารางที่ X.Y <title>` — Caption style, bold, 16 pt, keepNext so it cannot separate from the table.
- **Appendix tables also require captions**: `ตารางที่ ก.1`, `ตารางที่ ข.1`, … (they are not listed in สารบัญตาราง unless given TC/SEQ fields — the template lists chapter tables only).
- Repeat header row for tables that cross pages (Table Properties → Repeat as header row).
- Every table referenced in text before it appears.

## 8. Equations

- MathType/OMML equation placed in a **borderless 2-column table**: equation in the left cell, number `(X.Y)` in the right cell, Caption style, right-aligned.
- Cross-reference as `สมการที่ (X.Y)` — type "สมการที่" manually, then insert the cross-reference ("Only label and number").

---

## 9. Front-matter content rules

### 9.1 Cover
- Title max 4 lines Thai + 4 lines English, style Thesisname.
- Author line(s) with prefix (นาย/นางสาว; Mr./Ms.), student ID line.
- Degree statement block in Firstpage style — its position is fixed; do not reflow it.

### 9.2 Abstract (both languages)
- **Under 200 words**, one structured block: problem → objective → method → key results (with numbers) → conclusion.
- Keyword line, exactly one line, 4–5 terms, comma-separated:
  `คำสำคัญ: <ก>, <ข>, <ค>, <ง>, <จ>` and `Keywords: <a>, <b>, <c>, <d>, <e>` — Thai and English keyword sets must correspond 1:1.

### 9.3 ศัพท์เฉพาะ
- Nomenclature style only: term, tab, definition. One term per paragraph. No blank paragraphs between entries.

---

## 10. Writing rules (enforced at review)

- **No first-person pronouns** (ฉัน, ผม, ดิฉัน, เรา, พวกเรา) — recast in third person / passive.
- Introduction chapter answers, in order: (1) what is the problem, (2) why interesting/important, (3) why hard, (4) why prior solutions fall short, (5) key elements of this approach + results + limitations.
- Methods: full technical detail, novelty explicit. Results: experiments carry the argument (figures/tables). Discussion: fair, includes limitations. Conclusion: not a copy of the abstract; includes future work; do not enumerate weaknesses here.
- Short sentences; no stacked noun phrases; no copy-paste from other documents; define abbreviations at first use.

## 11. References — IEEE

- Bibliography style (hanging indent), numbered `[1] [2] …` in citation order.
- Every reference cited in text as `[n]`; every in-text `[n]` resolves to the list.
- Formats: journal — Author, "Title," *Journal*, vol., no., pp., year. Book — Author, *Title*, ed. City: Publisher, year. Online — Author/Org, "Title," year. [Online]. Available: URL. Standard — *Title*, Std. no., year.

---

## 12. Known pitfalls (each one has actually happened — check for all of them)

1. **Missing `szCs`** → Thai silently renders 12 pt while Latin is 16 pt. Audit any run you touch. (§2)
2. **Bare Heading0** → renders 20 pt instead of 18 pt. Always 36/36 run override. (§3.2)
3. **"Update entire table"** → wipes (ต่อ) headings and column headers, and can drop szCs from regenerated entries. Page numbers only. (§5.4)
4. **Reflow strands an entry** before a pinned (ต่อ) page (orphan above the page break). Re-seat the heading pair after any size/content change in the lists. (§5.3)
5. **ภาพที่/ตารางที่ prefix inside list entries** — prefix belongs only in the column header. (§5.2)
6. **Caption style used for prose** (or Normal used for captions). Style must match semantics even if manual overrides make it look right. (§3.5)
7. **Caption text ≠ TC/list text** (e.g. "(2 GB)" vs "(4 GB)") — mirror every caption edit into its TC field.
8. **ประวัติผู้เขียน** instead of **ประวัติผู้แต่ง**. (§4)
9. **Appendix tables without captions.** (§7)
10. **Editing the .docx XML while Word has the file open** → Word's in-memory copy overwrites your changes on next save. Close the document first (check the `~$…` lock file), edit, then reopen.
11. **Verifying on screen instead of the exported PDF** — Word's screen pagination and page count can differ from print/PDF output. The PDF is the deliverable; verify it.
12. **Deleted section break** → Thai-letter/Arabic page numbering collapses. (§4)

---

## 13. Pre-submission checklist (strict — all boxes required)

**Geometry & styles**
- [ ] A4; margins 2160/2160/1440/1440 twips in every section
- [ ] Only predefined styles used; no ad-hoc styles
- [ ] Body justified, 16 pt both scripts; spot-check runs for missing `szCs`

**Structure**
- [ ] Section order exactly as §4; ประวัติผู้แต่ง wording
- [ ] Section breaks intact; Thai letters in front matter, Arabic 1 from บทที่ 1; no number on cover
- [ ] Every Heading0 = 18 pt bold centered; every บทที่ = 24 pt; H2–H4 = 16 pt bold; depth ≤ 4

**Lists (สารบัญ / ภาพ / ตาราง)**
- [ ] All three are live fields; entries 16 pt; no ภาพที่/ตารางที่ prefix in entries
- [ ] (ต่อ) heading + column header on every continuation page, 18 pt / 16 pt, pinned, no orphaned entries
- [ ] Page numbers refreshed via "numbers only" AFTER the final content edit, then PDF re-exported
- [ ] Spot-check ≥3 entries per list against the actual PDF page

**Objects**
- [ ] Figures: inline centered, caption below, ภาพที่ X.Y bold 16 pt, (ที่มา: …) where applicable
- [ ] Tables: caption above, ตารางที่ X.Y, including every appendix table; header rows repeat
- [ ] Equations: borderless 2-col table with (X.Y); referenced as สมการที่ (X.Y)
- [ ] Caption text identical to its list/TC text

**Content**
- [ ] Abstract < 200 words (TH & EN), IMRAD, results with numbers
- [ ] คำสำคัญ/Keywords: 4–5 terms, TH↔EN matching
- [ ] No first-person pronouns anywhere
- [ ] All references IEEE, all cited, Bibliography style
- [ ] Intro answers the 5 questions; conclusion ≠ abstract; future work present

**Final**
- [ ] Export PDF ("Best for printing"), open the PDF, and page through the entire front matter + one spot-check per chapter + every appendix
- [ ] Commit/back up both .docx and .pdf together
