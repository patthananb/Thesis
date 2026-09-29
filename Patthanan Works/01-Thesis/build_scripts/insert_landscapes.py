#!/usr/bin/env python3
"""Add the three IT/OT landscape quadrant figures (Hardware/Software/Protocols) to
Study A (4.1) as Figures 4.1-4.3, with an explanation. Existing Chapter-4 figures
4.0-4.4 are renumbered 4.4-4.8 to keep ascending order."""
import re
from io import BytesIO
from docx import Document
from docx.shared import Cm
from docx.oxml.ns import qn
from PIL import Image

DOC = 'senior_project_report.docx'

FIGS = [
    ('figures/Hardware.png', 1108, 638,
     "Figure 4.1  IT/OT hardware landscape — consequence of failure versus deployment "
     "difficulty. IT assets (laptop, server, cloud compute, switch/router, storage, "
     "firewall) cluster at low consequence and low difficulty, whereas OT assets "
     "(sensors/transmitters, RTU, HMI, PLC, DCS, actuators/VFD, safety relays) sit at "
     "higher consequence and greater deployment complexity."),
    ('figures/software.png', 1103, 636,
     "Figure 4.2  IT/OT software landscape — consequence of failure versus learning "
     "curve. IT and data tools (Node-RED, InfluxDB, Grafana, Telegraf, Docker, "
     "Wireshark) are quicker to adopt and lower-consequence; OT engineering suites "
     "(Ignition, CODESYS, AVEVA, Studio 5000, TIA Portal/WinCC) carry steeper learning "
     "curves and higher consequence of failure."),
    ('figures/protocols.png', 1106, 612,
     "Figure 4.3  IT/OT protocol landscape — determinism versus difficulty of use. "
     "Best-effort IT protocols (HTTP/REST, MQTT, SNMP, Modbus, BACnet) sit lower-left; "
     "deterministic OT fieldbuses (CANopen, EtherNet/IP, PROFINET, EtherCAT, IEC 61850) "
     "sit upper-right; bridging protocols (OPC UA, DNP3, gRPC) span the middle."),
]

EXPLAIN = (
    "Beyond the per-capability matrix of Table 4.1, the IT and OT domains can be "
    "positioned visually along the trade-offs that matter most in each. Figures 4.1–4.3 "
    "plot representative hardware, software, and protocols on two axes each. A consistent "
    "pattern emerges: IT components optimise for flexibility, low cost, and ease of change, "
    "and therefore cluster toward low deployment difficulty and lower-consequence failures; "
    "OT components optimise for determinism, safety, and longevity, and therefore sit toward "
    "higher complexity and higher-consequence failures. The bridging protocols (OPC UA, "
    "DNP3, gRPC) and the convergence software in these views are precisely the elements this "
    "project uses to join the two domains.")


def istab(p):
    return p._p.find('.//' + qn('w:tab')) is not None


def img_par(doc, path, ow, oh):
    buf = BytesIO()
    Image.open(path).convert('RGB').save(buf, 'PNG')
    buf.seek(0)
    p = doc.add_paragraph()
    p.add_run().add_picture(buf, width=Cm(14.0))
    p.alignment = 1
    return p


def main():
    doc = Document(DOC)

    # 1) renumber existing Ch4 figures (descending) 4.4->4.8 ... 4.0->4.4
    remap = [('Figure 4.4', 'Figure 4.8'), ('Figure 4.3', 'Figure 4.7'),
             ('Figure 4.2', 'Figure 4.6'), ('Figure 4.1', 'Figure 4.5'),
             ('Figure 4.0', 'Figure 4.4')]
    inch = False
    for p in doc.paragraphs:
        if istab(p):
            continue
        t = p.text.strip()
        if t.startswith('CHAPTER 4'):
            inch = True
        if t.startswith('CHAPTER 5'):
            inch = False
        if inch:
            for r in p.runs:
                if r.text and 'Figure 4.' in r.text:
                    for a, b in remap:
                        r.text = r.text.replace(a, b)

    # 2) anchor = Study A findings paragraph
    anchor = None
    for p in doc.paragraphs:
        if not istab(p) and p.text.strip().startswith('The matrix confirms the device roles'):
            anchor = p
            break
    if anchor is None:
        raise SystemExit('Study A anchor not found')

    blocks = [doc.add_paragraph(EXPLAIN)._p]
    for path, ow, oh, cap in FIGS:
        blocks.append(img_par(doc, path, ow, oh)._p)
        blocks.append(doc.add_paragraph(cap)._p)

    ref = anchor._p
    for el in blocks:
        el.getparent().remove(el)
        ref.addnext(el)
        ref = el

    doc.save(DOC)
    print('Inserted 3 landscape figures (4.1-4.3); renumbered existing Ch4 figures +4.')


if __name__ == '__main__':
    main()
