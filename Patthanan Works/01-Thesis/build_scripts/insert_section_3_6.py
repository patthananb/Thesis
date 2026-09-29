#!/usr/bin/env python3
"""Rewrite Section 3.6 (IoT-Sniffer): new description matching the packet-inspector
screenshot, and insert the screenshot as Figure 3.9 (replacing the placeholder)."""
from io import BytesIO
from docx import Document
from docx.shared import Cm
from PIL import Image

DOC = 'senior_project_report.docx'
IMG = 'figures/figure3.9_iot_sniffer_packet_inspector.png'

DESC1 = (
    "The IoT-Sniffer (github.com/patthananb/IoT-sniffer) is a passive, real-time "
    "traffic analyser developed for this project to make the testbed's industrial "
    "exchanges directly observable. It captures packets on a named network interface "
    "with scapy, reassembles each TCP stream per flow, and decodes frames using "
    "pure-Python parsers — no external protocol libraries — before streaming both the "
    "decoded frames and a 1 Hz metrics snapshot to a browser-based inspector over "
    "WebSocket. It recognises Modbus TCP (port 502), MQTT over TCP (port 1883), and "
    "MQTT over WebSocket (port 8083), and computes live metrics including throughput, "
    "p50/p95/p99 latency, Modbus error rate, and MQTT jitter and reconnects."
)

DESC2 = (
    "Figure 3.9 shows the packet-inspector view. The left rail is a chronological, "
    "protocol-coloured list of captured frames — Modbus Read Coils and Write "
    "Single/Multiple Registers alongside MQTT PUBLISH, PUBACK, and SUBACK — each "
    "annotated with its unit ID, register address, and quantity. The centre pane fully "
    "dissects the selected frame, here a Modbus TCP Write Multiple Registers request: "
    "the MBAP fixed header (Transaction ID 0x4C1E, Protocol ID 0x0000, Length 6, Unit "
    "Identifier 2, Function Code 0x10) is separated from the variable header (Starting "
    "Address 0xC7EB, Quantity 9) and the raw payload hex dump, with the measured "
    "5.5 ms round-trip time reported above. The right column adds an MQTT topic tree "
    "with per-topic message counts, live throughput and packet-loss signals, and a "
    "Top Talkers ranking of the busiest endpoints by byte rate. This frame-level "
    "visibility is what later exposes the plaintext, unauthenticated nature of the "
    "field-bus traffic discussed in Chapter 4."
)

CAPTION = (
    "Figure 3.9  IoT-Sniffer packet inspector decoding a Modbus TCP Write Multiple "
    "Registers request: protocol-coloured packet rail (left), full MBAP/PDU field "
    "breakdown with hex dump (centre), and MQTT topic tree, live throughput / "
    "packet-loss signals, and Top Talkers panel (right)."
)


def set_text(p, text):
    for r in list(p.runs):
        r._element.getparent().remove(r._element)
    p.add_run(text)


def main():
    doc = Document(DOC)

    # locate heading and the two target paragraphs
    paras = doc.paragraphs
    hidx = None
    for i, p in enumerate(paras):
        if p.text.strip().startswith('3.6') and 'IoT-Sniffer' in p.text:
            hidx = i
            break
    if hidx is None:
        raise SystemExit('3.6 heading not found')

    desc = None
    placeholder = None
    for p in paras[hidx + 1:]:
        t = p.text.strip()
        if desc is None and t.startswith('The IoT-sniffer'):
            desc = p
        if t.startswith('[Figure 3.9'):
            placeholder = p
            break
    if desc is None or placeholder is None:
        raise SystemExit(f'desc/placeholder not found (desc={desc is not None}, ph={placeholder is not None})')

    # 1) replace old description with DESC1, add DESC2 after it
    set_text(desc, DESC1)
    d2 = doc.add_paragraph(DESC2)            # appended; move after desc
    desc._p.addnext(d2._p)

    # 2) build image paragraph, insert before placeholder
    buf = BytesIO()
    Image.open(IMG).convert('RGB').save(buf, 'PNG')
    buf.seek(0)
    imgp = doc.add_paragraph()
    imgp.add_run().add_picture(buf, width=Cm(15.0))
    imgp.alignment = 1  # center
    placeholder._p.addprevious(imgp._p)

    # 3) turn the placeholder paragraph into the caption (keep style)
    set_text(placeholder, CAPTION)

    doc.save(DOC)
    print('Section 3.6 rewritten; Figure 3.9 inserted. Tables:', len(doc.tables))


if __name__ == '__main__':
    main()
