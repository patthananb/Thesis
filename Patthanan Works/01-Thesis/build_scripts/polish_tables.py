#!/usr/bin/env python3
"""Table polish: make the header row repeat on each page (w:tblHeader) and prevent
individual rows from being split across a page boundary (w:cantSplit). Applied to
every table in the combined document."""
from docx import Document
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

DOC = 'senior_project_report.docx'


def set_repeat_header(row):
    trPr = row._tr.get_or_add_trPr()
    if trPr.find(qn('w:tblHeader')) is None:
        e = OxmlElement('w:tblHeader')
        e.set(qn('w:val'), 'true')
        trPr.append(e)


def set_cant_split(row):
    trPr = row._tr.get_or_add_trPr()
    if trPr.find(qn('w:cantSplit')) is None:
        trPr.append(OxmlElement('w:cantSplit'))


def main():
    doc = Document(DOC)
    n = 0
    for t in doc.tables:
        rows = t.rows
        if not rows:
            continue
        set_repeat_header(rows[0])
        for r in rows:
            set_cant_split(r)
        n += 1
    doc.save(DOC)
    print(f'Polished {n} tables (repeat header + cantSplit).')


if __name__ == '__main__':
    main()
