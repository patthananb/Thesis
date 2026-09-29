# RSP Style Guide — detail & worked examples

RSP = author byline on the KMUTNB "IoT Engineering Education" blog
(`https://iot-kmutnb.github.io/blogs/`). These are the recurring habits, with before/after
examples so a draft can be checked against them.

## Sentence-level habits

- **Open a topic in Thai, then gloss the English term (bold) in parentheses.** The English is
  the anchor for the reader who has seen it in datasheets.
- **Chain explanatory connectors:** "เริ่มต้นด้วย…", "จากนั้น…", "ในกรณีนี้…", "โดยทั่วไป…",
  "นอกจากนี้…", "ทั้งนี้…". Sentences build the idea step by step.
- **Call out caveats inline** with **"ข้อสังเกต:"** or **"หมายเหตุ:"**.
- **Give concrete numbers and units** (240 MHz, 9600 บอด, 120 Ω, 1200 เมตร, ±200 mV, 1~247).
- **Close a section** with a short **"กล่าวสรุป"** paragraph that restates what was shown.

## Formatting habits

- Section headers are short Thai noun phrases (the blog prefixes them "▷ ").
- **Bullet lists** for: hardware specs, IC pinouts, register maps, port lists, option sets.
- Figures are referenced as **"รูป: <caption> (Source: …)"**.
- Tables for packet types, register addresses, pin functions.
- Code blocks kept verbatim in English with real pin/register names.
- Keep part numbers, pins, registers, hex, and units ASCII — never transliterate.

## Worked before/after (thesis register: keep terms, formal tone)

**MQTT — before (generic thesis Thai):**
> MQTT เป็นโพรโทคอลแบบเผยแพร่-สมัครสมาชิก ไคลเอนต์เผยแพร่ข้อความไปยังหัวข้อบนโบรกเกอร์
> และโบรกเกอร์ส่งต่อไปยังผู้สมัครสมาชิกทุกราย … คุณลักษณะอย่างข้อความค้างและพินัยกรรมสุดท้าย …

**MQTT — after (RSP wording):**
> MQTT (เอ็ม-คิว-ที-ที) ย่อมาจาก MQ Telemetry Transport เป็นโพรโทคอลสำหรับการส่งข้อความ
> (messaging protocol) ที่มีน้ำหนักเบา … สถาปัตยกรรมเป็นไปตามรูปแบบผู้เผยแพร่-ผู้สมัครรับข้อความ
> (publisher–subscriber pattern) ประกอบด้วยโบรกเกอร์ (broker หรือ ตัวกลาง) และไคลเอนต์ (client)
> ไคลเอนต์ที่เป็นผู้เผยแพร่ข้อความ (publisher) ส่งข้อความไปยังหัวข้อ (topic) บนโบรกเกอร์ …
> คุณลักษณะข้อความที่เก็บรักษาไว้ (retained message) และการส่งข้อความครั้งสุดท้าย (last will) …

Changes: expand + phoneticise the acronym; "สมัครสมาชิก" → "สมัครรับข้อความ"; gloss publisher/
subscriber/broker/topic in English; "ข้อความค้าง" → "ข้อความที่เก็บรักษาไว้ (retained message)";
"พินัยกรรมสุดท้าย" → "การส่งข้อความครั้งสุดท้าย (last will)".

**Power meter — before:**
> มิเตอร์พลังงานไฟฟ้าเฟสเดียว … วัดแรงดันไฟ กระแสไฟ กำลังไฟฟ้าจริง/ปรากฏ/รีแอกทีฟ … ติดตั้งบนราง DIN

**Power meter — after:**
> เพาเวอร์มิเตอร์ไฟฟ้าดิจิทัลแบบเฟสเดียว (Single-Phase Digital Power Meter) … วัดแรงดันไฟฟ้า
> กระแสไฟฟ้า กำลังไฟฟ้าที่ใช้งานจริง (Real Power) กำลังไฟฟ้าที่ปรากฏ (Apparent Power)
> กำลังไฟฟ้ารีแอคทีฟ (Reactive Power) ค่าตัวประกอบกำลังไฟฟ้า (Power Factor) … ติดตั้งบนรางปีกนก (DIN Rail)

## Checklist before delivering

- [ ] Every acronym expanded + phoneticised on first mention.
- [ ] Every technical concept has an English gloss on first mention.
- [ ] "สมัครสมาชิก" replaced by "สมัครรับข้อความ" wherever it means MQTT subscribe.
- [ ] Part numbers / pins / registers / units left in English.
- [ ] Formal document: tutorial second-person tone removed from original analysis.
- [ ] Section ends with a brief summary if it is a background/how-to section.
