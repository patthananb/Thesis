#!/usr/bin/env python3
"""Fill TOC/LoF/LoT page numbers from a rendered PDF.
Default: last occurrence of the key (content comes after the front-matter line).
Exception: ABSTRACT/ACKNOWLEDGEMENTS sit BEFORE the TOC, so use first occurrence."""
import json, re, subprocess, sys
from docx import Document

DOC = 'senior_project_report.docx'
SIDE = 'frontmatter_keys.json'
PDF = sys.argv[1] if len(sys.argv) > 1 else '/tmp/cal/senior_project_report.pdf'
HEADERS = {'toc': 'TABLE OF CONTENTS', 'lof': 'LIST OF FIGURES', 'lot': 'LIST OF TABLES'}
STOP = {'TABLE OF CONTENTS', 'LIST OF FIGURES', 'LIST OF TABLES', 'NOMENCLATURE',
        'ABSTRACT', 'ACKNOWLEDGEMENTS'}
FIRST = {'ABSTRACT', 'ACKNOWLEDGEMENTS'}


def norm(s):
    return re.sub(r'\s+', ' ', s).strip()


def main():
    keys = json.load(open(SIDE))
    txt = subprocess.run(['pdftotext', '-layout', PDF, '-'], capture_output=True, text=True).stdout
    pages = [norm(pg) for pg in txt.split('\f')]

    def find(key, first=False):
        k = norm(key); hit = None
        for i, pg in enumerate(pages):
            if k and k in pg:
                if first:
                    return i + 1
                hit = i + 1
        return hit

    doc = Document(DOC)
    paras = doc.paragraphs
    miss = 0
    for sec, header in HEADERS.items():
        hidx = next(i for i, p in enumerate(paras) if p.text.strip() == header)
        ents = []
        for p in paras[hidx + 1:]:
            t = p.text.strip()
            if t in STOP:
                break
            if t:
                ents.append(p)
        ks = keys[sec]
        for p, k in zip(ents, ks):
            pg = find(k, first=(k in FIRST))
            if pg is None:
                miss += 1
                continue
            if p.runs:
                p.runs[-1].text = str(pg)
    doc.save(DOC)
    print('calibrated; unmatched =', miss)


if __name__ == '__main__':
    main()
