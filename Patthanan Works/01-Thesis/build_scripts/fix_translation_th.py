#!/usr/bin/env python3
"""Fix translationese in thesis_th.docx (2026-07-04 QA pass).

Run-boundary-safe replacement: edits w:t text without deleting runs,
so SEQ/caption fields and per-run formatting survive.
Policy: keep ubiquitous English terms in English (stress test, word, frame).
"""
from docx import Document

DOCX = "thesis_th.docx"

# Ordered: specific before generic.
REPLACEMENTS = [
    # "production(-grade)" mistranslated as เชิงผลิต
    ("เชิงผลิตจริง", "ที่ใช้งานจริง"),
    ("เชิงผลิต", "ที่ใช้งานจริง"),
    # "budget" (resources) mistranslated as money
    ("ภายในงบประมาณทรัพยากรของบอร์ด", "ภายในขีดจำกัดทรัพยากรของบอร์ด"),
    ("ภายในงบประมาณของเฟิร์มแวร์", "ภายในขีดจำกัดทรัพยากรของเฟิร์มแวร์"),
    ("ก.3  งบประมาณการบิลด์และทรัพยากร", "ก.3  การใช้ทรัพยากรจากการบิลด์"),
    # stress test — keep English
    ("ชุดทดสอบความเครียด (stress test)", "ชุดทดสอบ stress test"),
    ("ทดสอบความเครียด", "ทดสอบ stress test"),
    # "frames the request" — กรอบ -> เฟรม
    ("กำหนดกรอบคำขอแต่ละคำสั่ง", "ประกอบเฟรมคำขอแต่ละคำสั่ง"),
    ("กรอบคำขอ", "เฟรมคำขอ"),
    # 16-bit "word" — keep English
    ("คำใน V-memory", "word ใน V-memory"),
    ("คู่คำสูง/ต่ำ", "คู่ word สูง/ต่ำ"),
    ("ลำดับคำ", "ลำดับ word"),
    # abstract: "contrasted with" / "live"
    ("ตัดกันอย่างชัดเจนกับ", "แตกต่างอย่างชัดเจนจาก"),
    ("บนเครือข่ายแบบสด", "บนเครือข่ายจริงขณะทำงาน"),
    ("ที่แพลตฟอร์มแลกเปลี่ยนกันแบบสด", "ที่แพลตฟอร์มแลกเปลี่ยนกันแบบเรียลไทม์"),
    # "fabricated values" / "data consumers"
    ("ค่าที่ถูกกุขึ้นมา", "ค่าที่ไม่ถูกต้อง"),
    ("ผู้บริโภคข้อมูลปลายทาง", "ปลายทางที่รับข้อมูล"),
    # translationese "its" (ของมัน)
    ("อินพุต mqtt_consumer ของมันจะสมัครรับข้อความ", "อินพุต mqtt_consumer จะสมัครรับข้อความ"),
    ("อินพุต mqtt_consumer ของมันสมัครรับข้อความ", "อินพุต mqtt_consumer สมัครรับข้อความ"),
    ("จุดสัญญาณดิจิทัลกับแอนะล็อกของมัน", "จุดสัญญาณดิจิทัลกับแอนะล็อกของพีแอลซี"),
    ("ลูปสำรวจแบบซิงโครนัสของมัน", "ลูปสำรวจแบบซิงโครนัสของไลบรารี"),
    ("ตัวจัดตารางงานแบบแทรกก่อน (preemptive) ของมัน", "ตัวจัดตารางงานแบบแทรกก่อน (preemptive) ของ SBC"),
    # "native" -> ในตัว
    ("รองรับได้เต็มรูปแบบโดยกำเนิด", "รองรับได้เต็มรูปแบบในตัว"),
    ("ที่มีมาโดยกำเนิด", "ที่มีมาให้ในตัว"),
    ("เซิร์ฟเวอร์โดยกำเนิด", "เซิร์ฟเวอร์ในตัว"),
    ("ไคลเอนต์โดยกำเนิด", "ไคลเอนต์ในตัว"),
    ("โดยกำเนิด", "ในตัว"),
    # watchdog paragraph: "clean restart" / "wedged"
    ("บังคับให้รีสตาร์ทอย่างสะอาด", "บังคับให้รีสตาร์ตใหม่"),
    ("ที่ค้างแข็ง", "ที่ค้าง"),
    ("รีสตาร์ท", "รีสตาร์ต"),
    # monitoring / weather / EE terms
    ("แดชบอร์ดเฝ้าระวังทรัพยากร", "แดชบอร์ดเฝ้าติดตามทรัพยากร"),
    ("แดชบอร์ดสำหรับค่าทางอากาศ", "แดชบอร์ดสำหรับค่าสภาพอากาศ"),
    ("แรงดันไฟ กระแสไฟ และกำลังไฟฟ้าจริง", "แรงดันไฟฟ้า กระแสไฟฟ้า และกำลังไฟฟ้าจริง"),
    ("กำลังไฟฟ้าที่ใช้งานจริง (Real Power)", "กำลังไฟฟ้าจริง (Real Power)"),
    ("กำลังไฟฟ้าที่ปรากฏ (Apparent Power)", "กำลังไฟฟ้าปรากฏ (Apparent Power)"),
    ("สะพานเชื่อม WebSocket", "บริดจ์ WebSocket"),
    ("เครื่องส่งสัญญาณอุณหภูมิ/ความชื้น XY-MD02", "โมดูลเซนเซอร์วัดอุณหภูมิและความชื้น XY-MD02"),
    # misc awkward phrasing
    ("ทำงานเสร็จภายในรอบสองวินาทีได้อย่างสบาย", "ทำงานเสร็จภายในรอบสองวินาทีโดยมีเวลาเหลือมาก"),
    ("ค่าผิดปกติแบบเดี่ยว", "ค่าผิดปกติ (outlier) หนึ่งค่า"),
    ("อ้างอิงจากการสร้างจริงชุดนี้", "อ้างอิงจากระบบที่สร้างขึ้นจริงในงานนี้"),
]

# exact-match table cells (avoid collateral hits)
CELL_EXACT = {"ความเครียด": "stress test"}


def replace_in_paragraph(p, old, new):
    """Replace old->new across run boundaries, preserving runs."""
    count = 0
    while True:
        runs = p.runs
        texts = [r.text for r in runs]
        full = "".join(texts)
        i = full.find(old)
        if i == -1:
            return count
        end = i + len(old)
        pos = 0
        inserted = False
        for r, t in zip(runs, texts):
            rs, re_ = pos, pos + len(t)
            pos = re_
            if re_ <= i or rs >= end:
                continue  # run outside match
            keep_head = t[: max(0, i - rs)]
            keep_tail = t[max(0, min(len(t), end - rs)):]
            if not inserted:
                r.text = keep_head + new + keep_tail
                inserted = True
            else:
                r.text = keep_head + keep_tail
        count += 1


def iter_paragraphs(doc):
    for p in doc.paragraphs:
        yield p
    for tbl in doc.tables:
        for row in tbl.rows:
            for cell in row.cells:
                for p in cell.paragraphs:
                    yield p


def main():
    doc = Document(DOCX)
    stats = {}
    for p in iter_paragraphs(doc):
        for old, new in REPLACEMENTS:
            n = replace_in_paragraph(p, old, new)
            if n:
                stats[old] = stats.get(old, 0) + n
    for tbl in doc.tables:
        for row in tbl.rows:
            for cell in row.cells:
                t = cell.text.strip()
                if t in CELL_EXACT:
                    replace_in_paragraph(cell.paragraphs[0], t, CELL_EXACT[t])
                    stats[t] = stats.get(t, 0) + 1
    doc.save(DOCX)
    for k, v in sorted(stats.items(), key=lambda x: -x[1]):
        print(f"{v:3d}  {k}")
    print(f"total: {sum(stats.values())} replacements")


if __name__ == "__main__":
    main()
