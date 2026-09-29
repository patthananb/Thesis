#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Split thesis_en.docx and thesis_th.docx into per-chapter .docx files.

Output:
    chapters/en/thesis_en_00_frontmatter.docx   (cover ... nomenclature)
    chapters/en/thesis_en_ch1.docx ... ch5.docx
    chapters/en/thesis_en_06_backmatter.docx    (references, biography, appendices)
    chapters/th/thesis_th_00_frontmatter.docx   ... (same layout)

Each output is a copy of the full document with everything outside the target
range deleted, so styles, numbering, headers, images, and fonts are preserved.

Run after the main build pipeline:  python3 build_scripts/split_editions.py
"""
import os
import shutil
import docx
from docx.oxml.ns import qn

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

EDITIONS = {
    'thesis_en.docx': ('en', ['Chapter 1', 'Chapter 2', 'Chapter 3',
                              'Chapter 4', 'Chapter 5'], 'References'),
    'thesis_th.docx': ('th', ['บทที่ 1', 'บทที่ 2', 'บทที่ 3',
                              'บทที่ 4', 'บทที่ 5'], 'เอกสารอ้างอิง'),
}


def body_children(doc):
    """Direct children of <w:body> except the trailing <w:sectPr>."""
    return [c for c in doc.element.body.iterchildren()
            if c.tag != qn('w:sectPr')]


def child_text(el):
    if el.tag != qn('w:p'):
        return ''
    return ''.join(t.text or '' for t in el.iter(qn('w:t'))).strip()


def child_style(el):
    if el.tag != qn('w:p'):
        return ''
    ps = el.find(qn('w:pPr') + '/' + qn('w:pStyle'))
    if ps is None:
        ppr = el.find(qn('w:pPr'))
        ps = None if ppr is None else ppr.find(qn('w:pStyle'))
    return '' if ps is None else (ps.get(qn('w:val')) or '')


def find_boundaries(doc, chapter_keys, refs_key):
    """Return list of (name, start_idx) over body children.
    Chapter starts must be Heading-1-styled paragraphs (plain body text may
    also begin with e.g. "บทที่ 2 ..." in the thesis-structure paragraph)."""
    kids = body_children(doc)
    bounds = [('00_frontmatter', 0)]
    for n, key in enumerate(chapter_keys, 1):
        idx = next(i for i, c in enumerate(kids)
                   if child_text(c).startswith(key)
                   and 'Heading1' in child_style(c).replace(' ', ''))
        bounds.append((f'ch{n}', idx))
    ch5_idx = bounds[-1][1]
    # must lie AFTER ch5 and be a heading (the cached TOC also contains a
    # "toc 1"-styled paragraph starting with refs_key — skip it)
    idx = next(i for i, c in enumerate(kids)
               if i > ch5_idx
               and child_text(c).startswith(refs_key)
               and child_style(c).replace(' ', '').startswith('Heading'))
    bounds.append(('06_backmatter', idx))
    return bounds, len(kids)


def extract(src, dst, start, end):
    """Copy src docx to dst keeping only body children [start, end)."""
    shutil.copyfile(src, dst)
    d = docx.Document(dst)
    kids = body_children(d)
    for i, c in enumerate(kids):
        if not (start <= i < end):
            c.getparent().remove(c)
    d.save(dst)
    strip_unused_media(dst)


def strip_unused_media(path):
    """Drop image parts (and their rels) no longer referenced by document.xml."""
    import re
    import zipfile
    tmp = path + '.tmp'
    with zipfile.ZipFile(path) as zin:
        docxml = zin.read('word/document.xml').decode('utf8')
        used_ids = set(re.findall(r'r:(?:embed|link)="([^"]+)"', docxml))
        rels = zin.read('word/_rels/document.xml.rels').decode('utf8')
        drop_targets = set()
        def rel_sub(m):
            rid, target = m.group(1), m.group(2)
            if 'image' in m.group(0) and rid not in used_ids:
                drop_targets.add('word/' + target.replace('../', ''))
                return ''
            return m.group(0)
        rels2 = re.sub(r'<Relationship [^>]*Id="([^"]+)"[^>]*Target="([^"]+)"[^>]*/>',
                       rel_sub, rels)
        with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                if item.filename in drop_targets:
                    continue
                data = zin.read(item.filename)
                if item.filename == 'word/_rels/document.xml.rels':
                    data = rels2.encode('utf8')
                zout.writestr(item, data)
    os.replace(tmp, path)


def main():
    for fname, (lang, chapter_keys, refs_key) in EDITIONS.items():
        src = os.path.join(ROOT, fname)
        if not os.path.exists(src):
            print('skip missing', fname)
            continue
        outdir = os.path.join(ROOT, 'chapters', lang)
        os.makedirs(outdir, exist_ok=True)
        d = docx.Document(src)
        bounds, total = find_boundaries(d, chapter_keys, refs_key)
        stem = os.path.splitext(fname)[0]
        for (name, start), (_, nxt) in zip(bounds, bounds[1:] + [(None, total)]):
            dst = os.path.join(outdir, f'{stem}_{name}.docx')
            extract(src, dst, start, nxt)
            print(f'{lang}/{os.path.basename(dst)}: children {start}-{nxt - 1}')


if __name__ == '__main__':
    main()
