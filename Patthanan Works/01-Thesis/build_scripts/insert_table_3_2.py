#!/usr/bin/env python3
"""Insert Table 3.2 (hardware inventory + Thai retail cost) into the combined thesis.
Replaces the placeholder paragraph '[Table 3.2 - Hardware inventory ...]'.
Matches existing table styling: Table Grid, bold header row, caption as Normal paragraph above.
"""
from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
import copy

DOC = 'senior_project_report.docx'

CAPTION = ('Table 3.2  Hardware inventory and approximate Thai retail cost '
           '(indicative, June 2026).')

HEADERS = ['Device', 'Function / Purdue level', 'Key specifications', 'Qty', 'Unit price (THB)']

ROWS = [
    ['Siemens LOGO! 8.4 (6ED1052-1MD08-0BA2)',
     'OT controller / micro-PLC (L1)',
     '8 DI (4 as 0-10 V AI), 4x relay DO 10 A, RJ-45 Ethernet, native Modbus TCP server, IEC 61131-3 (LAD/FBD)',
     '1', '3,200'],
    ['Waveshare ESP32-S3-Relay-6CH',
     'Edge gateway: Modbus master + MQTT publisher (L2)',
     'ESP32-S3 dual-core 240 MHz, 8 MB flash + 2 MB PSRAM, 6x SPDT relay 10 A, isolated RS-485, Wi-Fi/BLE',
     '1', '1,200'],
    ['Raspberry Pi 4 Model B (4 GB)',
     'IT host: TIG stack in Docker (L3)',
     'BCM2711 quad Cortex-A72 1.5 GHz, 4 GB LPDDR4, Gigabit Ethernet, 2x USB 3.0',
     '1', '1,850'],
    ['Raspberry Pi 7" Touchscreen (DSI)',
     'HMI / Grafana kiosk',
     '800x480 px, 10-point capacitive touch, DSI ribbon, GPIO-powered',
     '1', '2,490'],
    ['XY-MD02 (SHT20) transmitter',
     'Field sensor (RS-485)',
     '-40 to 80 C +/-0.3 C, 0-100 %RH +/-3 %, Modbus RTU, 10-30 VDC',
     '1', '300'],
    ['Eastron SDM230-Modbus power meter',
     'Field instrument (RS-485)',
     '230 V single-phase, 45 A direct, Class 1, RS-485 Modbus RTU + pulse output, DIN-rail',
     '1', '1,300'],
    ['Mean Well MDR-20-24 PSU',
     '24 VDC DIN-rail power supply',
     '85-264 VAC in; 24 V / 1 A / 24 W out; OVP/OLP/SCP protection',
     '1', '550'],
    ['Miniature circuit breaker (1P)',
     'Mains-side protection',
     'Single-pole MCB, DIN-rail mount (EN 60715)',
     '1', '120'],
    ['microSD card 32 GB Class 10',
     'Raspberry Pi OS storage',
     'ext4, Raspberry Pi OS Lite 64-bit (Bookworm)',
     '1', '200'],
    ['DIN rail, RS-485/Ethernet cabling, terminals',
     'Interconnect & mounting',
     '35 mm DIN rail, twisted-pair RS-485, Cat-5e patch leads, screw terminals',
     '1 lot', '300'],
    ['ESP32-C6-DevKitC-1',
     'Study A benchmark fixture (Modbus slave)',
     'RISC-V single-core 160 MHz, Wi-Fi 6 / BLE / Zigbee, 8 MB flash',
     '1', '350'],
]

TOTAL = '11,860'

NOTE = ('Note: Prices are indicative single-unit Thai retail figures (June 2026) from local '
        'distributors (e.g. IBCON, Cytron Thailand, ArtronShop, Eastron dealers); imported '
        'modules are converted at approximately 36 THB/USD and include VAT where listed. '
        'The total excludes the development PC and standard hand tools.')


def set_cell(cell, text, bold=False, align=None):
    cell.text = ''
    p = cell.paragraphs[0]
    if align is not None:
        p.alignment = align
    r = p.add_run(text)
    r.bold = bold


def main():
    doc = Document(DOC)

    # locate placeholder paragraph
    anchor = None
    for p in doc.paragraphs:
        if p.text.strip().startswith('[Table 3.2'):
            anchor = p
            break
    if anchor is None:
        raise SystemExit('placeholder for Table 3.2 not found')

    anchor_el = anchor._p

    # caption paragraph (Normal), inserted before placeholder
    cap = doc.add_paragraph(CAPTION)  # appended at end; move next
    cap_el = cap._p
    cap_el.getparent().remove(cap_el)
    anchor_el.addprevious(cap_el)

    # build table at end, then move
    ncols = len(HEADERS)
    table = doc.add_table(rows=1 + len(ROWS) + 1, cols=ncols)
    table.style = 'Table Grid'
    table.alignment = WD_TABLE_ALIGNMENT.CENTER

    # header
    for ci, h in enumerate(HEADERS):
        al = WD_ALIGN_PARAGRAPH.CENTER if ci >= 3 else None
        set_cell(table.rows[0].cells[ci], h, bold=True, align=al)

    # body
    for ri, row in enumerate(ROWS, start=1):
        for ci, val in enumerate(row):
            al = WD_ALIGN_PARAGRAPH.CENTER if ci == 3 else (
                WD_ALIGN_PARAGRAPH.RIGHT if ci == 4 else None)
            set_cell(table.rows[ri].cells[ci], val, align=al)

    # total row: merge first 3 cells for label
    trow = table.rows[-1]
    merged = trow.cells[0].merge(trow.cells[1]).merge(trow.cells[2])
    set_cell(merged, 'Total (approx.)', bold=True, align=WD_ALIGN_PARAGRAPH.RIGHT)
    set_cell(trow.cells[3], '', align=WD_ALIGN_PARAGRAPH.CENTER)
    set_cell(trow.cells[4], TOTAL, bold=True, align=WD_ALIGN_PARAGRAPH.RIGHT)

    tbl_el = table._tbl
    tbl_el.getparent().remove(tbl_el)
    anchor_el.addprevious(tbl_el)

    # note paragraph after table, before (replacing) placeholder
    note = doc.add_paragraph()
    nr = note.add_run(NOTE)
    nr.italic = True
    note_el = note._p
    note_el.getparent().remove(note_el)
    anchor_el.addprevious(note_el)

    # remove placeholder
    anchor_el.getparent().remove(anchor_el)

    doc.save(DOC)
    print('Inserted Table 3.2 with', len(ROWS), 'items. Tables now:', len(doc.tables))


if __name__ == '__main__':
    main()
