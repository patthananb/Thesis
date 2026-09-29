#!/usr/bin/env python3
# Build thesis_v2.docx from the KMUTNB template: new title, abstract, Ch1 full bilingual,
# Ch2-5 + appendices skeleton. Front-matter section + header machinery preserved.
import copy, sys, os, glob, zipfile
from docx import Document
from docx.oxml.ns import qn

SK = "/Users/bean/.claude/skills/thai-docx/scripts"
sys.path.insert(0, SK)
from thai_docx import enforce_thai

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # Thesis paper/
DOTX = glob.glob(os.path.join(ROOT, "template", "*.dotx"))[0]
SRC  = os.path.join(os.path.dirname(os.path.abspath(__file__)), "template_base.docx")
OUT  = os.path.join(ROOT, "thesis_en.docx")
ENGLISH_ONLY = True   # body in English only; Thai edition is a later translation pass

# Regenerate a python-docx-readable .docx from the .dotx template (content-type patch).
def dotx_to_docx(src, out):
    tmpl = b'application/vnd.openxmlformats-officedocument.wordprocessingml.template.main+xml'
    docm = b'application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml'
    zin = zipfile.ZipFile(src, 'r'); zout = zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED)
    for it in zin.infolist():
        data = zin.read(it.filename)
        if it.filename == '[Content_Types].xml':
            data = data.replace(tmpl, docm)
        zout.writestr(it, data)
    zin.close(); zout.close()

dotx_to_docx(DOTX, SRC)
doc = Document(SRC)
paras = doc.paragraphs

# ---------- helpers ----------
def set_text(p, text):
    """Replace a paragraph's text, keep its style + first run's formatting."""
    runs = p.runs
    if runs:
        runs[0].text = text
        for r in runs[1:]:
            r._r.getparent().remove(r._r)
    else:
        p.add_run(text)

def find_idx(substr, start=0, end=None):
    end = len(paras) if end is None else end
    for i in range(start, end):
        if substr in paras[i].text:
            return i
    return -1

# ---------- TITLE / AUTHOR ----------
EN_TITLE = ("Design and Implementation of an Educational Industrial IoT Platform "
            "Combining SBC, MCU, and PLC")
TH_TITLE = ("การออกแบบและสร้างแพลตฟอร์มไอโอทีเชิงอุตสาหกรรมเพื่อการศึกษา "
            "โดยผสานคอมพิวเตอร์บอร์ดเดี่ยว ไมโครคอนโทรลเลอร์ และพีแอลซี")
STUDENT_TH = "นายพัทธนันท์\tพันธุมณี"
STUDENT_EN = "Mr. Patthanan\tBhandhumanee"
SID = "[Student ID]"

# Thai cover title sits at paras 0-2 region (Normal example title + instruction lines)
i = find_idx("การตรวจสอบการเกิดดิสชาร์จ")
if i >= 0:
    set_text(paras[i], EN_TITLE)   # all-English: first cover slot also English
i = find_idx('วิธีเขียน')
if i >= 0: set_text(paras[i], "")
i = find_idx('(สูงสุด 4 บรรทัด)')
if i >= 0: set_text(paras[i], "")
# Authors (first cover slot, English)
i = find_idx('นายดนัย', end=15)
if i >= 0: set_text(paras[i], STUDENT_EN)
i = find_idx('นางสาวสมใจ', end=15)
if i >= 0: set_text(paras[i], "")
i = find_idx('คํานําหน้าชื่อ')
if i >= 0: set_text(paras[i], "")
# English cover
i = find_idx('Monitoring of Partial Discharges')
if i >= 0: set_text(paras[i], EN_TITLE)
i = find_idx('How to Write')
if i >= 0: set_text(paras[i], "")
i = find_idx('(Maximum 4 lines)')
if i >= 0: set_text(paras[i], "")
i = find_idx('Mr. Kayan', end=35)
if i >= 0: set_text(paras[i], STUDENT_EN)
i = find_idx('Ms. Somjai', end=35)
if i >= 0: set_text(paras[i], "")
i = find_idx('(Style: Studentname)')
if i >= 0: set_text(paras[i], "")

# ---------- APPROVAL CERTIFICATE ----------
def repl(old, new, start=0):
    j = find_idx(old, start)
    if j >= 0: set_text(paras[j], new)
    return j

repl('ชื่อปริญญานิพนธ์\t:', 'ชื่อปริญญานิพนธ์\t:  ' + TH_TITLE)
repl('ชื่อ\t:  นายดนัย', 'ชื่อ\t:  นายพัทธนันท์  พันธุมณี \t\tรหัสนักศึกษา\t' + SID)
repl('\t:  นางสาวสมใจ', '')
repl('ที่ปรึกษา\t:', 'ที่ปรึกษา\t:  [อาจารย์ที่ปรึกษา]')
repl('ปีการศึกษา\t:', 'ปีการศึกษา\t:  [ปีการศึกษา]')
repl('Project\t:', 'Project\t:  ' + EN_TITLE)
repl('Name\t:  Mr. Kayan', 'Name\t:  Mr. Patthanan Bhandhumanee \t\tID. ' + SID)
repl('\t:  Ms. Somjai', '')
repl('Project Advisors\t:', 'Project Advisors\t:  [Advisor]')
repl('Academic Years\t:', 'Academic Years\t:  [Academic Year]')

# ---------- ABSTRACT (Thai + English, <200 words) ----------
ABS_EN = ("This work designs, builds, and evaluates a low-cost educational Industrial "
"Internet of Things (IIoT) platform that combines the three controller classes used in "
"modern automation: a microcontroller (MCU, ESP32-S3), a single-board computer (SBC, "
"Raspberry Pi 4), and a programmable logic controller (PLC, Siemens LOGO! 24CE). On the MCU "
"a Modbus RTU-to-TCP/MQTT gateway is implemented; ten open-source ESP32 Modbus libraries are "
"benchmarked on real hardware to select one, and the resulting gateway is measured for "
"latency, throughput, and flash/RAM use. Open-source software (Mosquitto, the TIG stack, "
"Node-RED) carries the IT and edge layers, contrasted with the proprietary LOGO! Soft Comfort "
"toolchain the PLC requires. An in-house passive sniffer decodes Modbus TCP and MQTT on the "
"wire and is used to demonstrate the unauthenticated-actuation and anonymous-publish gaps of "
"these protocols. Results show a single 1.5-USD-class MCU bridges legacy serial OT to an IT "
"dashboard within firmware budget, and that the three controller classes map cleanly onto "
"distinct Purdue layers as complementary, not competing, teaching subjects.")
ABS_KW_EN = "Keywords: Industrial IoT, Modbus gateway, IT/OT convergence, ESP32, PLC"

ABS_TH = ("งานนี้ออกแบบ สร้าง และประเมินแพลตฟอร์มไอโอทีเชิงอุตสาหกรรมต้นทุนต่ำเพื่อการศึกษา "
"ซึ่งผสานตัวควบคุมสามประเภทที่ใช้ในงานอัตโนมัติสมัยใหม่ ได้แก่ ไมโครคอนโทรลเลอร์ (ESP32-S3) "
"คอมพิวเตอร์บอร์ดเดี่ยว (Raspberry Pi 4) และพีแอลซี (Siemens LOGO! 24CE) "
"บนไมโครคอนโทรลเลอร์ได้พัฒนาเกตเวย์แปลงโพรโทคอล Modbus RTU เป็น TCP และ MQTT "
"พร้อมทดสอบไลบรารี Modbus โอเพนซอร์สสำหรับ ESP32 จำนวนสิบตัวบนฮาร์ดแวร์จริงเพื่อคัดเลือก "
"และวัดสมรรถนะของเกตเวย์ทั้งด้านเวลาแฝง อัตราการส่งข้อมูล และการใช้หน่วยความจำแฟลช/แรม "
"ชั้นไอทีและชั้นขอบใช้ซอฟต์แวร์โอเพนซอร์ส (Mosquitto, ชุด TIG, Node-RED) "
"ซึ่งตัดกับซอฟต์แวร์เฉพาะของผู้ผลิตอย่าง LOGO! Soft Comfort ที่พีแอลซีจำเป็นต้องใช้ "
"และได้พัฒนาเครื่องมือดักจับแพ็กเก็ตเพื่อถอดรหัส Modbus TCP และ MQTT "
"สำหรับสาธิตช่องโหว่การสั่งงานโดยไม่ต้องยืนยันตัวตนของโพรโทคอลเหล่านี้ "
"ผลการทดลองแสดงว่าไมโครคอนโทรลเลอร์ราคาต่ำเชื่อมระบบโอทีอนุกรมเดิมเข้ากับแดชบอร์ดไอทีได้ภายในงบประมาณเฟิร์มแวร์ "
"และตัวควบคุมทั้งสามประเภทเหมาะกับชั้น Purdue ที่แตกต่างกันอย่างเสริมกัน")
ABS_KW_TH = "คำสำคัญ: ไอโอทีอุตสาหกรรม, เกตเวย์ Modbus, การหลอมรวมไอทีและโอที, ESP32, พีแอลซี"

j = find_idx('(สไตล์: บทคัดย่อ)')
if j >= 0: set_text(paras[j], ABS_TH)
j = find_idx('คําสําคัญ: การประเมิน')
if j >= 0: set_text(paras[j], ABS_KW_TH)
j = find_idx('(Style: Abstract)')
if j >= 0: set_text(paras[j], ABS_EN)
j = find_idx('Keywords: Condition Evaluation')
if j >= 0: set_text(paras[j], ABS_KW_EN)

# ---------- ACKNOWLEDGEMENTS (English) ----------
ACK_EN = ("The author thanks the project advisor, the examination committee, and the faculty of "
"the Department of Electrical and Computer Engineering, King Mongkut's University of Technology "
"North Bangkok, for their guidance and support throughout this work, and family and classmates "
"for their constant encouragement.")
j = find_idx('(สไตล์: กิตติกรรมประกาศ)')
if j >= 0: set_text(paras[j], ACK_EN)

# ---------- TRUNCATE example chapters, keep front-matter section ----------
# Anchor on the FIRST Heading 1 styled paragraph (the template's first example chapter).
# NB: do NOT match the Thai word 'บทนำ' by text — it also occurs in the TOC, which would
# cut the document above the abstract/acknowledgements/TOC and delete the whole front matter.
ch1_h = next(i for i, p in enumerate(paras) if p.style.name == 'Heading 1')
# the section-break para is the nearest preceding paragraph holding a sectPr
fm_close = None
for k in range(ch1_h - 1, -1, -1):
    pPr = paras[k]._p.find(qn('w:pPr'))
    if pPr is not None and pPr.find(qn('w:sectPr')) is not None:
        fm_close = paras[k]._p
        break
assert fm_close is not None, "front-matter section break not found"

# capture a chapter section break to clone (from a later chapter break para 276 region)
chap_sect_src = None
for k in range(ch1_h, len(paras)):
    pPr = paras[k]._p.find(qn('w:pPr'))
    if pPr is not None and pPr.find(qn('w:sectPr')) is not None:
        chap_sect_src = pPr.find(qn('w:sectPr'))
        break
assert chap_sect_src is not None
CHAP_SECT = copy.deepcopy(chap_sect_src)

body = doc.element.body
final_sect = body.find(qn('w:sectPr'))   # document-level trailing sectPr
# remove everything after fm_close except the final body sectPr
el = fm_close.getnext()
while el is not None:
    nxt = el.getnext()
    if el is final_sect:
        el = nxt; continue
    body.remove(el)
    el = nxt

# ---------- content builders ----------
def add(text="", style="Normal"):
    return doc.add_paragraph(text, style=style)

def section_break():
    p = doc.add_paragraph("", style="Normal")
    pPr = p._p.get_or_add_pPr()
    pPr.append(copy.deepcopy(CHAP_SECT))
    return p

def H1(en):  # chapter title (single Heading 1 line)
    add(en, "Heading 1")

def H2(t): add(t, "Heading 2")
def H3(t): add(t, "Heading 3")

def table(caption, header, rows, style="Table Grid"):
    add(caption, "Caption")               # table caption goes ABOVE the table
    t = doc.add_table(rows=1, cols=len(header))
    try: t.style = style
    except Exception: pass
    for j, h in enumerate(header):
        t.rows[0].cells[j].text = str(h)
    for r in rows:
        cells = t.add_row().cells
        for j, v in enumerate(r):
            cells[j].text = str(v)
    return t

def code(line):                            # command / code line
    p = add(line, "Normal")
    for r in p.runs: r.font.name = "Consolas"
    return p
def TH(t):
    if ENGLISH_ONLY:
        return None
    r = add("", "Normal"); run = r.add_run(t); run.italic = True; return r

# ============ CHAPTER 1 — INTRODUCTION (full, bilingual) ============
H1("Chapter 1  Introduction")

H2("1.1  Background and Motivation")
add("Industry 4.0 has pushed factories to expose shop-floor data to information-technology (IT) "
"systems for monitoring, analytics, and remote supervision. Yet the operational-technology (OT) "
"equipment that runs physical processes still speaks decades-old protocols. Modbus, introduced in "
"1979, remains one of the most widely deployed field protocols, and in its serial RTU form it runs "
"over RS-485 with no authentication, no encryption, and no native path to an IP network [1]. "
"Replacing such field hardware wholesale is rarely economic, so the practical problem is not "
"replacement but integration: how to lift legacy OT signals into modern IT dashboards at low cost "
"and without compromising the determinism the OT side depends on.")
TH("อุตสาหกรรม 4.0 ผลักดันให้โรงงานเปิดเผยข้อมูลหน้างานสู่ระบบเทคโนโลยีสารสนเทศ (ไอที) "
"เพื่อการเฝ้าระวัง วิเคราะห์ และควบคุมระยะไกล แต่อุปกรณ์เทคโนโลยีเชิงปฏิบัติการ (โอที) "
"ที่ควบคุมกระบวนการจริงยังคงใช้โพรโทคอลที่มีอายุหลายสิบปี โพรโทคอล Modbus ที่เริ่มใช้เมื่อปี ค.ศ. 1979 "
"ยังเป็นหนึ่งในโพรโทคอลหน้างานที่แพร่หลายที่สุด และในรูปแบบอนุกรม RTU ทำงานบน RS-485 "
"โดยไม่มีการยืนยันตัวตน ไม่มีการเข้ารหัส และไม่มีเส้นทางสู่เครือข่ายไอพีโดยกำเนิด [1] "
"การเปลี่ยนอุปกรณ์หน้างานทั้งหมดมักไม่คุ้มค่า ปัญหาที่แท้จริงจึงไม่ใช่การเปลี่ยนทดแทน "
"แต่เป็นการบูรณาการ คือจะยกสัญญาณโอทีเดิมขึ้นสู่แดชบอร์ดไอทีสมัยใหม่ด้วยต้นทุนต่ำได้อย่างไร "
"โดยไม่ลดทอนความแน่นอนเชิงเวลาที่ฝั่งโอทีต้องการ")

add("Three classes of controller dominate this landscape, and a student entering the field must "
"understand all three: the microcontroller (MCU), the single-board computer (SBC), and the "
"programmable logic controller (PLC). They differ not only in compute and I/O but in something "
"this work treats as a first-class concern — their software ecosystems. The MCU and SBC are "
"programmed with well-known open-source software (the Arduino core and PlatformIO, Linux and "
"Docker, the Telegraf-InfluxDB-Grafana “TIG” stack, Node-RED, and the MQTT broker Mosquitto), "
"whereas the PLC is tied to a proprietary vendor toolchain — for the Siemens LOGO! used here, "
"LOGO! Soft Comfort. That contrast in openness is itself a lesson about vendor lock-in in OT.")
TH("ตัวควบคุมสามประเภทครองภูมิทัศน์นี้ และนักศึกษาที่เข้าสู่สาขานี้ต้องเข้าใจทั้งสามประเภท ได้แก่ "
"ไมโครคอนโทรลเลอร์ (MCU) คอมพิวเตอร์บอร์ดเดี่ยว (SBC) และพีแอลซี (PLC) "
"ทั้งสามต่างกันไม่เพียงด้านการประมวลผลและI/O แต่ยังต่างกันในสิ่งที่งานนี้ถือเป็นประเด็นสำคัญ "
"คือระบบนิเวศซอฟต์แวร์ MCU และ SBC เขียนโปรแกรมด้วยซอฟต์แวร์โอเพนซอร์สที่เป็นที่รู้จัก "
"(Arduino core และ PlatformIO, Linux และ Docker, ชุด TIG, Node-RED และโบรกเกอร์ MQTT Mosquitto) "
"ขณะที่พีแอลซีผูกกับซอฟต์แวร์เฉพาะของผู้ผลิต ซึ่งสำหรับ Siemens LOGO! ที่ใช้ในงานนี้คือ LOGO! Soft Comfort "
"ความต่างด้านความเปิดกว้างนี้เองเป็นบทเรียนเรื่องการผูกติดผู้ผลิตในงานโอที")

H2("1.2  Problem Statement")
add("Teaching IT/OT integration well requires hardware a student can touch, break, and instrument. "
"Commercial IIoT trainers are expensive and closed, hiding exactly the wire-level behaviour a "
"learner needs to see. Three gaps follow. First, no low-cost bench exposes all three controller "
"classes and real industrial protocols together. Second, although many open-source ESP32 Modbus "
"gateway libraries exist, there is no empirical comparison guiding which to use, so a builder "
"chooses blind. Third, the insecurity of Modbus and MQTT is widely asserted but seldom shown "
"on real traffic in a classroom-safe way.")
TH("การสอนการบูรณาการไอที/โอทีอย่างได้ผลต้องอาศัยฮาร์ดแวร์ที่นักศึกษาสัมผัส ทดลอง และตรวจวัดได้ "
"ชุดฝึกไอโอทีเชิงพาณิชย์มีราคาสูงและปิดตัว ซ่อนพฤติกรรมระดับสายสัญญาณที่ผู้เรียนจำเป็นต้องเห็น "
"จึงเกิดช่องว่างสามประการ ประการแรก ไม่มีชุดทดลองต้นทุนต่ำที่แสดงตัวควบคุมทั้งสามประเภทพร้อมโพรโทคอลอุตสาหกรรมจริงไปด้วยกัน "
"ประการที่สอง แม้จะมีไลบรารีเกตเวย์ Modbus โอเพนซอร์สสำหรับ ESP32 จำนวนมาก "
"แต่ไม่มีการเปรียบเทียบเชิงประจักษ์ว่าควรเลือกใช้ตัวใด ผู้พัฒนาจึงเลือกอย่างไร้ข้อมูล "
"ประการที่สาม ความไม่ปลอดภัยของ Modbus และ MQTT ถูกกล่าวอ้างทั่วไปแต่ไม่ค่อยถูกสาธิตบนการสื่อสารจริงในแบบที่ปลอดภัยต่อห้องเรียน")

H2("1.3  Objectives")
add("1)  Design and build a low-cost educational IIoT platform that integrates an MCU "
"(ESP32-S3), an SBC (Raspberry Pi 4), and a PLC (Siemens LOGO! 24CE) across the Purdue model layers.")
add("2)  Survey related work to identify the open-source software most commonly adopted in IIoT "
"applications — notably the MQTT broker, Node-RED, and the TIG stack (Telegraf, InfluxDB, "
"Grafana) — and adopt these as the platform's edge and IT layers.")
add("3)  Implement a Modbus RTU-to-TCP/MQTT gateway on the MCU and empirically evaluate ten "
"open-source ESP32 Modbus libraries to select one for the platform.")
add("4)  Measure the resulting gateway’s performance: request latency, throughput, flash/RAM "
"footprint, and robustness under fault injection.")
add("5)  Compare two of the commonly adopted MQTT-to-InfluxDB ingestion pipelines, Node-RED and "
"Telegraf, on memory, latency, throughput, and recovery.")
add("6)  Develop a passive IoT sniffer that decodes Modbus TCP and MQTT, and use it to demonstrate "
"the IT/OT security gaps of these protocols.")
TH("วัตถุประสงค์ของปริญญานิพนธ์ ได้แก่ (1) ออกแบบและสร้างแพลตฟอร์มไอโอทีอุตสาหกรรมต้นทุนต่ำเพื่อการศึกษา "
"ที่ผสาน MCU (ESP32-S3), SBC (Raspberry Pi 4) และ PLC (Siemens LOGO! 24CE) ตามชั้นแบบจำลอง Purdue "
"(2) สำรวจงานที่เกี่ยวข้องเพื่อระบุซอฟต์แวร์โอเพนซอร์สที่ใช้กันแพร่หลายในงานไอโอทีอุตสาหกรรม ได้แก่ โบรกเกอร์ MQTT, Node-RED และชุด TIG และนำมาใช้เป็นชั้นขอบและชั้นไอทีของแพลตฟอร์ม "
"(3) พัฒนาเกตเวย์ Modbus RTU เป็น TCP/MQTT บน MCU และประเมินไลบรารี Modbus โอเพนซอร์สสิบตัวเพื่อคัดเลือก "
"(4) วัดสมรรถนะของเกตเวย์ทั้งเวลาแฝง อัตราการส่ง การใช้แฟลช/แรม และความทนทานต่อความผิดพร่อง "
"(5) เปรียบเทียบไปป์ไลน์รับข้อมูล MQTT สู่ InfluxDB สองแบบคือ Node-RED และ Telegraf "
"และ (6) พัฒนาเครื่องมือดักจับแพ็กเก็ตเชิงรับที่ถอดรหัส Modbus TCP และ MQTT เพื่อสาธิตช่องโหว่ความปลอดภัยไอที/โอที")

H2("1.4  Scope and Limitations")
add("The platform is a single-site LAN bench. In scope: Modbus RTU and TCP, MQTT, the TIG stack, "
"the passive sniffer, and a live security demonstration. Out of scope: OPC-UA, industrial "
"certification, hazardous-area (ATEX) deployment, and production hardening. Security mitigations "
"are discussed and partially implemented but not exhaustively deployed. Library results are "
"obtained on one ESP32-S3 hardware revision and may shift on other revisions.")
TH("แพลตฟอร์มเป็นชุดทดลองบนเครือข่ายภายในสถานที่เดียว ขอบเขตครอบคลุม Modbus RTU และ TCP, MQTT, ชุด TIG, "
"เครื่องมือดักจับเชิงรับ และการสาธิตความปลอดภัยแบบสด ส่วนที่อยู่นอกขอบเขต ได้แก่ OPC-UA "
"การรับรองมาตรฐานอุตสาหกรรม การติดตั้งในพื้นที่อันตราย (ATEX) และการทำให้พร้อมใช้งานจริง "
"มาตรการลดความเสี่ยงด้านความปลอดภัยถูกอภิปรายและนำไปใช้บางส่วน แต่ไม่ได้ติดตั้งครบถ้วน "
"ผลการประเมินไลบรารีได้จากฮาร์ดแวร์ ESP32-S3 รุ่นเดียวและอาจเปลี่ยนแปลงในรุ่นอื่น")

H2("1.5  Thesis Organization")
add("Chapter 2 reviews IT/OT convergence, the Purdue model, the Modbus and MQTT protocols, the "
"three controller classes and their open-source versus proprietary toolchains, the monitoring "
"stack, and related work. Chapter 3 presents the platform architecture and the implementation of "
"each layer, including the MCU gateway firmware, the IT stack, and the sniffer. Chapter 4 reports "
"the evaluation: the Modbus library benchmark, gateway performance, the Node-RED versus Telegraf "
"comparison, and the security demonstration. Chapter 5 discusses the findings, the fit of each "
"controller class, limitations, and future work.")
TH("บทที่ 2 ทบทวนการหลอมรวมไอที/โอที แบบจำลอง Purdue โพรโทคอล Modbus และ MQTT "
"ตัวควบคุมสามประเภทพร้อมซอฟต์แวร์โอเพนซอร์สเทียบกับซอฟต์แวร์เฉพาะผู้ผลิต ชุดเฝ้าระวัง และงานที่เกี่ยวข้อง "
"บทที่ 3 นำเสนอสถาปัตยกรรมแพลตฟอร์มและการพัฒนาแต่ละชั้น รวมถึงเฟิร์มแวร์เกตเวย์บน MCU ชุดไอที และเครื่องมือดักจับ "
"บทที่ 4 รายงานการประเมิน ได้แก่ การทดสอบไลบรารี Modbus สมรรถนะเกตเวย์ การเปรียบเทียบ Node-RED กับ Telegraf "
"และการสาธิตความปลอดภัย บทที่ 5 อภิปรายผล ความเหมาะสมของตัวควบคุมแต่ละประเภท ข้อจำกัด และงานในอนาคต")

# ============ CHAPTERS 2-5 SKELETON ============
def stub():
    p = add("[to be written]", "Normal")
    p.runs[0].italic = True

section_break(); H1("Chapter 2  Background and Related Work")
add("This chapter establishes the theory needed to justify the platform's design. It begins with "
"the IT/OT divide and the Purdue reference model, then describes the industrial protocols, the "
"three controller classes and their software ecosystems, the monitoring stack, and the security "
"properties of the protocols involved. It closes with related work and the research gap this work "
"addresses.")

H2("2.1  IT/OT Convergence and the Purdue Reference Model")
add("Industrial automation has historically separated two technology domains. Operational "
"technology (OT) comprises the controllers, sensors, and actuators that drive physical processes, "
"and prizes determinism, availability, and safety. Information technology (IT) comprises the "
"servers, databases, and dashboards that store and present data, and prizes throughput, "
"flexibility, and confidentiality. Industry 4.0 demands that OT data reach IT systems in real time, "
"a goal known as IT/OT convergence [1], [2].")
add("The Purdue Enterprise Reference Architecture, adopted by the ISA-95 standard, organises a "
"plant into hierarchical levels [3]. Level 0 is the physical process (sensors and actuators); "
"Level 1 is basic control (PLCs and controllers); Level 2 is area supervision (SCADA, HMIs); "
"Level 3 is site operations (historians, manufacturing execution); and Levels 4-5 are enterprise "
"IT. A demilitarised zone is conventionally placed between Levels 3 and 4 to mediate IT/OT "
"traffic. The model is used throughout this thesis to assign each device a layer and to reason "
"about where data crosses the IT/OT boundary.")

H2("2.2  Industrial Communication Protocols")
H3("2.2.1  Modbus RTU")
add("Modbus, published by Modicon in 1979, is a request-response protocol in which a single master "
"polls one or more slaves [4]. In its RTU variant the application data unit (ADU) is carried over "
"a serial line, typically RS-485, and consists of a one-byte slave address, a one-byte function "
"code, a data field, and a two-byte cyclic redundancy check (CRC-16). Function codes select the "
"data model: FC01/FC05 address discrete coils, FC02 discrete inputs, FC03/FC06/FC16 holding "
"registers, and FC04 input registers. Modbus RTU has no authentication, no encryption, and no "
"addressing beyond the slave id, which makes it simple to implement but trivially open on the "
"wire.")
H3("2.2.2  Modbus TCP")
add("Modbus TCP carries the same protocol data unit over TCP port 502, replacing the serial frame "
"with a seven-byte Modbus Application Protocol (MBAP) header: a transaction identifier, a protocol "
"identifier (always zero), a length field, and a unit identifier [4]. The CRC is dropped because "
"TCP already guarantees integrity. Because the function codes and register model are unchanged, a "
"device that speaks both variants can act as a protocol gateway, exposing serial RTU slaves to any "
"IP host. This equivalence is the basis of the gateway built in Chapter 3.")
H3("2.2.3  MQTT")
add("Message Queuing Telemetry Transport (MQTT) is a lightweight publish-subscribe protocol "
"standardised as ISO/IEC 20922 and widely used in IoT [5]. Clients publish messages to a topic on "
"a broker, and the broker forwards them to all subscribers of that topic, decoupling producers "
"from consumers. Three quality-of-service levels are offered: QoS 0 (at most once), QoS 1 (at "
"least once, with PUBACK), and QoS 2 (exactly once). Features such as retained messages and the "
"last-will-and-testament support intermittent connectivity. MQTT brokers permit anonymous access "
"by default, a convenience that, as Section 2.6 discusses, is also a hazard.")

H2("2.3  Controller Classes: MCU, SBC, and PLC")
add("Three classes of programmable device span modern automation, and a complete education must "
"cover all three.")
H3("2.3.1  Microcontroller (MCU)")
add("A microcontroller integrates a processor, memory, and peripherals on a single chip. The "
"ESP32-S3 used here is a dual-core Xtensa device with integrated Wi-Fi, multiple UARTs, and a few "
"hundred kilobytes of RAM, running the Arduino core over the FreeRTOS real-time kernel. Its low "
"cost, deterministic cooperative scheduling, and native serial and wireless interfaces make it a "
"natural protocol-conversion node at the edge. Its constraints are equally instructive: flash and "
"RAM are scarce, so resource use must be measured rather than assumed.")
H3("2.3.2  Single-Board Computer (SBC)")
add("A single-board computer runs a full operating system on commodity hardware. The Raspberry Pi "
"4 used here runs Linux with a complete IP stack and the Docker container runtime, hosting the "
"data-plane services. It trades the MCU's determinism (a general-purpose scheduler introduces "
"jitter) for the flexibility of a general computer: any service that runs in a container can run "
"on it.")
H3("2.3.3  Programmable Logic Controller (PLC)")
add("A programmable logic controller is a ruggedised industrial computer designed for "
"deterministic control. It executes a fixed scan cycle (read inputs, solve program, write "
"outputs) and is programmed in the IEC 61131-3 languages, most commonly ladder diagram (LAD) and "
"function block diagram (FBD). The Siemens LOGO! 24CE used here provides industrial 24 V DC I/O "
"and a native Modbus TCP server, but is programmed only through the vendor's LOGO! Soft Comfort "
"software. It contributes real industrial signalling and certified hardware that neither the MCU "
"nor the SBC offers.")

H2("2.4  Open-Source versus Proprietary Toolchains")
add("Beyond compute and I/O, the three classes differ sharply in the openness of their software, "
"a distinction this work treats as a first-class teaching point. The MCU is programmed with the "
"open-source Arduino core and the PlatformIO build system; the SBC runs open-source Linux, Docker, "
"the Telegraf-InfluxDB-Grafana stack, Node-RED, and the Mosquitto MQTT broker. The PLC, by "
"contrast, can be programmed only through Siemens' proprietary LOGO! Soft Comfort, a closed, "
"licensed application. The open stack is inspectable, scriptable, free to reproduce, and "
"community-supported; the proprietary stack offers vendor support and certification but binds the "
"user to one supplier. This contrast lets students experience vendor lock-in directly rather than "
"as an abstraction, and motivates the platform's deliberate mix of both worlds.")

H2("2.5  Time-Series Monitoring Stack (TIG) and MQTT")
add("Telemetry in this work is stored and visualised with the TIG stack, a widely used open-source "
"combination. Telegraf is a plug-in-based collection agent; its mqtt_consumer input subscribes to "
"the broker and its influxdb_v2 output writes to the database, while additional inputs gather host "
"metrics [6]. InfluxDB is a time-series database that stores points in buckets and is queried with "
"the Flux language [7]. Grafana renders dashboards from those queries and supports anonymous "
"read-only viewing for kiosk displays [8]. The Mosquitto broker connects the edge to this stack "
"over MQTT. All four components are distributed as Docker images and orchestrated with Docker "
"Compose, which pins image tags and injects secrets through environment variables.")

H2("2.6  Security Challenges in IT/OT Environments")
add("The protocols that make integration easy also make it dangerous. Modbus, in both RTU and TCP "
"forms, authenticates nothing: any host that can reach a Modbus TCP server on port 502 can issue "
"write commands such as FC05 (write single coil) and actuate physical outputs [9]. MQTT brokers "
"that allow anonymous access let any LAN host subscribe to every topic and publish forged "
"telemetry. When OT and IT share one flat network, the Purdue separation collapses and a single "
"compromised IT host gains direct control of field equipment. These weaknesses are widely "
"documented but seldom demonstrated to learners on live traffic; Chapter 4 does so with the "
"sniffer developed in this work.")

H2("2.7  Related Work and Research Gap")
add("Prior work has built ESP32-based Modbus gateways and IoT monitoring testbeds, and surveys of "
"IIoT protocols and the Purdue model are plentiful [1]-[5]. A consistent finding across this "
"literature is that a small set of open-source tools recurs in IIoT data pipelines: the MQTT "
"broker as the messaging fabric, Node-RED as the flow-based integration layer, and the TIG stack "
"(Telegraf, InfluxDB, Grafana) for collection, storage, and visualisation [6]-[8]. This work "
"adopts that de-facto stack rather than inventing bespoke components, which keeps the platform "
"familiar and reproducible. However, three gaps remain. First, "
"existing testbeds typically demonstrate one controller class rather than integrating the MCU, "
"SBC, and PLC together so their roles can be compared. Second, although numerous open-source "
"ESP32 Modbus libraries exist, no published empirical benchmark compares them on the same hardware "
"to guide selection. Third, the insecurity of Modbus and MQTT is asserted in the literature but "
"rarely shown in a reproducible, classroom-safe demonstration. This thesis addresses all three: it "
"integrates the three controller classes on one low-cost bench, benchmarks ten Modbus libraries to "
"select a gateway implementation, and demonstrates the protocol weaknesses live with a purpose-"
"built sniffer.")

section_break(); H1("Chapter 3  System Design and Implementation")
add("This chapter presents the platform from architecture down to implementation. It first maps "
"every device onto a Purdue level and defines the data paths, then justifies the hardware, and "
"finally details each layer: the PLC, the MCU gateway firmware, the containerised IT stack, and "
"the IoT sniffer.")

H2("3.1  Overall Platform Architecture")
add("The platform integrates the three controller classes on a single local-area network and "
"arranges them by Purdue level. At Level 0 are the field instruments: an XY-MD02 temperature and "
"humidity sensor and an Eastron SDM230 single-phase power meter, both Modbus RTU slaves on an "
"RS-485 bus. At Level 1 is the Siemens LOGO! 24CE PLC, performing deterministic control with "
"industrial I/O. At Level 2 is the ESP32-S3 edge gateway, converting protocols. At Level 3 is the "
"Raspberry Pi 4, hosting the MQTT broker and the TIG data plane. The design exposes two data "
"paths. Path A is direct Modbus TCP: any LAN host, including the PLC acting as a master, polls a "
"Modbus TCP server. Path B is the telemetry pipeline: the ESP32-S3 polls the RTU sensors, "
"publishes JSON over MQTT, and Telegraf ingests it into InfluxDB for display in Grafana.")

H2("3.2  Hardware Selection and Justification")
add("Hardware was chosen to cover all three controller classes at the lowest cost while using real "
"industrial signalling. The MCU is a Waveshare ESP32-S3-Relay-6CH, selected for its on-board "
"RS-485 transceiver, six SPDT relay outputs, PSRAM, and PlatformIO support, at a board cost on the "
"order of a few hundred baht. The SBC is a Raspberry Pi 4 (4 GB), chosen for its Linux environment, "
"Docker support, and Ethernet. The PLC is a Siemens LOGO! 24CE (part 6ED1052-1CC08-0BA2), a 24 V "
"DC unit with four transistor outputs and a native Modbus TCP server, chosen for genuine "
"industrial I/O and certification. The field instruments, the XY-MD02 and the SDM230, were chosen "
"because both are inexpensive Modbus RTU slaves that nonetheless expose real measurement semantics, "
"including the IEEE-754 float pairs of the power meter.")

H2("3.3  OT Layer: Siemens LOGO! PLC and LOGO! Soft Comfort")
add("The LOGO! 24CE is programmed exclusively through LOGO! Soft Comfort, the vendor's proprietary "
"IEC 61131-3 environment, illustrating the closed-toolchain point of Section 2.4. Control logic is "
"drawn as a function block or ladder diagram and downloaded over Ethernet. A representative program "
"implements a self-latching start/stop with a runtime counter held in V-memory. The PLC's Modbus "
"TCP server is enabled in the same tool, and its discrete and analog points are mapped to Modbus "
"addresses (coils and V-memory words) so any LAN host can read or write them. The LOGO! can also "
"act as a Modbus TCP master, reading the ESP32-S3's holding registers into its own V-memory, which "
"demonstrates that once both ends share Modbus TCP the direction of data flow is a configuration "
"choice rather than an architectural one.")

H2("3.4  Edge Gateway: ESP32-S3 Modbus Firmware")
add("The firmware is an Arduino-core application built with PlatformIO. It performs three concurrent "
"roles from one cooperative, non-blocking loop that runs on a two-second cycle and never calls "
"delay(). First, a hand-rolled Modbus RTU master polls the XY-MD02 and SDM230 over RS-485, framing "
"requests with a CRC-16, recognising exception responses, and reporting a unified status code per "
"slave. Second, an MQTT publisher (the 256dpi/MQTT library) sends the readings as a JSON document "
"to the broker at QoS 1; on a device-side error the affected value fields are omitted and only the "
"status code is sent, so downstream consumers never ingest a fabricated number. Third, a Modbus "
"TCP slave (the emelianov/modbus-esp8266 library) serves the same readings on port 502 as holding "
"registers HR0-HR20: scaled integers for temperature and humidity, status and poll counters, and "
"high/low word pairs for the eight SDM230 IEEE-754 floats. The three roles, plus a watchdog, are "
"serviced cooperatively so none blocks the others. The build occupies 946 KB of 1310 KB flash "
"(72.2 percent) and 48.5 KB of 327.6 KB RAM (14.8 percent), confirming the gateway fits a "
"low-cost MCU with ample headroom.")

H2("3.5  IT Layer: Containerised MQTT and TIG Stack")
add("The Raspberry Pi hosts the data plane as Docker Compose services with pinned image tags and "
"secrets supplied through environment variables. Mosquitto 2.0 is the MQTT broker, listening on "
"port 1883 and on 9001 for WebSockets, with Docker log rotation. InfluxDB 2.7 stores telemetry in "
"the bucket sensors under the organisation weatherstation. Telegraf 1.28 bridges the two: its "
"mqtt_consumer input subscribes at QoS 1 and parses the JSON, its influxdb_v2 output writes to the "
"database, and additional inputs collect Raspberry Pi host metrics (CPU, memory, disk, "
"temperature) and network connectivity. Grafana renders dashboards for the weather, power, host, "
"and network measurements, with an anonymous viewer role for an unattended kiosk display. Because "
"every component is open-source and declared in one Compose file, the entire IT layer is "
"reproducible by a student on commodity hardware.")

H2("3.6  IoT-Sniffer Tool")
add("To make wire-level behaviour observable, a passive sniffer was developed in Python. It "
"captures traffic on a network interface with scapy's AsyncSniffer, reassembles each TCP flow, and "
"decodes frames with pure-Python parsers for Modbus TCP (recognised by port 502 and a zero "
"protocol identifier in the MBAP header) and MQTT (recognised by its control-packet structure on "
"port 1883, and over WebSockets after stripping the RFC 6455 framing). It computes live metrics, "
"including throughput and p50/p95/p99 request latency, persists frames to SQLite in write-ahead-log "
"mode, and pushes both decoded frames and a one-hertz metrics snapshot to a browser dashboard over "
"WebSocket. The tool serves two purposes: during development it verifies byte order and protocol "
"behaviour on the wire, and during the security demonstration of Chapter 4 it exposes "
"unauthenticated Modbus writes and anonymous MQTT publishes as plain, readable frames.")

section_break(); H1("Chapter 4  Evaluation and Results")
add("This chapter reports four evaluations: an empirical benchmark of open-source ESP32 Modbus "
"libraries (Study A), the resource and timing performance of the resulting production gateway, a "
"comparison of two open-source ingestion pipelines (Study B), and a live demonstration of the "
"security gaps of the platform's protocols.")

H2("4.1  Study A: Modbus Gateway Library Evaluation")
H3("4.1.1  Bench Setup and Method")
add("Ten open-source ESP32 Modbus libraries were identified. ESPHome was excluded as a "
"configuration-driven firmware generator rather than a software library, leaving nine evaluated: "
"Rob2011/ModbusMaster, vwetter, zivillian, harihanv, tobiasfaust/SolaxModbusGateway, "
"eModbus/eModbus, NamNamIoT/ModbusMaster, maxx-ukoo/esp32-modbus-tcp2rtu, espressif/esp-modbus, "
"and emelianov/modbus-esp8266. Each was built into its own PlatformIO environment on an identical "
"ESP32-S3-DevKitC-1 (N16R8) with a MAX3485 RS-485 transceiver. A host PC ran pymodbus 3.6 as a "
"simultaneous Modbus TCP client and RTU slave at 9,600 baud, 8-N-1. Round-trip latency was "
"measured for FC03 reads of 100 holding registers; flash and RAM were taken from the build; and a "
"stress suite injected bad CRCs, a 500 ms slow-slave delay, a slave-off TCP reset, and a "
"Wi-Fi drop with reconnect. The theoretical RS-485 wire-time floor for the test frame is "
"approximately 19.6 ms.")
add("Ten evaluation criteria were applied beyond raw timing: repository activity, popularity, "
"framework support, network interface, Modbus protocol features, software architecture, "
"dependencies, build system, documentation, and deployment features.")
H3("4.1.2  Results")
table("Table 4.1  FC03 round-trip latency and resource usage per Modbus library (ESP32-S3, 100 registers, 9,600 baud). Latency in ms; flash and RAM in KB.",
      ["Library", "Framework", "Mean", "p95", "Max", "Flash", "RAM", "Stress"],
      [["NamNamIoT/ModbusMaster", "Arduino", "24.5", "30.6", "30.8", "301", "22.3", "PASS"],
       ["tobiasfaust (raw RTU)", "Arduino", "27.7", "34.2", "34.2", "300", "22.0", "PASS"],
       ["vwetter (raw RTU)", "Arduino", "27.9", "34.2", "34.2", "301", "22.0", "PASS"],
       ["harihanv (raw RTU)", "Arduino", "28.0", "34.2", "34.2", "300", "22.0", "PASS"],
       ["maxx-ukoo/esp-modbus", "ESP-IDF", "27.8", "34.4", "34.5", "270", "14.4", "PASS"],
       ["espressif/esp-modbus", "ESP-IDF", "28.0", "34.1", "34.3", "270", "14.4", "PASS"],
       ["eModbus/eModbus", "Arduino", "30.3", "36.0", "36.0", "384", "22.9", "PASS"],
       ["zivillian/eModbus", "Arduino", "32.9", "36.0", "132.3", "384", "22.9", "PASS"],
       ["emelianov/modbus-esp8266", "Arduino", "33.4", "40.0", "40.0", "310", "22.2", "PASS (rec.)"]])
add("All nine libraries passed the stress suite. The fastest on mean latency is NamNamIoT "
"(24.5 ms, about 5 ms above the wire-time floor). The ESP-IDF libraries (esp-modbus, maxx-ukoo) "
"reach wire speed with the smallest RAM footprint (14.4 KB) because the IDF Modbus stack runs in "
"its own task. The asynchronous Arduino libraries (eModbus, zivillian) add roughly 2 ms per step "
"from their 2 ms FreeRTOS polling tick, and zivillian showed a single 132 ms outlier. "
"emelianov/modbus-esp8266 is the slowest on mean latency (33.4 ms) because its synchronous polling "
"loop sleeps in 2 ms ticks and adds an internal queue delay.")
H3("4.1.3  Recommendation")
add("Latency is not the deciding criterion, because every candidate is within about 14 ms of the "
"wire-time floor and far below the platform's two-second telemetry cycle. The selection therefore "
"weights maintainability, feature coverage, and robustness. emelianov/modbus-esp8266 is "
"recommended for the production gateway: it is the only evaluated library with active maintenance "
"at the evaluation date, it is one of only two (with eModbus) that simultaneously provide the "
"three roles this platform needs (RTU master, Modbus TCP slave, and multi-client TCP), and it "
"produces the smallest combined binary among the TCP-capable libraries (310 KB) while passing the "
"full stress suite. eModbus/eModbus is the recommended alternative for FreeRTOS-task designs or "
"more than five concurrent TCP clients, and Rob2011/ModbusMaster remains the right choice for "
"RTU-only, single-master applications with no TCP requirement.")

H2("4.2  Gateway Performance Measurement")
add("The benchmark above measures each library in isolation. The production gateway firmware does "
"more: it runs the chosen emelianov library as a Modbus TCP slave, a hand-rolled RTU master "
"polling two sensors, an MQTT publisher, and a watchdog, all from one cooperative loop. Built that "
"way, the firmware occupies 946 KB of 1,310 KB flash (72.2 percent) and 48.5 KB of 327.6 KB RAM "
"(14.8 percent), confirming that a complete dual-protocol gateway fits a low-cost MCU with "
"substantial headroom. End to end, an RTU sensor poll, register update, MQTT publish, and TCP "
"slave service complete well inside the two-second cycle, and the cooperative design keeps any one "
"role from blocking the others. The gateway therefore meets its functional goal — bridging legacy "
"serial OT to both an IT dashboard (via MQTT) and IP control hosts (via Modbus TCP) — within the "
"resource budget of a single inexpensive board.")

H2("4.3  Study B: Node-RED versus Telegraf Ingestion")
add("Both Telegraf and Node-RED can subscribe to MQTT and write to InfluxDB, yet they occupy "
"different architectural roles. Telegraf is a compiled Go agent configured by a single file and "
"run as a set-and-forget service; it has very low memory overhead, sustains thousands of metrics "
"per second, and buffers internally so it tolerates brief database outages. Node-RED is a "
"Node.js, browser-based flow editor in which logic is wired visually; it is unmatched for rapid "
"prototyping, conditional routing, and complex per-message transforms, but carries the heavier "
"footprint of a Node.js runtime.")
table("Table 4.2  Telegraf versus Node-RED feature comparison.",
      ["Feature", "Telegraf", "Node-RED"],
      [["Interface", "CLI / configuration file", "Browser-based visual editor"],
       ["Logic", "Fixed: collect, process, write", "Freeform: conditional, branching flows"],
       ["Customisation", "Go plugins (recompile)", "Drag-in nodes / inline functions"],
       ["Deployment", "Single binary, trivial to scale", "Requires Node.js runtime"],
       ["Best fit", "High-rate pass-through, host metrics", "Prototyping, complex transforms"]])
add("The two are complementary rather than interchangeable. In this platform Telegraf does the "
"heavy lifting — ingesting telemetry and Raspberry Pi host metrics into InfluxDB as a reliable "
"service — while Node-RED is the better tool when a flow needs visual debugging or a non-trivial "
"transformation. The platform standardises on Telegraf for production ingestion and treats "
"Node-RED as a complementary prototyping and integration tool.")

H2("4.4  Security Demonstration")
add("The demonstration shows that the platform's field protocols carry no credentials, using the "
"sniffer of Section 3.6 to make the exposure visible. Modbus TCP authenticates nothing: a single "
"command from an ordinary LAN-connected laptop forces a coil write and actuates a physical output "
"on the PLC.")
code("mbpoll -a 1 -t 0 -r 0 -1 192.168.1.100 1   # FC05 Write Single Coil")
add("The sniffer captures the request as a plaintext twelve-byte frame on the wire, with no "
"authentication field present anywhere in the exchange. The MQTT layer is equally open: with "
"anonymous access enabled, any host on the network can publish forged telemetry to the sensor "
"topic, which then appears as a genuine reading in Grafana.")
code("mosquitto_pub -h 192.168.1.50 -t sensors/esp32/data -m '{\"temperature\":99.9}'")
add("These two actions, captured live, demonstrate concretely what the literature asserts: on a "
"flat network, unauthenticated Modbus and anonymous MQTT let any IT host read and command OT "
"equipment. Mitigations follow directly and are discussed as future work: enabling MQTT "
"authentication and TLS, restricting Modbus TCP by firewall, and segregating the OT and IT zones "
"by VLAN so the Purdue separation is enforced rather than assumed.")

section_break(); H1("Chapter 5  Discussion and Conclusion")
add("This chapter interprets the results, draws out the platform's educational value, and "
"concludes against the five objectives before proposing future work.")

H2("5.1  MCU versus SBC versus PLC: Roles and Fit")
add("The central design claim is that the three controller classes are complementary layers rather "
"than competing alternatives, and the evaluation supports it. Each device is optimal at a "
"different Purdue level for reasons that are structural, not incidental.")
table("Table 5.1  Comparison of the three controller classes used in the platform.",
      ["Attribute", "MCU — ESP32-S3", "SBC — Raspberry Pi 4", "PLC — LOGO! 24CE"],
      [["Purdue level", "L2 — edge / gateway", "L3 — site operations", "L1 — basic control"],
       ["Operating system", "None (cooperative loop)", "Full Linux", "Proprietary firmware"],
       ["Determinism", "Soft real-time", "Non-deterministic", "Hard real-time"],
       ["Native I/O", "GPIO/ADC/UART/RS-485", "GPIO + USB; no analog", "24 V DI, 0-10 V AI, relays"],
       ["Networking", "Wi-Fi / BLE", "Gigabit Ethernet", "10/100 Modbus TCP"],
       ["Power draw", "~0.6-1.7 W", "~3.4-7.6 W", "<=4.5 W at 24 V DC"],
       ["Toolchain", "Open (Arduino/PlatformIO)", "Open (Linux/Docker)", "Proprietary (Soft Comfort)"],
       ["Certification", "None", "None", "CE, UL, FM, ATEX"],
       ["Approx. unit cost", "~USD 15-30", "~USD 55", "~USD 150-300"]])
add("The MCU delivers the lowest cost-per-channel and lowest power and is the correct field-edge "
"gateway, but it lacks an operating system and certification. The SBC offers unmatched software "
"richness — any Linux package or container runs unmodified — but its preemptive scheduler cannot "
"guarantee hard real-time behaviour, so it belongs in the data plane, not in control. The PLC is "
"the only device that drives mains-level actuators under a bounded, certified scan cycle, which is "
"a safety property rather than a mere performance figure, but it is the most expensive and the "
"most closed. Substituting one class for another across layers trades exactly these properties. "
"The Purdue assignment is therefore an engineering consequence, not a preference.")

H2("5.2  Open-Source versus Proprietary Toolchains as a Teaching Point")
add("The platform also makes the openness of the software stack tangible. The MCU and SBC are "
"built entirely from well-known open-source software — the Arduino core and PlatformIO, Linux and "
"Docker, the TIG stack, Node-RED, and Mosquitto — all inspectable, scriptable, free to reproduce, "
"and community-supported. The PLC, by contrast, can be programmed only through Siemens' "
"proprietary LOGO! Soft Comfort. A student using the platform experiences this divide directly: "
"the open layers can be version-controlled, diffed, and rebuilt from a single command, whereas the "
"PLC logic lives in a licensed desktop tool and a vendor binary. The lesson — that openness buys "
"reproducibility and inspectability while proprietary tooling buys certification and support, at "
"the price of vendor lock-in — is one the platform teaches by example rather than by assertion.")

H2("5.3  The Platform as an Educational Tool")
add("Taken together, the platform exposes the full learning surface of IT/OT integration on one "
"low-cost bench. A learner can poll a real Modbus RTU sensor, watch a microcontroller bridge it to "
"both an IT dashboard and an IP control host, drive a certified industrial output from a PLC, "
"inspect every frame on the wire, and witness the security consequences of leaving those frames "
"unauthenticated. Because the entire IT and edge stack is open-source and declared as code, the "
"platform is fully reproducible by another student on commodity hardware, which is itself a "
"pedagogical asset. The empirical artefacts — the library benchmark and the device comparison — "
"give the learner evidence-based guidance rather than folklore.")

H2("5.4  Conclusion")
add("This work designed, built, and evaluated a low-cost educational Industrial IoT platform that "
"integrates the three controller classes of modern automation. Against the six objectives: the "
"platform integrates an ESP32-S3 microcontroller, a Raspberry Pi 4 single-board computer, and a "
"Siemens LOGO! 24CE PLC across Purdue Levels 1 to 3 on a single network. A survey of related work "
"identified the open-source software most commonly adopted in IIoT applications — the MQTT broker, "
"Node-RED, and the TIG stack — and these were adopted as the platform's edge and IT layers. A "
"Modbus RTU-to-TCP/MQTT "
"gateway was implemented on the microcontroller, and a benchmark of nine open-source ESP32 Modbus "
"libraries selected emelianov/modbus-esp8266 on the strength of its maintenance, feature coverage, "
"footprint, and robustness. The production gateway runs within 72.2 percent flash and 14.8 percent "
"RAM on a single inexpensive board. Two open-source ingestion pipelines were compared and found "
"complementary, with Telegraf chosen for production. A purpose-built sniffer decoded Modbus TCP "
"and MQTT and demonstrated, on live traffic, that both protocols expose OT equipment to any IT "
"host on a flat network. The platform thus turns the abstract goal of IT/OT convergence into a "
"concrete, reproducible, and instructive system.")

H2("5.5  Future Work")
add("Several extensions would broaden the platform. On security, MQTT authentication and TLS, "
"firewalling of Modbus TCP, and VLAN segregation of the OT and IT zones would convert the "
"demonstrated weaknesses into enforced controls. On the gateway, a telemetry ring buffer would "
"allow replay across Wi-Fi outages, and an over-the-air update mechanism would ease maintenance. "
"On the IT layer, scheduled InfluxDB backups, container health checks, and Grafana threshold "
"alerting would harden the data plane. Finally, adding OPC-UA as a more secure OT protocol and "
"validating the platform with students in a laboratory course would extend both its technical and "
"its educational reach.")

# References / Biography / Appendices
section_break(); add("References", "Heading 0")
for ref in [
 '[1]  M. Endres, A. Fettweis, et al., "IT/OT convergence in Industry 4.0," IEEE Ind. Electron. Mag., vol. 13, no. 2, pp. 22-33, 2019.',
 '[2]  L. D. Xu, E. L. Xu, and L. Li, "Industry 4.0: state of the art and future trends," Int. J. Prod. Res., vol. 56, no. 8, pp. 2941-2962, 2018.',
 '[3]  Enterprise-Control System Integration - Part 1: Models and Terminology, ISA-95.00.01, 2010.',
 '[4]  Modbus Organization, Modbus Application Protocol Specification V1.1b3, 2012.',
 '[5]  Information technology - Message Queuing Telemetry Transport (MQTT) v3.1.1, ISO/IEC 20922, 2016.',
 '[6]  InfluxData, "Telegraf: the open-source server agent," documentation, 2024.',
 '[7]  InfluxData, "InfluxDB 2.x time-series database," documentation, 2024.',
 '[8]  Grafana Labs, "Grafana: operational dashboards," documentation, 2024.',
 '[9]  T. Morris and W. Gao, "Industrial control system cyber attacks and the Modbus protocol," in Proc. Int. Symp. ICS & SCADA Cyber Security, 2013, pp. 22-29.',
]:
    add(ref, "Bibliography")

add("Author Biography", "Heading 0")
add("Mr. Patthanan Bhandhumanee, King Mongkut’s University of Technology North Bangkok, "
"Department of Electrical and Computer Engineering. [birthdate, hometown, education, contact]", "Biography")

for a, t in [("A", "ESP32-S3 Firmware Listings"),
             ("B", "Docker Compose and Telegraf Configuration"),
             ("C", "Modbus Library Evaluation Scorecard"),
             ("D", "IoT-Sniffer Sample Captures"),
             ("E", "Hardware Reference"),
             ("F", "IIoT Platform Comparison Matrix")]:
    add(f"Appendix {a}  {t}", "Heading 0"); stub()

# ---------- Thai font enforcement + save ----------
# ---------- ALL-ENGLISH front matter: delete the duplicate Thai blocks ----------
# The KMUTNB template ships a Thai twin of the cover/approval/abstract; the English
# twins remain. Delete whole Thai blocks (not text-only) so no orphan lines survive.
from docx.shared import Pt

def del_range(start_sub, end_sub):
    ps = doc.paragraphs
    si = next((i for i, p in enumerate(ps) if start_sub in p.text), None)
    ei = next((i for i, p in enumerate(ps) if end_sub in p.text), None)
    if si is None or ei is None or ei <= si:
        return
    for p in ps[si:ei]:
        p._p.getparent().remove(p._p)

# 1) delete the whole Thai cover section (section 1): start .. first section-break para
ps = doc.paragraphs
fb = next((i for i, p in enumerate(ps)
           if p._p.find(qn('w:pPr')) is not None
           and p._p.find(qn('w:pPr')).find(qn('w:sectPr')) is not None), None)
if fb is not None:
    for p in ps[:fb + 1]:
        p._p.getparent().remove(p._p)

# 2) delete the Thai approval and Thai abstract blocks (English twins remain)
del_range('ใบรับรองปริญญานิพนธ์', 'Approval Project Certificate')
del_range('บทคัดย่อ', 'Abstract')

# 3) rename the Thai-only structural headings to English
RENAME = {
    'กิตติกรรมประกาศ': 'Acknowledgements',
    'สารบัญ': 'Table of Contents',
    'สารบัญ (ต่อ)': 'Table of Contents (continued)',
    'สารบัญภาพ': 'List of Figures',
    'สารบัญตาราง': 'List of Tables',
    'ศัพท์เฉพาะ': 'Nomenclature',
}
for p in doc.paragraphs:
    k = p.text.strip()
    if k in RENAME:
        set_text(p, RENAME[k])

# 4) remove the broken template TOC field + duplicate "(continued)" headings
for p in list(doc.paragraphs):
    sn = p.style.name.lower()
    if sn.startswith('toc') or 'bookmark not defined' in p.text.lower() \
       or p.text.strip() == 'Table of Contents (continued)':
        p._p.getparent().remove(p._p)

# 5) strip auto-numbering from heading styles (chapters/sections numbered manually;
#    Heading 1's list numbering otherwise prints a Thai "บทที่ N" prefix)
for sn in ('Heading 1', 'Heading 2', 'Heading 3', 'Heading 4'):
    spr = doc.styles[sn].element.find(qn('w:pPr'))
    if spr is not None:
        npr = spr.find(qn('w:numPr'))
        if npr is not None:
            spr.remove(npr)

# 6) fixed table layout with explicit per-cell widths so numbers stop wrapping
from docx.shared import Inches
from docx.oxml import OxmlElement
def _fix_table(t):
    t.autofit = False
    ncol = len(t.columns)
    # totals kept <= 5.75 in (page text width is 5.77 in); else Word scales + wraps
    if ncol >= 8:        # Table 4.1: Library, Framework, 5 numerics, Stress (inches)
        win = [1.40, 0.75, 0.55, 0.55, 0.55, 0.55, 0.55, 0.75]
    elif ncol == 4:      # Table 5.1 comparison
        win = [1.40, 1.45, 1.45, 1.45]
    elif ncol == 3:      # Table 4.2 Telegraf vs Node-RED
        win = [1.30, 2.20, 2.20]
    else:
        win = [5.7 / ncol] * ncol
    # (a) the w:tblGrid gridCol widths drive fixed-layout column sizing
    grid = t._tbl.find(qn('w:tblGrid'))
    if grid is not None:
        for gc, w in zip(grid.findall(qn('w:gridCol')), win):
            gc.set(qn('w:w'), str(int(w * 1440)))
    # (b) per-cell tcW must agree
    for row in t.rows:
        for j, c in enumerate(row.cells):
            if j < len(win):
                c.width = Inches(win[j])
    # (c) fixed layout via python-docx (writes w:tblLayout in the correct schema slot)
    t.autofit = False
    t.allow_autofit = False
    # (d) the existing w:tblW defaults to type="auto" w="0"; under fixed layout that
    #     leaves the table no total width to fill, so columns collapse. Set a real dxa.
    tblPr = t._tbl.tblPr
    tblW = tblPr.find(qn('w:tblW'))
    if tblW is not None:
        tblW.set(qn('w:type'), 'dxa')
        tblW.set(qn('w:w'), str(int(sum(win) * 1440)))
    # (e) shrink cell insets — large default margins were collapsing the usable cell width
    old_cm = tblPr.find(qn('w:tblCellMar'))
    if old_cm is not None:
        tblPr.remove(old_cm)
    cm = OxmlElement('w:tblCellMar')
    for side, w in (('top', '0'), ('left', '40'), ('bottom', '0'), ('right', '40')):
        e = OxmlElement('w:' + side); e.set(qn('w:w'), w); e.set(qn('w:type'), 'dxa')
        cm.append(e)
    look = tblPr.find(qn('w:tblLook'))
    (look.addprevious(cm) if look is not None else tblPr.append(cm))
    fs = Pt(9) if ncol >= 8 else (Pt(11) if ncol >= 6 else Pt(12))
    for row in t.rows:
        for c in row.cells:
            for par in c.paragraphs:
                for r in par.runs:
                    r.font.size = fs
for t in doc.tables:
    _fix_table(t)

# 7) safety net: remove any remaining Thai-text stragglers (ack body, "หน้า", etc.)
import re as _re
_THAI = _re.compile(r'[฀-๿]')
for p in list(doc.paragraphs):
    if _THAI.search(p.text):
        pPr = p._p.find(qn('w:pPr'))
        if pPr is not None and pPr.find(qn('w:sectPr')) is not None:
            set_text(p, "")
        else:
            p._p.getparent().remove(p._p)

enforce_thai(doc, thai_font="Angsana New", latin_font="Angsana New")
doc.save(OUT)
print("SAVED:", OUT)
print("paras now:", len(doc.paragraphs))
