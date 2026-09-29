#!/usr/bin/env python3
"""Insert Table 4.3 (MCU vs SBC vs PLC comparison) replacing the placeholder."""
from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.shared import Cm

DOC = 'senior_project_report.docx'

CAPTION = ('Table 4.3  Comparison of the three device classes used in this project: '
           'MCU (ESP32-S3), SBC (Raspberry Pi 4), and PLC (Siemens LOGO! 8.4).')

HEADERS = ['Attribute', 'MCU — ESP32-S3', 'SBC — Raspberry Pi 4', 'PLC — Siemens LOGO! 8.4']

ROWS = [
    ['Purdue level',
     'L2 — supervisory / edge',
     'L3 — site operations',
     'L1 — basic control'],
    ['Role in project',
     'Modbus RTU/TCP master + MQTT edge gateway',
     'TIG stack host: broker, time-series DB, dashboards',
     'Deterministic control of field actuators (ladder logic)'],
    ['Operating system',
     'None — bare-metal cooperative loop (Arduino/FreeRTOS)',
     'Full Linux (Raspberry Pi OS, Debian Bookworm)',
     'Proprietary firmware, IEC 61131-3 runtime'],
    ['Determinism',
     'Soft real-time; cooperative, no preemption',
     'Non-deterministic; preemptive Linux, no hard RT guarantee',
     'Hard real-time; bounded cyclic scan'],
    ['Processing / memory',
     'Xtensa LX7 dual-core 240 MHz; 512 KB SRAM + 2 MB PSRAM',
     'Quad Cortex-A72 1.5 GHz; 4 GB LPDDR4',
     'Micro-PLC; 400 function blocks, 4 KB V-memory'],
    ['Native I/O',
     'GPIO/ADC/UART/SPI/I2C, 6x relay, RS-485 (3.3 V logic)',
     'GPIO header + USB; no native industrial I/O',
     '24 VDC DI, 0-10 V AI, relay DO 10 A (industrial levels)'],
    ['Networking',
     'Wi-Fi / BLE + isolated RS-485',
     'Gigabit Ethernet + dual-band Wi-Fi',
     '10/100 Ethernet (Modbus TCP server, <=8 connections)'],
    ['Power draw',
     '~0.6-1.7 W (idle-active)',
     '~3.4-7.6 W (idle-load)',
     '<=4.5 W at 24 VDC'],
    ['Programming',
     'C/C++ (Arduino core on PlatformIO)',
     'Any Linux language; Docker Compose',
     'LAD / FBD via LOGO! Soft Comfort (proprietary)'],
    ['Manageability',
     'No OS/SSH; firmware reflash to update',
     'Full SSH, package manager, containers',
     'Offline programming via vendor tool only'],
    ['Certification',
     'None (development module)',
     'None (consumer SBC)',
     'CE, UL, cUL, FM, ATEX Zone 2'],
    ['Approx. unit cost',
     '~USD 15-30 (THB 1,200)',
     '~USD 55 (THB 1,850)',
     '~USD 150-300 (THB 3,200)'],
    ['Best-fit use',
     'Field-edge I/O, low cost/power, protocol bridging',
     'Site data plane: brokering, storage, dashboards, analytics',
     'Mains-level / safety-critical certified actuation'],
]

COL_W = [Cm(3.2), Cm(4.2), Cm(4.2), Cm(4.2)]


def set_cell(cell, text, bold=False):
    cell.text = ''
    r = cell.paragraphs[0].add_run(text)
    r.bold = bold


def main():
    doc = Document(DOC)

    anchor = None
    for p in doc.paragraphs:
        if p.text.strip().startswith('[Table 4.3'):
            anchor = p
            break
    if anchor is None:
        raise SystemExit('placeholder for Table 4.3 not found')
    anchor_el = anchor._p

    cap = doc.add_paragraph(CAPTION)
    cap_el = cap._p
    cap_el.getparent().remove(cap_el)
    anchor_el.addprevious(cap_el)

    table = doc.add_table(rows=1 + len(ROWS), cols=len(HEADERS))
    table.style = 'Table Grid'
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False

    for ci, h in enumerate(HEADERS):
        set_cell(table.rows[0].cells[ci], h, bold=True)
    for ri, row in enumerate(ROWS, start=1):
        for ci, val in enumerate(row):
            set_cell(table.rows[ri].cells[ci], val, bold=(ci == 0))

    # apply column widths to every cell
    for r in table.rows:
        for ci, c in enumerate(r.cells):
            c.width = COL_W[ci]

    tbl_el = table._tbl
    tbl_el.getparent().remove(tbl_el)
    anchor_el.addprevious(tbl_el)

    anchor_el.getparent().remove(anchor_el)

    doc.save(DOC)
    print('Inserted Table 4.3 with', len(ROWS), 'rows. Tables now:', len(doc.tables))


if __name__ == '__main__':
    main()
