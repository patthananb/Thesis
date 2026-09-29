#!/usr/bin/env python3
"""Pass 2: read the rendered PDF, find the page of each entry (last occurrence of
its key), and write the page numbers into the TOC / LoF / LoT entry paragraphs."""
import json, re, subprocess
from docx import Document

DOC = 'senior_project_report.docx'
SIDE = 'frontmatter_keys.json'
PDF = '/tmp/lo3/senior_project_report.pdf'

HEADERS = {'toc': 'TABLE OF CONTENTS', 'lof': 'LIST OF FIGURES', 'lot': 'LIST OF TABLES'}
STOP = {'TABLE OF CONTENTS', 'LIST OF FIGURES', 'LIST OF TABLES', 'NOMENCLATURE',
        'ABSTRACT', 'ACKNOWLEDGEMENTS'}


def norm(s):
    return re.sub(r'\s+', ' ', s).strip()


def page_texts():
    txt = subprocess.run(['pdftotext', '-layout', PDF, '-'],
                         capture_output=True, text=True).stdout
    return [norm(pg) for pg in txt.split('\f')]


def find_page(pages, key, start_after=0):
    k = norm(key)
    last = None
    for i in range(start_after, len(pages)):
        if k and k in pages[i]:
            last = i + 1  # 1-based
    return last


def main():
    keys = json.load(open(SIDE))
    pages = page_texts()

    # Determine the page where front-matter lists end, to avoid matching the
    # TOC/LoF/LoT lines themselves (search content after the lists begin anyway;
    # last-occurrence already favours content, which is later in the document).
    doc = Document(DOC)
    paras = doc.paragraphs

    # Build, per section, the ordered list of entry paragraphs (between header and
    # next ALLCAPS stop header).
    def section_entries(header_text):
        hidx = next(i for i, p in enumerate(paras) if p.text.strip() == header_text)
        out = []
        for p in paras[hidx + 1:]:
            t = p.text.strip()
            if t in STOP:
                break
            if not t:
                continue
            out.append(p)
        return out

    report = {}
    for sec, header in HEADERS.items():
        ents = section_entries(header)
        ks = keys[sec]
        if len(ents) != len(ks):
            print(f'WARN {sec}: {len(ents)} paragraphs vs {len(ks)} keys')
        miss = 0
        for p, k in zip(ents, ks):
            pg = find_page(pages, k)
            if pg is None:
                miss += 1
                continue
            # last run holds the page placeholder
            runs = p.runs
            if runs:
                runs[-1].text = str(pg)
        report[sec] = (len(ents), miss)

    doc.save(DOC)
    for sec, (n, miss) in report.items():
        print(f'{sec}: {n} entries, {miss} unmatched')


if __name__ == '__main__':
    main()
