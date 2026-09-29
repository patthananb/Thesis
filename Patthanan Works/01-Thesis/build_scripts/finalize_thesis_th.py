#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Finalize thesis_th.docx per KMUTNB EE template (Thai_Template_Bachelor Thesis May2023_EE.dotx).

Run AFTER build_thesis_th.py + thai_typography.py. This pass:
  1. Inserts all 20 figures from assets/figures with ภาพที่ X.Y captions (Caption
     style, below figure, centered) and cites each figure in the preceding text.
  2. Inserts real TOC / List-of-Figures / List-of-Tables fields (empty headings
     before) + hidden TC entries for every figure/table caption, and sets
     w:updateFields so Word refreshes them on open (or Ctrl+A, F9).
  3. Inserts the English Abstract page (template requires Thai + English).
  4. Replaces the Thai abstract with a <200-word version (template rule).
  5. Fills the ศัพท์เฉพาะ (Nomenclature) section.
  6. Makes body page numbering continuous (chapters no longer restart at 1).
  7. Page-break-before on every Heading 0 section (references, biography,
     appendices each start on a fresh page); keep-with-next on captions.
  8. Fixes Table 4.1 / Appendix ค table column widths (no 1-char wrapping).
  9. Normalizes AngsanaUPC -> Angsana New; shortens approval-page dotted
     signature lines so they fit on one line.
"""
import os
import docx
from docx.shared import Cm, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOC = os.path.join(ROOT, "thesis_th.docx")
FIG = os.path.join(ROOT, "assets", "figures")
FONT = "Angsana New"

# Normalize images before insertion: apply EXIF rotation (phone photos are
# orientation-6), re-encode headers python-docx can't parse, cap resolution.
import tempfile
from PIL import Image as PILImage, ImageOps
FIGCACHE = os.path.join(tempfile.gettempdir(), "figcache_th")
os.makedirs(FIGCACHE, exist_ok=True)

def norm_image(path):
    im = PILImage.open(path)
    im = ImageOps.exif_transpose(im)
    if max(im.size) > 2000:
        im.thumbnail((2000, 2000))
    out = os.path.join(FIGCACHE, os.path.splitext(os.path.basename(path))[0])
    if im.mode in ("RGBA", "P", "LA"):
        out += ".png"; im.save(out, "PNG")
    else:
        out += ".jpg"; im.convert("RGB").save(out, "JPEG", quality=88)
    return out

d = docx.Document(DOC)
paras = list(d.paragraphs)

# ---------------------------------------------------------------- helpers
def style_run(r, size=16, bold=False):
    rpr = r._element.get_or_add_rPr()
    rf = rpr.find(qn('w:rFonts'))
    if rf is None:
        rf = OxmlElement('w:rFonts'); rpr.insert(0, rf)
    for a in ('w:ascii', 'w:hAnsi', 'w:cs', 'w:eastAsia'):
        rf.set(qn(a), FONT)
    for tag in ('w:sz', 'w:szCs'):
        e = rpr.find(qn(tag))
        if e is None:
            e = OxmlElement(tag); rpr.append(e)
        e.set(qn('w:val'), str(size * 2))
    if bold:
        for tag in ('w:b', 'w:bCs'):
            e = rpr.find(qn(tag))
            if e is None:
                e = OxmlElement(tag); rpr.append(e)

def new_para_after(anchor_el, style=None):
    p = OxmlElement('w:p')
    anchor_el.addnext(p)
    para = docx.text.paragraph.Paragraph(p, d)
    if style:
        para.style = style
    return para

def keep_next(p):
    pf = p.paragraph_format
    pf.keep_with_next = True

def add_field(p, instr, result_text=""):
    """Add a complex field {instr} to paragraph p."""
    r1 = p.add_run(); fc = OxmlElement('w:fldChar')
    fc.set(qn('w:fldCharType'), 'begin'); fc.set(qn('w:dirty'), 'true')
    r1._element.append(fc)
    r2 = p.add_run(); it = OxmlElement('w:instrText')
    it.set(qn('xml:space'), 'preserve'); it.text = instr
    r2._element.append(it)
    r3 = p.add_run(); fs = OxmlElement('w:fldChar')
    fs.set(qn('w:fldCharType'), 'separate'); r3._element.append(fs)
    r4 = p.add_run(result_text); style_run(r4)
    r5 = p.add_run(); fe = OxmlElement('w:fldChar')
    fe.set(qn('w:fldCharType'), 'end'); r5._element.append(fe)

def add_tc(p, text, flag):
    """Hidden TC entry (for LoF/LoT) appended to caption paragraph p."""
    r1 = p.add_run(); fc = OxmlElement('w:fldChar')
    fc.set(qn('w:fldCharType'), 'begin'); r1._element.append(fc)
    r2 = p.add_run(); it = OxmlElement('w:instrText')
    it.set(qn('xml:space'), 'preserve')
    it.text = ' TC "%s" \\f %s \\l "1" ' % (text.replace('"', "'"), flag)
    r2._element.append(it)
    r3 = p.add_run(); fe = OxmlElement('w:fldChar')
    fe.set(qn('w:fldCharType'), 'end'); r3._element.append(fe)

# ---------------------------------------------------------------- 1. figures
# (filename, anchor paragraph index, caption text, width cm)
FIGS = [
    # figure 2.1 (figure2.1.png, Purdue diagram) removed per author request (Purdue dropped)
    # figures 2.2 (Hardware.png), 2.3 (protocols.png) and 2.4 (software.png) removed per author request
    ("system_architecture.png", 124, "ภาพที่ 3.1  สถาปัตยกรรมโดยรวมของแพลตฟอร์ม: เครือข่ายอุตสาหกรรมแบบมีสาย เกตเวย์ Raspberry Pi 4 และอุปกรณ์ขอบไร้สาย ESP32-S3", 14),
    ("waveshareesp32s3 xymd sdm.jpg", 126, "ภาพที่ 3.2  ฮาร์ดแวร์จริงของแพลตฟอร์ม: เกตเวย์ ESP32-S3-Relay-6CH, XY-MD02 และ SDM230 พร้อมการเดินสาย RS-485", 11),
    ("plc.jpg", 128,       "ภาพที่ 3.3  การเดินสายภายในแผงควบคุม Siemens LOGO! 24CE", 9.5),
    ("PLC_no_glowing_llights.jpg", 128, "ภาพที่ 3.4  แผงสาธิตพีแอลซีที่ประกอบเสร็จ พร้อมสวิตช์ปุ่มกดและไฟแสดงสถานะ", 9),
    ("data flow.png", 132, "ภาพที่ 3.5  เส้นทางการไหลของข้อมูลจากอุปกรณ์หน้างานผ่านเกตเวย์สู่ชั้นไอที (MBPoll, Node-RED, Mosquitto, Telegraf, InfluxDB และ Grafana)", 14),
    ("raspberrypi.jpg", 132, "ภาพที่ 3.6  Raspberry Pi 4 ที่ติดตั้งใช้งานจริงพร้อมแหล่งจ่ายไฟและสายอีเทอร์เน็ต", 10),
    ("figure3.9_iot_sniffer_packet_inspector.png", 134, "ภาพที่ 3.7  ส่วนต่อประสานผู้ใช้ของเครื่องมือ IoT-Sniffer ขณะถอดรหัสคำขอ Modbus TCP Write Multiple Registers", 14),
    ("MODBUS GATEWAY testbench.png", 140, "ภาพที่ 4.1  ชุดทดลองการศึกษา A บนเบรดบอร์ด: ESP32-S3 ทำหน้าที่เกตเวย์ Modbus RTU/TCP ร่วมกับตัวรับส่งสัญญาณ MAX3485 และ ESP32-C6 จำลองสเลฟ", 11.5),
    ("TempHum.png", 148,   "ภาพที่ 4.2  แดชบอร์ด Grafana แสดงอุณหภูมิและความชื้นจาก XY-MD02 ที่รับผ่านเกตเวย์แบบเรียลไทม์", 13),
    ("Powermeter.png", 148, "ภาพที่ 4.3  แดชบอร์ด Grafana แสดงค่าทางไฟฟ้าจากมิเตอร์ SDM230 (แรงดันไฟ กระแสไฟ และกำลังไฟฟ้าจริง)", 13),
    ("PiTelemetry.png", 150, "ภาพที่ 4.4  แดชบอร์ดเฝ้าระวังทรัพยากรของ Raspberry Pi (อุณหภูมิซีพียู โหลด และหน่วยความจำ) ที่เก็บผ่าน Telegraf", 13),
    ("piscreen.jpg", 150,  "ภาพที่ 4.5  จอสัมผัสขนาด 7 นิ้วของ Raspberry Pi แสดงแดชบอร์ด Grafana ในโหมดคีออสก์", 10.5),
    ("ESP32-S3-Relay-6CH-details-1.jpg", 239, "ภาพที่ จ.1  บอร์ด Waveshare ESP32-S3-Relay-6CH", 9.5),
    ("SiemensLOGO.jpeg", 247, "ภาพที่ จ.2  พีแอลซี Siemens LOGO! 24CE", 9),
    ("pi4.jpg", 253,       "ภาพที่ จ.3  Raspberry Pi 4 Model B (4 GB)", 9.5),
    ("xymd02.jpg", 259,    "ภาพที่ จ.4  เครื่องส่งสัญญาณอุณหภูมิ/ความชื้น XY-MD02", 5.5),
]

# cite figures in the anchor paragraph text (chapters only, not appendix จ)
from collections import OrderedDict
by_anchor = OrderedDict()
for fn, idx, cap, w in FIGS:
    by_anchor.setdefault(idx, []).append((fn, cap, w))

for idx, items in by_anchor.items():
    anchor = paras[idx]
    # in-text citation, e.g. "... ดังแสดงในภาพที่ 3.3 และภาพที่ 3.4"
    if idx < 230:
        nums = [cap.split()[1] for _, cap, _ in items]
        cite = " ดังแสดงใน" + " และ".join("ภาพที่ " + n for n in nums)
        r = anchor.add_run(cite)
        style_run(r)
    last_el = anchor._p
    for fn, cap, w in items:
        path = os.path.join(FIG, fn)
        assert os.path.exists(path), path
        path = norm_image(path)
        # image paragraph — force single (auto) line spacing, otherwise an
        # inherited "Exactly" line rule crops the inline image to one line
        pimg = new_para_after(last_el)
        pimg.alignment = WD_ALIGN_PARAGRAPH.CENTER
        pf = pimg.paragraph_format
        pf.line_spacing = 1.0
        pf.space_before = Pt(6); pf.space_after = Pt(0)
        keep_next(pimg)
        run = pimg.add_run()
        run.add_picture(path, width=Cm(w))
        # caption below, Caption style, centered
        pcap = new_para_after(pimg._p, style=d.styles['Caption'])
        pcap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        pcap.paragraph_format.space_after = Pt(6)
        rc = pcap.add_run(cap)
        style_run(rc)
        add_tc(pcap, cap, 'F')
        last_el = pcap._p
print("Inserted", len(FIGS), "figures.")

# TC entries for the existing table captions (for the List of Tables field)
for p in paras:
    if p.style.name == 'Caption' and p.text.strip().startswith('ตารางที่'):
        keep_next(p)
        add_tc(p, p.text.strip(), 'T')

# ---------------------------------------------------------------- 2. TOC fields
HINT = "(เปิดใน Word แล้วกด Ctrl+A ตามด้วย F9 เพื่ออัปเดตสารบัญ)"
toc_map = {
    54: r' TOC \o "1-4" \h \z \t "Heading 0,1" ',   # สารบัญ
    55: r' TOC \h \z \f F ',                        # สารบัญภาพ
    59: r' TOC \h \z \f T ',                        # สารบัญตาราง
}
for idx, instr in toc_map.items():
    head = paras[idx]
    pf = new_para_after(head._p)
    add_field(pf, instr, HINT)

# w:updateFields so Word refreshes fields when the document opens
se = d.settings.element
if se.find(qn('w:updateFields')) is None:
    uf = OxmlElement('w:updateFields'); uf.set(qn('w:val'), 'true')
    se.append(uf)

# stray empty Heading 0 (would show as blank TOC line)
if paras[61].text.strip() == '':
    paras[61].style = d.styles['Normal']

# ---------------------------------------------------------------- 3. English abstract
EN_ABS = docx.Document(os.path.join(ROOT, "thesis_en.docx"))
en_body = EN_ABS.paragraphs[47].text
en_kw = EN_ABS.paragraphs[49].text
anchor = paras[49]._p          # Thai คำสำคัญ line
ph = new_para_after(anchor, style=d.styles['Heading 0'])
ph.paragraph_format.page_break_before = True
rh = ph.add_run("Abstract"); style_run(rh, size=18, bold=True)
pb = new_para_after(ph._p, style=d.styles['Abstract'])
rb = pb.add_run(en_body); style_run(rb)
pk = new_para_after(pb._p, style=d.styles['Abstract'])
rk = pk.add_run(en_kw); style_run(rk)

# ---------------------------------------------------------------- 4. Thai abstract < 200 words
ABS_TH_SHORT = (
"งานนี้ออกแบบ สร้าง และประเมินแพลตฟอร์มไอโอทีเชิงอุตสาหกรรมต้นทุนต่ำเพื่อการศึกษา "
"ซึ่งผสานตัวควบคุมสามประเภทตามชั้นของแบบจำลอง Purdue ได้แก่ ไมโครคอนโทรลเลอร์ (MCU, ESP32-S3) "
"คอมพิวเตอร์บอร์ดเดี่ยว (SBC, Raspberry Pi 4) และพีแอลซี (PLC, Siemens LOGO! 24CE) "
"บนไมโครคอนโทรลเลอร์ได้พัฒนาเกตเวย์แปลงโพรโทคอล Modbus RTU เป็น TCP และ MQTT "
"โดยทดสอบไลบรารี Modbus โอเพนซอร์สแปดตัวบนฮาร์ดแวร์จริงเพื่อคัดเลือกหนึ่งตัว "
"แล้ววัดสมรรถนะของเกตเวย์ทั้งด้านเวลาแฝง อัตราการส่งข้อมูล และการใช้หน่วยความจำ "
"ชั้นไอทีใช้ซอฟต์แวร์โอเพนซอร์สทั้งหมด (Mosquitto, Telegraf, InfluxDB, Grafana และ Node-RED) "
"ซึ่งตัดกันชัดเจนกับซอฟต์แวร์เฉพาะผู้ผลิตที่พีแอลซีจำเป็นต้องใช้ "
"และได้พัฒนาเครื่องมือดักจับแพ็กเก็ตเชิงรับสำหรับสังเกตพฤติกรรมของ Modbus TCP และ MQTT "
"บนสายสัญญาณแบบสด ผลการทดลองแสดงว่าไมโครคอนโทรลเลอร์ราคาต่ำกว่า 2,000 บาทเพียงตัวเดียว"
"สามารถเชื่อมระบบโอทีอนุกรมเดิมเข้ากับแดชบอร์ดไอทีสมัยใหม่ได้ "
"และตัวควบคุมทั้งสามประเภทสอดคล้องกับชั้น Purdue ที่แตกต่างกัน "
"ในฐานะหัวข้อการเรียนรู้ที่เสริมกันมากกว่าจะแข่งขันกัน")
p47 = paras[47]
for r in list(p47.runs)[1:]:
    r._r.getparent().remove(r._r)
if p47.runs:
    p47.runs[0].text = ABS_TH_SHORT
else:
    style_run(p47.add_run(ABS_TH_SHORT))

# ---------------------------------------------------------------- 5. nomenclature
NOMEN = [
    ("IIoT", "ไอโอทีเชิงอุตสาหกรรม (Industrial Internet of Things)"),
    ("IT / OT", "เทคโนโลยีสารสนเทศ / เทคโนโลยีเชิงปฏิบัติการ"),
    ("MCU", "ไมโครคอนโทรลเลอร์ (microcontroller unit)"),
    ("SBC", "คอมพิวเตอร์บอร์ดเดี่ยว (single-board computer)"),
    ("PLC", "ตัวควบคุมโปรแกรมได้ (programmable logic controller)"),
    ("Modbus RTU / TCP", "โพรโทคอลสื่อสารอุตสาหกรรมแบบร้องขอ-ตอบสนอง บนสายอนุกรมหรือ TCP/IP"),
    ("MQTT", "โพรโทคอลรับส่งข้อความแบบเผยแพร่-สมัครสมาชิกสำหรับโทรมาตร"),
    ("TIG", "ชุดซอฟต์แวร์ Telegraf, InfluxDB และ Grafana"),
    ("RS-485", "มาตรฐานการสื่อสารอนุกรมแบบดิฟเฟอเรนเชียลสำหรับงานอุตสาหกรรม"),
    ("DMZ", "เขตกันชนของเครือข่ายระหว่างชั้นไอทีและโอที (demilitarized zone)"),
]
last = paras[63]._p
for term, defn in NOMEN:
    pn = new_para_after(last, style=d.styles['Nomenclature'])
    rn = pn.add_run(term + "\t" + defn); style_run(rn)
    last = pn._p

# ---------------------------------------------------------------- 6. page numbering
# body sections must continue numbering (only chapter 1 starts at 1)
secs = d.sections
for si in (3, 4, 5, 6):   # ch2..ch5
    pg = secs[si]._sectPr.find(qn('w:pgNumType'))
    if pg is not None and pg.get(qn('w:start')) is not None:
        del pg.attrib[qn('w:start')]

# ---------------------------------------------------------------- 7. page breaks
for p in paras:
    if p.style.name == 'Heading 0' and p.text.strip():
        p.paragraph_format.page_break_before = True

# ---------------------------------------------------------------- 8. table widths
def fix_table(t, widths_cm):
    tbl = t._tbl
    tblPr = tbl.tblPr
    layout = tblPr.find(qn('w:tblLayout'))
    if layout is None:
        layout = OxmlElement('w:tblLayout'); tblPr.append(layout)
    layout.set(qn('w:type'), 'fixed')
    # narrow cell side margins (0.1 cm) so numbers fit on one line
    mar = tblPr.find(qn('w:tblCellMar'))
    if mar is None:
        mar = OxmlElement('w:tblCellMar'); tblPr.append(mar)
    for side in ('w:left', 'w:right'):
        e = mar.find(qn(side))
        if e is None:
            e = OxmlElement(side); mar.append(e)
        e.set(qn('w:w'), '57'); e.set(qn('w:type'), 'dxa')
    grid = tbl.find(qn('w:tblGrid'))
    for gc, w in zip(grid.findall(qn('w:gridCol')), widths_cm):
        gc.set(qn('w:w'), str(int(w * 567)))
    for row in t.rows:
        for cell, w in zip(row.cells, widths_cm):
            cell.width = Cm(w)

fix_table(d.tables[1], [3.6, 1.7, 1.5, 1.5, 1.5, 1.5, 1.5, 1.8])   # ตารางที่ 4.1
fix_table(d.tables[6], [4.8, 1.9, 2.0, 1.7, 1.7, 2.4])                 # ภาคผนวก ค

# table cells inherit the body first-line indent, which crushes the first
# line to ~1 character in narrow columns -> remove indent inside all tables
for t in d.tables:
    for row in t.rows:
        for cell in row.cells:
            for p in cell.paragraphs:
                p.paragraph_format.first_line_indent = Cm(0)
                p.paragraph_format.left_indent = Cm(0)

# ---------------------------------------------------------------- 9. cleanup
# AngsanaUPC -> Angsana New
for rf in d.element.body.iter(qn('w:rFonts')):
    for a in ('w:ascii', 'w:hAnsi', 'w:cs', 'w:eastAsia'):
        if rf.get(qn(a)) == 'AngsanaUPC':
            rf.set(qn(a), FONT)

# approval page: shorten dotted signature lines / placeholder IDs to one line
DOTS = "…………………………………………"
for i in range(29, 44):
    p = paras[i]
    t = p.text
    if '………' in t:
        import re
        t2 = re.sub(r'[….]{20,}', DOTS, t)
        if p.runs:
            p.runs[0].text = t2
            for r in list(p.runs)[1:]:
                r._r.getparent().remove(r._r)
    elif '(xx' in t:
        import re
        t2 = re.sub(r'x{30,}', 'x' * 28, t)
        if p.runs:
            p.runs[0].text = t2
            for r in list(p.runs)[1:]:
                r._r.getparent().remove(r._r)

d.save(DOC)
print("Finalized:", DOC)
