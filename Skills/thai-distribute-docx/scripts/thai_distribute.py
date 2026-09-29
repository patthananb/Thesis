#!/usr/bin/env python3
"""thai_distribute — rebuild Thai paragraphs Word-style and apply thaiDistribute.

Why this exists
---------------
Word justifies Thai (``w:jc="thaiDistribute"``) by stretching space *between
words*, which it finds with a dictionary. Two things break that:

    1. Fragmented runs. Programmatic edits split one paragraph into many
       ``<w:r>`` runs; run boundaries block Thai word segmentation, so Word
       stretches space between *characters* instead ("ภ า ค ผ น ว ก").
    2. Missing ``<w:cs/>``. Word itself tags Thai runs as complex script.
       Runs without the flag may not get dictionary word-breaking.

For each target body paragraph this script concatenates the run text, deletes
the old runs, re-emits runs segmented by script (Thai -> run with ``<w:cs/>``,
Latin -> plain run, spaces inherit the current segment), writes ``w:sz`` and
``w:szCs``, and sets ``w:jc = thaiDistribute``.

Paragraphs containing fields, drawings, tabs, breaks, hyperlinks, or
footnote references are skipped (rebuilding them would destroy captions,
SEQ/TC fields and images), as are headings, captions and short lines.

Usage
-----
    python3 thai_distribute.py THESIS.docx
    python3 thai_distribute.py THESIS.docx --start "ภาคผนวก ก"
    python3 thai_distribute.py THESIS.docx --start "บทที่ 4" --end "บทที่ 5"
    python3 thai_distribute.py THESIS.docx --min-len 80 --size 32 -o out.docx

The file is overwritten in place unless ``-o`` is given. Close it in Word
first, and commit before running (binary docx — no merge rescue).
"""

from __future__ import annotations

import argparse
import copy
import re
import sys

from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

_THAI_RE = re.compile(r"[฀-๿]")

# Anything inside a paragraph that a naive run rebuild would destroy.
# Matched by local name so the mc: (markup-compatibility) prefix needs no nsmap.
_UNSAFE_TAGS = (
    "fldChar", "instrText", "fldSimple", "drawing", "pict", "object", "tab",
    "br", "cr", "hyperlink", "footnoteReference", "endnoteReference",
    "commentReference", "bookmarkStart", "sym", "AlternateContent",
)
_UNSAFE_XPATH = ".//*[" + " or ".join(f"local-name()='{t}'" for t in _UNSAFE_TAGS) + "]"


def _style_name(par) -> str:
    try:
        return par.style.name or ""
    except (KeyError, AttributeError):
        return ""


def _is_heading(par) -> bool:
    name = _style_name(par).lower().replace(" ", "")
    return name.startswith("heading") or name in ("title", "subtitle")


def _is_caption(par) -> bool:
    return "caption" in _style_name(par).lower()


def _segments(text: str):
    """Split text into (is_thai, chunk) runs; spaces join the current segment."""
    out: list[list] = []
    for ch in text:
        if ch.isspace() and out:
            out[-1][1] += ch
            continue
        thai = bool(_THAI_RE.match(ch))
        if out and out[-1][0] == thai:
            out[-1][1] += ch
        else:
            out.append([thai, ch])
    return [(t, s) for t, s in out]


def _base_rpr(p_el):
    """Copy the first run's rPr so fonts/bold survive the rebuild."""
    first = p_el.find(qn("w:r"))
    rpr = first.find(qn("w:rPr")) if first is not None else None
    rpr = copy.deepcopy(rpr) if rpr is not None else OxmlElement("w:rPr")
    for tag in ("w:cs", "w:sz", "w:szCs", "w:rtl"):
        for el in rpr.findall(qn(tag)):
            rpr.remove(el)
    return rpr


def _set_val(parent, tag: str, val: str):
    el = OxmlElement(tag)
    el.set(qn("w:val"), val)
    parent.append(el)


def _make_run(base_rpr, text: str, thai: bool, size: int):
    r = OxmlElement("w:r")
    rpr = copy.deepcopy(base_rpr)
    # Schema order inside rPr: ... cs, ... sz, szCs ... ; append is accepted by Word.
    if thai:
        rpr.append(OxmlElement("w:cs"))
    _set_val(rpr, "w:sz", str(size))
    _set_val(rpr, "w:szCs", str(size))
    r.append(rpr)
    t = OxmlElement("w:t")
    t.text = text
    t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    r.append(t)
    return r


def _set_jc(p_el, value: str):
    ppr = p_el.get_or_add_pPr()
    jc = ppr.find(qn("w:jc"))
    if jc is None:
        jc = OxmlElement("w:jc")
        ppr.append(jc)
    jc.set(qn("w:val"), value)


def rebuild(par, size: int) -> bool:
    p_el = par._p
    if p_el.xpath(_UNSAFE_XPATH):
        return False
    runs = p_el.findall(qn("w:r"))
    if not runs:
        return False
    text = "".join(t.text or "" for r in runs for t in r.findall(qn("w:t")))
    if not _THAI_RE.search(text):
        return False
    base = _base_rpr(p_el)
    anchor = runs[0]
    new_runs = [_make_run(base, s, thai, size) for thai, s in _segments(text)]
    for nr in reversed(new_runs):
        anchor.addnext(nr)
    for r in runs:
        p_el.remove(r)
    _set_jc(p_el, "thaiDistribute")
    return True


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("docx")
    ap.add_argument("-o", "--output", help="write here instead of in place")
    ap.add_argument("--start", help="begin at the heading whose text starts with this")
    ap.add_argument("--end", help="stop at the heading whose text starts with this")
    ap.add_argument("--min-len", type=int, default=60,
                    help="skip paragraphs shorter than this (default 60)")
    ap.add_argument("--size", type=int, default=32,
                    help="half-point font size for rebuilt runs (32 = 16 pt)")
    args = ap.parse_args(argv)

    doc = Document(args.docx)
    active = args.start is None
    changed = skipped = 0
    for par in doc.paragraphs:
        txt = par.text.strip()
        if _is_heading(par):
            if args.start and txt.startswith(args.start):
                active = True
            elif args.end and active and txt.startswith(args.end):
                break
            continue
        if not active or _is_caption(par) or len(txt) < args.min_len:
            continue
        if rebuild(par, args.size):
            changed += 1
        else:
            skipped += 1

    if args.start and not active:
        print(f"heading starting with {args.start!r} not found", file=sys.stderr)
        return 1
    doc.save(args.output or args.docx)
    print(f"rebuilt {changed} paragraph(s); skipped {skipped} unsafe/non-Thai")
    return 0


if __name__ == "__main__":
    sys.exit(main())
