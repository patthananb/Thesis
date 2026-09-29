#!/usr/bin/env python3
"""Insert Table 2.2 (MQTT 5.0 control packet types) replacing the placeholder."""
from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Cm

DOC = 'senior_project_report.docx'

CAPTION = ('Table 2.2  MQTT 5.0 control packet types (ISO/IEC 20922:2016) [6][16].')

HEADERS = ['Packet type', 'Code', 'Direction', 'Purpose']

C2S, S2C, BOTH = 'Client → Server', 'Server → Client', 'Client ↔ Server'

ROWS = [
    ['CONNECT', '0x01', C2S, 'Session initiation; carries Client ID, Clean Session, LWT, and Keep Alive'],
    ['CONNACK', '0x02', S2C, 'Connection acknowledgement with Session Present flag and return code'],
    ['PUBLISH', '0x03', BOTH, 'Carries topic name, optional Packet Identifier (QoS >= 1), and payload'],
    ['PUBACK', '0x04', BOTH, 'QoS 1 acknowledgement from the receiver'],
    ['PUBREC', '0x05', BOTH, 'QoS 2 publish received (step 1 of the exactly-once handshake)'],
    ['PUBREL', '0x06', BOTH, 'QoS 2 publish release (step 2 of the exactly-once handshake)'],
    ['PUBCOMP', '0x07', BOTH, 'QoS 2 publish complete (step 3 of the exactly-once handshake)'],
    ['SUBSCRIBE', '0x08', C2S, 'Client requests a topic filter with a minimum QoS'],
    ['SUBACK', '0x09', S2C, 'Broker confirms the subscription and the granted QoS'],
    ['UNSUBSCRIBE', '0x0A', C2S, 'Client removes one or more subscriptions'],
    ['UNSUBACK', '0x0B', S2C, 'Broker acknowledges the unsubscribe request'],
    ['PINGREQ', '0x0C', C2S, 'Keep-alive heartbeat request (every Keep Alive interval, default 60 s)'],
    ['PINGRESP', '0x0D', S2C, 'Keep-alive heartbeat response'],
    ['DISCONNECT', '0x0E', BOTH, 'Clean session termination; suppresses the LWT when sent by the client'],
    ['AUTH', '0x0F', BOTH, 'Enhanced authentication exchange (new in MQTT 5.0; not used here)'],
]

COL_W = [Cm(3.0), Cm(1.6), Cm(3.4), Cm(8.4)]


def set_cell(cell, text, bold=False, align=None):
    cell.text = ''
    p = cell.paragraphs[0]
    if align is not None:
        p.alignment = align
    r = p.add_run(text)
    r.bold = bold


def main():
    doc = Document(DOC)

    anchor = None
    for p in doc.paragraphs:
        if p.text.strip().startswith('[Table 2.2'):
            anchor = p
            break
    if anchor is None:
        raise SystemExit('placeholder for Table 2.2 not found')
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
        al = WD_ALIGN_PARAGRAPH.CENTER if ci == 1 else None
        set_cell(table.rows[0].cells[ci], h, bold=True, align=al)
    for ri, row in enumerate(ROWS, start=1):
        for ci, val in enumerate(row):
            al = WD_ALIGN_PARAGRAPH.CENTER if ci == 1 else None
            set_cell(table.rows[ri].cells[ci], val, bold=(ci == 0), align=al)

    for r in table.rows:
        for ci, c in enumerate(r.cells):
            c.width = COL_W[ci]

    tbl_el = table._tbl
    tbl_el.getparent().remove(tbl_el)
    anchor_el.addprevious(tbl_el)

    anchor_el.getparent().remove(anchor_el)

    doc.save(DOC)
    print('Inserted Table 2.2 with', len(ROWS), 'rows. Tables now:', len(doc.tables))


if __name__ == '__main__':
    main()
