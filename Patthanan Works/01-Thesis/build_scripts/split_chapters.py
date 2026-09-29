#!/usr/bin/env python3
"""Regenerate chapters/ from the combined thesis (content-based boundaries).

Each chapter file is a copy of the combined document with all body elements
outside the chapter's range removed (the trailing section properties are always
kept). This preserves styles, numbering, headers/footers, images and tables.
"""
import os
from docx import Document
from docx.oxml.ns import qn

DOC = 'senior_project_report.docx'
OUT = 'chapters'

# Ordered markers: (output filename, predicate on UPPER-cased paragraph text)
MARKERS = [
    ('00_front_matter.docx',            None),                       # from start
    ('01_abstract_acknowledgements.docx', lambda t: t.startswith('ABSTRACT')),
    ('02_chapter1_introduction.docx',   lambda t: t.startswith('CHAPTER 1')),
    ('03_chapter2_background.docx',     lambda t: t.startswith('CHAPTER 2')),
    ('04_chapter3_system_design.docx',  lambda t: t.startswith('CHAPTER 3')),
    ('05_chapter4_results.docx',        lambda t: t.startswith('CHAPTER 4')),
    ('06_chapter5_conclusion.docx',     lambda t: t.startswith('CHAPTER 5')),
    ('07_references.docx',              lambda t: t.startswith('REFERENCES')),
    ('08_appendix_a_firmware.docx',     lambda t: t.startswith('APPENDIX A')),
    ('09_appendix_b_docker.docx',       lambda t: t.startswith('APPENDIX B')),
    ('10_appendix_c_library_eval.docx', lambda t: t.startswith('APPENDIX C')),
    ('11_appendix_d_iot_sniffer.docx',  lambda t: t.startswith('APPENDIX D')),
    ('12_appendix_e_hardware.docx',     lambda t: t.startswith('APPENDIX E')),
]


def para_text(el):
    return ''.join(n.text or '' for n in el.iter(qn('w:t')))


def child_index_of_marker(children, predicate, after=0):
    for i in range(after, len(children)):
        ch = children[i]
        if ch.tag != qn('w:p'):
            continue
        # skip TOC / List-of-Figures / List-of-Tables entries (they contain a <w:tab/>)
        if ch.find('.//' + qn('w:tab')) is not None:
            continue
        txt = para_text(ch)
        if predicate(txt.strip().upper()):
            return i
    raise SystemExit(f'marker not found after index {after}')


def main():
    doc = Document(DOC)
    children = list(doc.element.body)

    # find boundary child-indices
    starts = [0]
    after = 0
    for fname, pred in MARKERS[1:]:
        idx = child_index_of_marker(children, pred, after)
        starts.append(idx)
        after = idx + 1
    starts.append(len(children))  # sentinel end

    ranges = [(MARKERS[i][0], starts[i], starts[i + 1]) for i in range(len(MARKERS))]

    os.makedirs(OUT, exist_ok=True)
    for fname, start, end in ranges:
        d = Document(DOC)
        body = d.element.body
        kids = list(body)
        for idx, ch in enumerate(kids):
            if ch.tag == qn('w:sectPr'):
                continue  # always keep body section properties
            if not (start <= idx < end):
                body.remove(ch)
        d.save(os.path.join(OUT, fname))
        print(f'{fname:38s} children[{start}:{end}] -> {end-start} elems')


if __name__ == '__main__':
    main()
