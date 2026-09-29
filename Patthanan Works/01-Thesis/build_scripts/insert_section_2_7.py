#!/usr/bin/env python3
"""Insert new Section 2.7 'Hardware Platforms' into Chapter 2, before the existing
'2.7 Related Work and Research Gap' heading (which is renumbered to 2.8)."""
from docx import Document

DOC = 'senior_project_report.docx'

# (kind, text): h2/h3 = bold heading, body = normal, formula = italic standalone line
BLOCKS = [
    ('h2', '2.7  Hardware Platforms'),
    ('body',
     "The testbed combines three classes of computing hardware — a microcontroller "
     "unit (MCU), a single-board computer (SBC), and a programmable logic controller "
     "(PLC) — together with RS-485 field instruments. Each class embodies a different "
     "trade-off between determinism, computational power, I/O capability, and cost, and "
     "each maps to a specific layer of the Purdue model introduced in Section 2.1. This "
     "section explains the operating principles of each device; full electrical and "
     "mechanical specifications are listed in Appendix E, and a quantitative role "
     "comparison is given in Section 4.4."),

    ('h3', '2.7.1  Microcontroller Unit: Espressif ESP32-S3'),
    ('body',
     "The ESP32-S3 is a system-on-chip (SoC) built around a dual-core Xtensa LX7 32-bit "
     "processor clocked up to 240 MHz, integrating Wi-Fi, Bluetooth Low Energy, on-chip "
     "SRAM, and a wide peripheral set on a single die (512 KB SRAM, 2 MB PSRAM, 8 MB "
     "flash on the board used here). Unlike a general-purpose computer it has no "
     "memory-management unit (MMU) and runs no conventional operating system: firmware "
     "executes directly on the hardware, optionally scheduled by the lightweight "
     "FreeRTOS kernel. In this project the firmware is written in C/C++ on the Arduino "
     "core (built with PlatformIO) as a cooperative, non-blocking loop in which the "
     "developer interleaves tasks manually using millis() timing comparisons rather than "
     "relying on a preemptive scheduler."),
    ('body',
     "For analogue acquisition the ESP32-S3 integrates two 12-bit successive-"
     "approximation-register (SAR) ADCs. The smallest voltage an N-bit ADC can resolve — "
     "its quantisation step, or least-significant-bit (LSB) value — is:"),
    ('formula', 'Q = V_ref / 2^N'),
    ('body',
     "For the ESP32-S3 (N = 12, V_ref ≈ 3.3 V) this gives Q = 3.3 V / 4096 ≈ 0.81 mV. "
     "This quantisation sets the floor on the precision of any directly sampled analogue "
     "signal. Digital sensors read over RS-485 avoid this conversion error entirely, "
     "which is why the field instruments in this project (Section 2.7.5) are read "
     "digitally rather than through the on-chip ADC. The MCU therefore occupies Purdue "
     "Level 2 as a low-cost, low-power edge gateway with direct hardware I/O, at the "
     "expense of only soft real-time timing guarantees."),

    ('h3', '2.7.2  Single-Board Computer: Raspberry Pi 4 Model B'),
    ('body',
     "A single-board computer is a complete general-purpose computer on one board. The "
     "Raspberry Pi 4 Model B uses a Broadcom BCM2711 SoC with four ARM Cortex-A72 cores "
     "at 1.5 GHz, an MMU, and 4 GB of LPDDR4 RAM, running a full preemptive Linux "
     "operating system (Raspberry Pi OS). This gives it orders of magnitude more compute "
     "and memory than the MCU and access to the entire Debian software ecosystem — here "
     "the Docker engine and the Telegraf–InfluxDB–Grafana (TIG) stack."),
    ('body',
     "The cost of this generality is timing non-determinism. A preemptive, time-sharing "
     "kernel is optimised for average throughput, not worst-case latency. The response "
     "time of a task is the sum of its own execution time and the scheduling delay "
     "introduced by context switches, interrupts, and resource contention:"),
    ('formula', 't_response = t_execute + t_schedule(jitter)'),
    ('body',
     "Because t_schedule is effectively unbounded in a standard (non-real-time) Linux "
     "kernel, the SBC cannot guarantee hard deadlines. This is acceptable for protocol "
     "brokering, time-series ingestion, and dashboard serving at Purdue Level 3, but "
     "unsuitable for direct field actuation. A further practical limitation is that the "
     "operating system and data reside on a microSD card, a component with finite write "
     "endurance that constitutes a single point of failure."),

    ('h3', '2.7.3  Programmable Logic Controller: Siemens LOGO! 8.4'),
    ('body',
     "A programmable logic controller is a ruggedised industrial controller that "
     "executes its control program in a strictly periodic scan cycle. The Siemens LOGO! "
     "8.4 is a compact logic module programmed in the IEC 61131-3 graphical languages "
     "Ladder Diagram (LAD) and Function Block Diagram (FBD). Each scan cycle consists of "
     "three deterministic phases — the controller first copies all physical inputs into "
     "an input image table, then executes the user program exactly once, and finally "
     "writes the output image to the physical outputs:"),
    ('formula', 'T_scan = t_read + t_execute + t_write'),
    ('body',
     "Because inputs are sampled only at the start of a cycle and outputs are updated "
     "only at its end, the worst-case input-to-output response time is bounded by "
     "approximately two scan cycles:"),
    ('formula', 't_response(max) ≈ 2 × T_scan'),
    ('body',
     "This bounded, repeatable timing is precisely what makes a PLC suitable for "
     "safety-related actuation and is the basis of the industrial certifications it "
     "carries (CE, UL, FM, ATEX). The LOGO! 8.4 provides genuine industrial I/O — 24 VDC "
     "digital inputs, 0–10 V / 4–20 mA analogue inputs (converted via a shunt resistor "
     "as derived in Section 2.1.2), and relay outputs rated 10 A — and its integrated "
     "Ethernet port exposes a Modbus TCP server that bridges Purdue Level 1 directly to "
     "Level 3."),

    ('h3', '2.7.4  Relay Output Stage and Galvanic Isolation'),
    ('body',
     "Both the ESP32-S3 relay board and the LOGO! switch real loads through "
     "electromechanical relays. A logic-level GPIO (3.3 V, a few milliamps) cannot drive "
     "a relay coil directly, so each channel uses a driver stage with an optocoupler for "
     "galvanic isolation: the GPIO energises an LED inside the optocoupler (for example a "
     "PC817), whose phototransistor in turn switches the transistor driving the relay "
     "coil. The optocoupler breaks the conductive path between the low-voltage logic and "
     "the switched circuit, forming an isolation barrier — rated 5 kV on the Waveshare "
     "board — that protects the microcontroller from transients on the load side. A "
     "free-wheeling (flyback) diode placed across the coil clamps the inductive turn-off "
     "spike that would otherwise appear across the driver, since the voltage across an "
     "inductor is:"),
    ('formula', 'V_L = −L (di/dt)'),

    ('h3', '2.7.5  Field Instruments'),
    ('body',
     "The XY-MD02 transmitter is built around the Sensirion SHT20 sensing element. "
     "Relative humidity is measured capacitively: a polymer dielectric absorbs water "
     "vapour, changing its permittivity and hence the capacitance of a sense capacitor, "
     "which the sensor's on-chip ASIC converts to a calibrated digital value. "
     "Temperature is derived from a bandgap reference whose output voltage varies "
     "predictably with absolute temperature. The module exposes both quantities as "
     "Modbus RTU input registers (temperature ×10 and humidity ×10), so the ESP32-S3 "
     "reads engineering values directly over RS-485, avoiding the ADC quantisation of "
     "Section 2.7.1."),
    ('body',
     "The SDM230 single-phase energy meter measures a 230 V mains circuit and computes "
     "electrical quantities digitally. It samples the instantaneous line voltage v(t) "
     "and current i(t) — the latter through an internal shunt — many times per mains "
     "cycle and integrates their product to obtain the real (active) power averaged over "
     "the period T:"),
    ('formula', 'P = (1/T) ∫ v(t) · i(t) dt'),
    ('body',
     "Active energy is the time integral of power, reported in kilowatt-hours:"),
    ('formula', 'E = ∫ P dt'),
    ('body',
     "while the apparent power is S = V_rms × I_rms and the power factor is PF = P / S. "
     "All of these values are published over RS-485 as Modbus holding registers, giving "
     "the edge gateway true-RMS electrical measurements without any additional metering "
     "hardware."),
    ('blank', ''),
]


def add_block(doc, kind, text):
    p = doc.add_paragraph()
    if kind == 'blank':
        return p
    run = p.add_run(text)
    if kind in ('h2', 'h3'):
        run.bold = True
    elif kind == 'formula':
        run.italic = True
    return p


def main():
    doc = Document(DOC)

    # anchor: the existing '2.7  Related Work and Research Gap' heading
    anchor = None
    for p in doc.paragraphs:
        t = p.text.strip()
        if t.startswith('2.7') and 'Related Work' in t:
            anchor = p
            break
    if anchor is None:
        raise SystemExit('Related Work heading not found')

    # build new paragraphs at end, then move them (in order) before the anchor
    new_paras = [add_block(doc, k, t) for k, t in BLOCKS]
    for np in new_paras:
        el = np._p
        el.getparent().remove(el)
        anchor._p.addprevious(el)

    # renumber the anchor heading 2.7 -> 2.8 (preserve bold)
    for r in anchor.runs:
        if '2.7' in r.text:
            r.text = r.text.replace('2.7', '2.8', 1)
            break
    else:
        # fallback: rebuild text
        full = anchor.text.replace('2.7', '2.8', 1)
        for r in list(anchor.runs):
            r._element.getparent().remove(r._element)
        anchor.add_run(full).bold = True

    doc.save(DOC)
    print('Inserted Section 2.7 (', len(BLOCKS), 'blocks ); renumbered Related Work to 2.8.')


if __name__ == '__main__':
    main()
