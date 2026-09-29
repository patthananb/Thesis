#!/usr/bin/env python3
"""Apply KMUTNB template typography to the Thai chapter files (chapter_thai/).
Body = Angsana New 16 pt; chapter titles 24 pt bold centred; unnumbered headings
18 pt bold centred; sections/subsections 16 pt bold; captions 16 pt. Code (Courier
New) runs are left untouched. Also fixes the Abstract heading mistranslation."""
import glob, re, os
from docx import Document
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from docx.enum.text import WD_ALIGN_PARAGRAPH

FONT = 'Angsana New'
DIR = 'chapter_thai'

UNNUMBERED = {'บทคัดย่อ', 'เชิงนามธรรม', 'กิตติกรรมประกาศ', 'เอกสารอ้างอิง',
              'ประวัติผู้แต่ง', 'ประวัติผู้เขียน', 'สารบัญ', 'สารบัญภาพ',
              'สารบัญตาราง', 'ศัพท์เฉพาะ', 'คำสำคัญ'}
CH = re.compile(r'^บทที่\s*\d')
SEC = re.compile(r'^\d+\.\d+\s')
SUB = re.compile(r'^\d+\.\d+\.\d+')
CAP = re.compile(r'^(รูปที่|ตารางที่|ภาพที่)\s')
APX = re.compile(r'^(ภาคผนวก|APPENDIX)')


def set_run(r, size_pt, bold=None, keep_font=False):
    rpr = r._element.get_or_add_rPr()
    if not keep_font:
        rf = rpr.find(qn('w:rFonts'))
        if rf is None:
            rf = OxmlElement('w:rFonts'); rpr.insert(0, rf)
        for a in ('w:ascii', 'w:hAnsi', 'w:cs', 'w:eastAsia'):
            rf.set(qn(a), FONT)
    for tag in ('w:sz', 'w:szCs'):
        e = rpr.find(qn(tag))
        if e is None:
            e = OxmlElement(tag); rpr.append(e)
        e.set(qn('w:val'), str(int(size_pt * 2)))
    if bold is not None:
        for tag in ('w:b', 'w:bCs'):
            e = rpr.find(qn(tag))
            if e is None:
                e = OxmlElement(tag); rpr.append(e)
            e.set(qn('w:val'), '1' if bold else '0')


def is_code(r):
    rpr = r._element.find(qn('w:rPr'))
    if rpr is None:
        return False
    rf = rpr.find(qn('w:rFonts'))
    return rf is not None and (rf.get(qn('w:ascii')) or '').startswith('Courier')


FIGCAP = ('รูปที่', 'ภาพที่')


def classify(text):
    t = text.strip()
    if not t:
        return (16, None, WD_ALIGN_PARAGRAPH.JUSTIFY)
    if CH.match(t):
        return (24, True, WD_ALIGN_PARAGRAPH.CENTER)
    if APX.match(t) and len(t) < 80:
        return (18, True, WD_ALIGN_PARAGRAPH.CENTER)
    if t.startswith('คำสำคัญ'):
        return (16, True, WD_ALIGN_PARAGRAPH.LEFT)
    if t in UNNUMBERED:
        return (18, True, WD_ALIGN_PARAGRAPH.CENTER)
    if SUB.match(t) or SEC.match(t):
        return (16, True, WD_ALIGN_PARAGRAPH.LEFT)
    return (16, None, WD_ALIGN_PARAGRAPH.JUSTIFY)


def _prev_is_image(p):
    el = p._p.getprevious()
    while el is not None and el.tag == qn('w:p') and not (el.findtext('.//' + qn('w:t')) or '').strip() \
            and el.find('.//' + qn('w:drawing')) is None:
        el = el.getprevious()           # skip blank paragraphs
    return el is not None and el.tag == qn('w:p') and el.find('.//' + qn('w:drawing')) is not None


def _next_is_table(p):
    el = p._p.getnext()
    while el is not None and el.tag == qn('w:p') and not (el.findtext('.//' + qn('w:t')) or '').strip():
        el = el.getnext()
    return el is not None and el.tag == qn('w:tbl')


def fmt_paragraph(p):
    t = p.text.strip()
    if CAP.match(t) and t.startswith(FIGCAP) and _prev_is_image(p):
        size, bold, align = 16, False, WD_ALIGN_PARAGRAPH.CENTER       # figure caption
    elif CAP.match(t) and t.startswith('ตารางที่') and _next_is_table(p):
        size, bold, align = 16, False, WD_ALIGN_PARAGRAPH.LEFT         # table caption
    else:
        size, bold, align = classify(p.text)
    if align is not None:
        p.alignment = align
    for r in p.runs:
        if not r.text:
            continue
        if is_code(r):
            set_run(r, 14, bold=None, keep_font=True)
        else:
            set_run(r, size, bold=bold)


def main():
    total = 0
    for f in sorted(glob.glob(os.path.join(DIR, '*.docx'))):
        d = Document(f)
        # fix Abstract mistranslation
        for p in d.paragraphs:
            for r in p.runs:
                if r.text and 'เชิงนามธรรม' in r.text:
                    r.text = r.text.replace('เชิงนามธรรม', 'บทคัดย่อ')
        for p in d.paragraphs:
            fmt_paragraph(p)
        for t in d.tables:
            for row in t.rows:
                for c in row.cells:
                    for p in c.paragraphs:
                        # table cells: 14 pt body, keep code
                        size, bold, _ = classify(p.text)
                        for r in p.runs:
                            if not r.text:
                                continue
                            if is_code(r):
                                set_run(r, 13, keep_font=True)
                            else:
                                set_run(r, 14, bold=bold)
        # set Normal style default font too
        try:
            nm = d.styles['Normal']
            nm.font.name = FONT
            rpr = nm.element.get_or_add_rPr()
            rf = rpr.find(qn('w:rFonts'))
            if rf is None:
                rf = OxmlElement('w:rFonts'); rpr.insert(0, rf)
            for a in ('w:ascii', 'w:hAnsi', 'w:cs', 'w:eastAsia'):
                rf.set(qn(a), FONT)
        except Exception:
            pass
        d.save(f)
        total += 1
        print('formatted', os.path.basename(f))
    print('done:', total, 'files')


if __name__ == '__main__':
    main()
