"""
Run this script after saving the 4 photos to:
  Senior Project/Thesis paper/figures/

Usage:
  cd "Senior Project/Thesis paper"
  python3 insert_figures.py
"""
import os, sys
from docx import Document
from docx.shared import Cm
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

THESIS = 'senior_project_report.docx'
FIGURES_DIR = 'figures'

FIGURE_MAP = {
    'fig_3_7_grafana_touchscreen.jpg': {
        'placeholder': '[Figure 3.7 — Grafana dashboard screenshot: Temperature & Humidity time-series panel with threshold bands]',
        'caption': 'Figure 3.7  Grafana dashboard on Raspberry Pi 7" DSI touchscreen: Temperature & Humidity time-series panel (Last 6 hours, 10 s auto-refresh). Last reading 29.4 °C, 6-hour mean 28.0 °C.',
        'width_cm': 12,
    },
    'fig_e4_logo_plc_panel.jpg': {
        'placeholder': '[Figure E.4 — Photograph of the Siemens LOGO! 8.4 unit (front panel with display and function keys)]',
        'caption': 'Figure E.4  Siemens LOGO! 8.4 DIN-rail panel assembly: MCB (circuit breaker), Mean Well HDR-60-24 PSU, LOGO! 8.4 logic module with front display, and field I/O push-button/indicator station.',
        'width_cm': 12,
    },
    'fig_e8_raspberry_pi4.jpg': {
        'placeholder': '[Figure E.8 — Photograph of the Raspberry Pi 4 Model B (4 GB) with official 7" DSI touchscreen attached]',
        'caption': 'Figure E.8  Raspberry Pi 4 Model B (4 GB) with active-cooling heatsink/fan, Gigabit Ethernet (yellow), DSI ribbon cable to 7" touchscreen, and 5 V/3 A AC–DC adapter.',
        'width_cm': 12,
    },
    'fig_3_2_testbed_esp32_sensors.jpg': {
        'placeholder': '[Figure 3.2 — Hardware photograph: complete testbed assembly showing LOGO! 8.4, Waveshare ESP32-S3-Relay-6CH, XY-MD02, SDM230, and Raspberry Pi 4 wired together]',
        'caption': 'Figure 3.2  IT/OT testbed: Waveshare ESP32-S3-Relay-6CH (centre, black enclosure) with XY-MD02 temperature/humidity sensor (white, top-left), SDM230 single-phase power meter (grey DIN-rail, right), RS-485 wiring (blue/yellow), and Ethernet connections.',
        'width_cm': 13,
    },
    'fig_4_0_studya_bench.jpg': {
        'placeholder': '[Figure 4.0 — Study A test bench: ESP32-S3 (ESP32S3-WROOM-1, centre) acting as Modbus RTU/TCP gateway',
        'caption': 'Figure 4.0  Study A test bench (breadboard): ESP32-S3 (ESP32S3-WROOM-1, centre) acting as Modbus RTU/TCP gateway; ESP32-C6 (purple board, right) acting as mock Modbus slave. Two MAX3485 RS-485 transceivers (blue boards) bridge the devices via differential RS-485 A/B pair (green/red wires). A third MAX3485 module (top-left) connects to the pymodbus host PC via USB-UART, enabling simultaneous RTU slave emulation and TCP client latency measurement.',
        'width_cm': 13,
    },
}

def insert_image_before_placeholder(doc, placeholder_text, image_path, caption_text, width_cm):
    """Replace a placeholder paragraph with: image paragraph + caption paragraph."""
    for i, p in enumerate(doc.paragraphs):
        if placeholder_text in p.text:
            # Replace placeholder text with caption
            for run in p.runs:
                run.text = ''
            # Add caption text into placeholder paragraph
            run = p.add_run(caption_text)
            run.italic = True
            run.font.size = None  # inherit

            # Insert image paragraph BEFORE this caption
            img_p = OxmlElement('w:p')
            img_pPr = OxmlElement('w:pPr')
            img_jc = OxmlElement('w:jc'); img_jc.set(qn('w:val'), 'center')
            img_pPr.append(img_jc)
            img_p.append(img_pPr)
            p._element.addprevious(img_p)

            # Add the image run
            from docx.shared import Cm as DocxCm
            # Use a temporary paragraph to add picture, then move run
            tmp_p = doc.add_paragraph()
            tmp_run = tmp_p.add_run()
            tmp_run.add_picture(image_path, width=DocxCm(width_cm))
            # Move run element to img_p
            img_p.append(tmp_run._element)
            tmp_p._element.getparent().remove(tmp_p._element)

            print(f'  ✓ Inserted {os.path.basename(image_path)} → "{placeholder_text[:60]}..."')
            return True
    print(f'  ✗ Placeholder not found: "{placeholder_text[:60]}..."')
    return False


def main():
    if not os.path.exists(THESIS):
        print(f'ERROR: {THESIS} not found. Run from the Thesis paper/ directory.')
        sys.exit(1)

    missing = []
    for fname in FIGURE_MAP:
        path = os.path.join(FIGURES_DIR, fname)
        if not os.path.exists(path):
            missing.append(fname)

    if missing:
        print('Missing image files:')
        for f in missing:
            print(f'  → figures/{f}')
        print('\nSave them to the figures/ folder and re-run.')
        sys.exit(1)

    doc = Document(THESIS)
    print(f'Inserting figures into {THESIS}...')

    for fname, info in FIGURE_MAP.items():
        path = os.path.join(FIGURES_DIR, fname)
        insert_image_before_placeholder(
            doc,
            info['placeholder'],
            path,
            info['caption'],
            info['width_cm'],
        )

    out = THESIS.replace('.docx', '_with_figures.docx')
    doc.save(out)
    print(f'\nSaved → {out}')
    print('Review in Word, then rename/overwrite the original if satisfied.')


if __name__ == '__main__':
    main()
