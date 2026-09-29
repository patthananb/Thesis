#!/usr/bin/env python3
"""verify_thai_docx.py — QA scanner for Thai rendering in a .docx.

Run this AFTER saving, every time. The preview lies (LibreOffice and the docx
previewer guess a Thai font); this reads the actual XML the recipient's Word
will obey. It reports, per run that contains Thai, which complex-script
properties are missing and the symptom each omission produces.

    python verify_thai_docx.py contract.docx

Exit code 0 means every Thai-bearing run is fully specified — safe to send.
Exit code 1 means at least one run is under-specified — fix before sending.
"""

from __future__ import annotations

import sys

from docx import Document
from docx.oxml.ns import qn

import re
_THAI_RE = re.compile(r"[฀-๿]")


def _run_text(r) -> str:
    return "".join(t.text or "" for t in r.findall(qn("w:t")))


def _issues_for_run(r) -> list[str]:
    """Return human-readable problems for a Thai-bearing run, or []."""
    rpr = r.find(qn("w:rPr"))
    problems = []

    rfonts = rpr.find(qn("w:rFonts")) if rpr is not None else None
    if rfonts is None or not rfonts.get(qn("w:cs")):
        problems.append("missing w:rFonts/@w:cs  -> Thai falls back to wrong font / floating marks")

    # szCs only matters as a problem when a Latin size IS set but the CS twin isn't:
    # that is exactly the "Thai shrinks while Latin stays 16pt" symptom.
    if rpr is not None:
        sz = rpr.find(qn("w:sz"))
        szcs = rpr.find(qn("w:szCs"))
        if sz is not None and sz.get(qn("w:val")) and (szcs is None or not szcs.get(qn("w:val"))):
            problems.append("has w:sz but no w:szCs  -> Thai shrinks (~10pt) while Latin keeps its size")

        b = rpr.find(qn("w:b"))
        bcs = rpr.find(qn("w:bCs"))
        if b is not None and bcs is None:
            problems.append("has w:b but no w:bCs  -> bold ignored on Thai glyphs")

        lang = rpr.find(qn("w:lang"))
        if lang is None or not lang.get(qn("w:bidi")):
            problems.append("missing w:lang/@w:bidi  -> Word may misshape / mis-stack marks")
    else:
        problems.append("no w:rPr at all  -> entirely unspecified Thai run")

    return problems


def scan(path: str) -> int:
    doc = Document(path)

    # Collect every run from body, tables, headers, footers.
    roots = [doc.element.body]
    for section in doc.sections:
        for hf in (section.header, section.footer,
                   section.first_page_header, section.first_page_footer,
                   section.even_page_header, section.even_page_footer):
            if hf is not None:
                roots.append(hf._element)

    total_thai = 0
    bad = 0
    for root in roots:
        for r in root.iter(qn("w:r")):
            text = _run_text(r)
            if not _THAI_RE.search(text):
                continue
            total_thai += 1
            problems = _issues_for_run(r)
            if problems:
                bad += 1
                snippet = text.strip()[:40]
                print(f"  ✗ {snippet!r}")
                for p in problems:
                    print(f"      - {p}")

    print()
    print(f"Thai-bearing runs: {total_thai}   under-specified: {bad}")
    if bad == 0:
        print("PASS — every Thai run is fully specified. Safe to send.")
        return 0
    print("FAIL — run enforce_thai(doc) before saving, then re-scan.")
    return 1


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: python verify_thai_docx.py <file.docx>", file=sys.stderr)
        return 2
    return scan(argv[1])


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
