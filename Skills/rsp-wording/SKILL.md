---
name: "rsp-wording"
description: "Write Thai technical/engineering content in the voice and terminology of the KMUTNB IoT Engineering Education blog (iot-kmutnb.github.io/blogs, author RSP). Use when the user asks to write, translate, or edit Thai material about IoT, microcontrollers (ESP32/Arduino/STM32/RP2040), Raspberry Pi / SBCs, Modbus, RS-485, MQTT, sensors, power meters, electronics, RTOS, or FPGA — or explicitly asks for 'RSP wording', 'KMUTNB IoT blog style', or 'his voice'."
---

# RSP Wording — KMUTNB IoT Engineering Education style

Write Thai engineering prose the way the KMUTNB "IoT Engineering Education" blog does
(`https://iot-kmutnb.github.io/blogs/`, author byline **RSP**). The goal is Thai that reads
like RSP wrote it: clear, instructional, and consistent in its bilingual terminology.

Load `reference/glossary.md` for the term table and `reference/style-guide.md` for detailed
rules and worked before/after examples. The essentials are below.

## Core conventions (apply every time)

1. **Thai narrative, English term in parentheses on first mention.** Introduce each technical
   concept in Thai, then gloss the English (often bold) in parentheses:
   *"ไมโครคอนโทรลเลอร์ (Microcontroller: MCU)"*, *"รหัสคำสั่ง (Function Code)"*,
   *"การสื่อสารแบบดิฟเฟอเรนเชียล (Differential Signaling)"*. After first mention you may use the
   Thai or the English term alone.

2. **Keep product names, part numbers, pins, registers, code, and units in English/ASCII:**
   ESP32-S3, Raspberry Pi 4, SDM120, XY-MD02, MAX485, `FC=0x04`, `GPIO21`, `0x0000`, 9600 บอด,
   120 Ω, 240 MHz, IEEE 802.11 b/g/n. Never transliterate these.

3. **Phoneticise spoken acronyms and expand them once:**
   *"MQTT (เอ็ม-คิว-ที-ที) ย่อมาจาก MQ Telemetry Transport"*. Do the expansion on first use.

4. **Gloss roles with alternatives RSP uses:** *"โบรกเกอร์ (broker หรือ ตัวกลาง)"*,
   *"ไคลเอนต์ (client)"*, *"ผู้เผยแพร่ข้อความ (publisher)"*, *"ผู้สมัครรับข้อความ (subscriber)"*.

5. **Instructional but precise tone.** Sentences are explanatory and often step-by-step
   ("เริ่มต้นด้วย…", "จากนั้น…", "ในกรณีนี้…", "ข้อสังเกต:…", "โดยทั่วไป…"). Sections often close
   with a **"กล่าวสรุป"** paragraph. This teaching register suits background/tutorial material.

6. **Structure like the blog:** short Thai lead-in → bullet lists for specs/pins/registers →
   figures captioned *"รูป: …"* → tables → a brief summary. Use bullet lists for hardware
   specs and register maps.

## Register guidance (important for theses/reports)

RSP's voice is a **teaching/tutorial** voice. It fits **background and how-to** sections
perfectly. For a formal thesis or paper, apply the **terminology and glossing conventions
everywhere**, but keep an **academic register** (no second-person "ลองทำดู…") in original
results, analysis, and discussion so the document stays formal. When in doubt, keep the terms,
soften the tutorial tone.

## Preferred terminology (quick list — full table in reference/glossary.md)

- master/slave → **มาสเตอร์ (master)** / **สเลฟ (slave)**; slave id → **หมายเลขอุปกรณ์สเลฟ (slave address)**
- function code → **รหัสคำสั่ง (Function Code, FC)**; registers keep English: input/holding registers
- CRC → **การตรวจสอบความถูกต้องแบบ 16-bit CRC**; endianness → **big-endian** (kept in English)
- publish/subscribe → **เผยแพร่ / สมัครรับข้อความ** (NOT "สมัครสมาชิก"); topic → **หัวข้อ (topic)**
- retained message → **ข้อความที่เก็บรักษาไว้ (retained message)**; last will → **การส่งครั้งสุดท้าย (last will)**
- edge gateway → **เอดจ์เกตเวย์ (edge gateway)**; broker → **โบรกเกอร์ (ตัวกลาง)**
- microcontroller → **ไมโครคอนโทรลเลอร์ (Microcontroller: MCU)**; SBC → **คอมพิวเตอร์บอร์ดเดี่ยว (Single-Board Computer: SBC)**
- embedded systems → **ระบบสมองกลฝังตัว (Embedded Systems)**; multi-core → **หลายแกน (Multi-Core)**
- RTOS → **ระบบปฏิบัติการเวลาจริง (RTOS)**; multi-threading → **การเขียนโปรแกรมแบบมัลติเธรด (Multi-Threading)**
- power meter → **เพาเวอร์มิเตอร์ไฟฟ้า…**; real/apparent/reactive power → **กำลังไฟฟ้าที่ใช้งานจริง (Real Power)** / **…ที่ปรากฏ (Apparent Power)** / **…รีแอคทีฟ (Reactive Power)**; power factor → **ค่าตัวประกอบกำลังไฟฟ้า (Power Factor)**
- DIN rail → **รางปีกนก (DIN Rail)**; transceiver → **ตัวรับส่งสัญญาณ (Transceiver)**; differential signaling → **การสื่อสารแบบดิฟเฟอเรนเชียล (Differential Signaling)**
- oscilloscope → **ออสซิลโลสโคป (Oscilloscope)**; breadboard → **เบรดบอร์ด / แผงต่อวงจร**; firmware → **เฟิร์มแวร์**

## Workflow

1. Draft the Thai content following the conventions above.
2. Check every technical term against `reference/glossary.md`; fix any that drift (especially
   "สมัครสมาชิก" → "สมัครรับข้อความ", missing English glosses, or transliterated part numbers).
3. If the target is a formal document, verify the register (terms kept, tutorial tone removed
   from original analysis).
4. Offer a short before/after diff of any terms you changed so the user can confirm.

Attribution note: the blog is licensed CC BY-SA 4.0. This skill captures **wording/terminology
conventions**, not verbatim text — write original Thai, don't copy passages.
