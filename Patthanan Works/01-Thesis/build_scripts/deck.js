const pptxgen = require("pptxgenjs");
const p = new pptxgen();
p.layout = "LAYOUT_WIDE";              // 13.33 x 7.5 in
p.author = "Patthanan Bhandhumanee";
p.title = "IT/OT Integration in IIoT Applications";

const W = 13.33, H = 7.5;
const NAVY = "0F2A43", INK = "1E293B", TEAL = "0E7C86", TEAL2 = "14B8A6",
      AMBER = "C9821B", MUTED = "6B7C8F", PANEL = "EEF3F6", WHITE = "FFFFFF",
      LINE = "D6E0E7";
const HF = "Georgia", BF = "Calibri";
const FOOT = "Design & Implementation of IT/OT Integration in IIoT Applications";

const shadow = () => ({ type: "outer", color: "0F2A43", blur: 7, offset: 3, angle: 135, opacity: 0.16 });

function fit(ow, oh, bw, bh) {       // contain
  const r = Math.min(bw / ow, bh / oh);
  return { w: ow * r, h: oh * r };
}
function img(slide, path, ow, oh, bx, by, bw, bh, frame = true) {
  const d = fit(ow, oh, bw, bh);
  const x = bx + (bw - d.w) / 2, y = by + (bh - d.h) / 2;
  if (frame) slide.addShape(p.shapes.RECTANGLE, { x: x - 0.06, y: y - 0.06, w: d.w + 0.12, h: d.h + 0.12, fill: { color: WHITE }, line: { color: LINE, width: 1 }, shadow: shadow() });
  slide.addImage({ path, x, y, w: d.w, h: d.h });
}

let n = 0;
function content(title, kicker) {
  const s = p.addSlide();
  s.background = { color: WHITE };
  s.addShape(p.shapes.RECTANGLE, { x: 0, y: 0, w: 0.18, h: H, fill: { color: TEAL } });
  s.addText(kicker.toUpperCase(), { x: 0.75, y: 0.33, w: 11.8, h: 0.3, fontFace: BF, fontSize: 12, bold: true, color: TEAL, charSpacing: 2, margin: 0 });
  s.addText(title, { x: 0.73, y: 0.6, w: 12.0, h: 0.7, fontFace: HF, fontSize: 28, bold: true, color: NAVY, margin: 0 });
  n++;
  s.addText(FOOT, { x: 0.75, y: 7.04, w: 10.5, h: 0.3, fontFace: BF, fontSize: 8, color: MUTED, margin: 0 });
  s.addText(String(n), { x: 12.5, y: 7.0, w: 0.6, h: 0.3, fontFace: BF, fontSize: 10, color: MUTED, align: "right", margin: 0 });
  return s;
}
function bullets(arr) {
  return arr.map((t, i) => ({ text: t, options: { bullet: { code: "2022", indent: 16 }, breakLine: true, paraSpaceAfter: 9, color: INK, fontSize: 15, fontFace: BF } }));
}

/* ---------- 1. TITLE ---------- */
{
  const s = p.addSlide();
  s.background = { color: NAVY };
  s.addShape(p.shapes.RECTANGLE, { x: 0, y: 0, w: W, h: 0.22, fill: { color: TEAL } });
  s.addShape(p.shapes.RECTANGLE, { x: 0, y: H - 0.22, w: W, h: 0.22, fill: { color: TEAL } });
  s.addText("SENIOR PROJECT  ·  KMUTNB  ·  2026", { x: 1.0, y: 1.5, w: 11, h: 0.4, fontFace: BF, fontSize: 15, bold: true, color: TEAL2, charSpacing: 3 });
  s.addText("Design and Implementation of\nIT/OT Integration in IIoT Applications", { x: 1.0, y: 2.0, w: 11.3, h: 2.0, fontFace: HF, fontSize: 40, bold: true, color: WHITE, lineSpacingMultiple: 1.05 });
  s.addShape(p.shapes.RECTANGLE, { x: 1.05, y: 4.25, w: 2.6, h: 0.06, fill: { color: AMBER } });
  s.addText([
    { text: "Patthanan Bhandhumanee (Bean)", options: { bold: true, color: WHITE, fontSize: 18, breakLine: true } },
    { text: "Faculty of Engineering, King Mongkut's University of Technology North Bangkok", options: { color: "C7D6E2", fontSize: 13, breakLine: true } },
    { text: "Project Advisor: ____________________", options: { color: "C7D6E2", fontSize: 13 } },
  ], { x: 1.0, y: 4.55, w: 11, h: 1.4, fontFace: BF, paraSpaceAfter: 6 });
}

/* ---------- 2. INTRODUCTION ---------- */
{
  const s = content("The IT/OT Divide", "Introduction");
  s.addText(bullets([
    "Industry 4.0 depends on OT field data — historically locked in air-gapped serial networks (Modbus RTU over RS-485).",
    "IT and cloud systems speak entirely different languages: MQTT, HTTP, and time-series databases.",
    "Bridging the two — IT/OT convergence — is the defining architectural challenge of industrial digitalisation.",
    "Security is often an afterthought: legacy OT protocols carry no authentication or encryption.",
  ]), { x: 0.75, y: 1.7, w: 7.4, h: 4.8, valign: "top" });
  img(s, "img/purdue.png", 1024, 1536, 8.5, 1.55, 4.2, 5.0);
}

/* ---------- 3. OBJECTIVES & SCOPE ---------- */
{
  const s = content("Objectives & Scope", "Goals");
  s.addText("OBJECTIVES", { x: 0.75, y: 1.65, w: 7.3, h: 0.35, fontFace: BF, fontSize: 14, bold: true, color: TEAL, margin: 0 });
  s.addText(bullets([
    "Build a reproducible IT/OT testbed: ESP32-S3 MCU + Raspberry Pi 4 SBC + Siemens LOGO! 8.4 PLC over Modbus TCP and MQTT.",
    "Benchmark 10 open-source ESP32 Modbus-TCP gateway libraries (latency, throughput, resources, fault recovery).",
    "Compare Node-RED vs Telegraf as the MQTT-to-InfluxDB pipeline.",
    "Demonstrate the security impact of unauthenticated Modbus and anonymous MQTT.",
  ]), { x: 0.75, y: 2.05, w: 7.4, h: 4.4, valign: "top" });
  // scope card
  s.addShape(p.shapes.RECTANGLE, { x: 8.5, y: 1.65, w: 4.2, h: 4.7, fill: { color: PANEL }, line: { color: LINE, width: 1 } });
  s.addShape(p.shapes.RECTANGLE, { x: 8.5, y: 1.65, w: 4.2, h: 0.5, fill: { color: NAVY } });
  s.addText("SCOPE", { x: 8.5, y: 1.65, w: 4.2, h: 0.5, fontFace: BF, fontSize: 14, bold: true, color: WHITE, align: "center", valign: "middle" });
  s.addText([
    { text: "In scope", options: { bold: true, color: TEAL, fontSize: 13, breakLine: true, paraSpaceAfter: 3 } },
    { text: "Modbus RTU/TCP, MQTT, TIG stack (Telegraf · InfluxDB 2 · Grafana), Docker Compose, passive traffic analysis, open-source library evaluation.", options: { color: INK, fontSize: 12.5, breakLine: true, paraSpaceAfter: 12 } },
    { text: "Out of scope", options: { bold: true, color: AMBER, fontSize: 13, breakLine: true, paraSpaceAfter: 3 } },
    { text: "OPC-UA, industrial certification, production-grade security hardening, cloud deployment.", options: { color: INK, fontSize: 12.5 } },
  ], { x: 8.75, y: 2.35, w: 3.7, h: 3.8, fontFace: BF, valign: "top" });
}

/* ---------- 4. BACKGROUND ---------- */
{
  const s = content("Background: Purdue Model & Protocols", "Background");
  s.addText(bullets([
    "Purdue / ISA-95 model defines where each device sits: L0 field sensors → L1 control → L2 edge → L3 site operations.",
    "Convergence means moving field data up these layers without breaking OT protocols at the bottom.",
  ]), { x: 0.75, y: 1.7, w: 12.0, h: 1.4, valign: "top" });
  // two protocol cards
  const card = (x, name, color, lines) => {
    s.addShape(p.shapes.RECTANGLE, { x, y: 3.25, w: 5.7, h: 3.1, fill: { color: WHITE }, line: { color: LINE, width: 1 }, shadow: shadow() });
    s.addShape(p.shapes.RECTANGLE, { x, y: 3.25, w: 5.7, h: 0.6, fill: { color } });
    s.addText(name, { x, y: 3.25, w: 5.7, h: 0.6, fontFace: HF, fontSize: 18, bold: true, color: WHITE, align: "center", valign: "middle" });
    s.addText(lines.map((t) => ({ text: t, options: { bullet: { code: "2022", indent: 14 }, breakLine: true, paraSpaceAfter: 7, fontSize: 13, color: INK, fontFace: BF } })), { x: x + 0.25, y: 4.0, w: 5.2, h: 2.2, valign: "top" });
  };
  card(0.75, "Modbus", TEAL, ["Master/slave; RTU over RS-485 + TCP over Ethernet (port 502)", "Register & coil data model (FC03/04 read, FC05 write)", "Simple, deterministic — but no authentication or encryption"]);
  card(6.95, "MQTT", NAVY, ["Lightweight publish/subscribe over TCP (broker-centric)", "QoS 0/1/2 delivery guarantees; topic hierarchy", "Ideal northbound IT transport for telemetry"]);
}

/* ---------- 5. ARCHITECTURE ---------- */
{
  const s = content("System Architecture", "Design");
  img(s, "img/arch.png", 2106, 1022, 0.75, 1.6, 8.2, 4.9);
  s.addShape(p.shapes.RECTANGLE, { x: 9.2, y: 1.7, w: 3.5, h: 2.2, fill: { color: PANEL }, line: { color: TEAL, width: 1.5 } });
  s.addText([
    { text: "Path A — OT direct", options: { bold: true, color: TEAL, fontSize: 13, breakLine: true, paraSpaceAfter: 3 } },
    { text: "LOGO! 8.4 → Modbus TCP → any LAN host → Grafana", options: { color: INK, fontSize: 12, breakLine: true } },
  ], { x: 9.4, y: 1.85, w: 3.15, h: 1.9, fontFace: BF, valign: "top" });
  s.addShape(p.shapes.RECTANGLE, { x: 9.2, y: 4.1, w: 3.5, h: 2.4, fill: { color: PANEL }, line: { color: NAVY, width: 1.5 } });
  s.addText([
    { text: "Path B — Edge bridge", options: { bold: true, color: NAVY, fontSize: 13, breakLine: true, paraSpaceAfter: 3 } },
    { text: "RS-485 sensors → ESP32-S3 → MQTT → Telegraf → InfluxDB → Grafana", options: { color: INK, fontSize: 12, breakLine: true } },
  ], { x: 9.4, y: 4.25, w: 3.15, h: 2.1, fontFace: BF, valign: "top" });
}

/* ---------- 6. HARDWARE ---------- */
{
  const s = content("Hardware Testbed", "Implementation");
  img(s, "img/testbed.jpg", 4080, 3060, 0.75, 1.6, 6.4, 4.9);
  const items = [
    ["Siemens LOGO! 8.4", "Micro-PLC, Modbus TCP server (L1)"],
    ["Waveshare ESP32-S3-Relay-6CH", "Edge gateway: RTU master + MQTT (L2)"],
    ["Raspberry Pi 4 (4 GB) + 7\" touch", "TIG stack host & Grafana kiosk (L3)"],
    ["XY-MD02 (SHT20)", "RS-485 temperature / humidity sensor"],
    ["Eastron SDM230", "RS-485 single-phase power meter"],
  ];
  let y = 1.75;
  items.forEach(([a, b]) => {
    s.addShape(p.shapes.RECTANGLE, { x: 7.5, y, w: 0.12, h: 0.78, fill: { color: TEAL } });
    s.addText([
      { text: a, options: { bold: true, color: NAVY, fontSize: 14, breakLine: true } },
      { text: b, options: { color: MUTED, fontSize: 11.5 } },
    ], { x: 7.75, y, w: 5.0, h: 0.78, fontFace: BF, valign: "middle", margin: 0 });
    y += 0.9;
  });
  s.addText("Total bill of materials ≈ ฿11,860 (indicative Thai retail)", { x: 7.5, y: y + 0.05, w: 5.3, h: 0.4, fontFace: BF, italic: true, fontSize: 12, color: AMBER });
}

/* ---------- 7. OT LAYER ---------- */
{
  const s = content("OT Layer — Siemens LOGO! 8.4", "OT · Purdue Level 1");
  img(s, "img/plc.jpg", 4080, 3060, 0.75, 1.6, 5.6, 4.9);
  s.addText(bullets([
    "Compact micro-PLC programmed in IEC 61131-3 Ladder Diagram.",
    "Program 1: pump start/stop with self-latch relay (Q1) + non-volatile runtime counter (VW4).",
    "Program 2: analogue threshold control on a 0–10 V input.",
    "Exposes a native Modbus TCP server — coils Q1–Q4 and holding registers HR0–HR9.",
    "Deterministic scan cycle: bounded, repeatable, certified (CE/UL/FM/ATEX).",
  ]), { x: 6.7, y: 1.7, w: 6.0, h: 4.8, valign: "top" });
}

/* ---------- 8. EDGE GATEWAY ---------- */
{
  const s = content("Edge Gateway — ESP32-S3 Firmware", "Edge · Purdue Level 2");
  s.addText(bullets([
    "PlatformIO + Arduino core; one cooperative, non-blocking loop() — no delay() calls.",
    "Bridges OT field instruments to IT messaging while keeping Modbus intact at the field edge.",
  ]), { x: 0.75, y: 1.7, w: 12.0, h: 1.3, valign: "top" });
  const role = (x, num, title, lines, color) => {
    s.addShape(p.shapes.ROUNDED_RECTANGLE, { x, y: 3.2, w: 3.85, h: 3.0, fill: { color: WHITE }, line: { color: LINE, width: 1 }, rectRadius: 0.08, shadow: shadow() });
    s.addShape(p.shapes.OVAL, { x: x + 0.25, y: 3.45, w: 0.7, h: 0.7, fill: { color } });
    s.addText(num, { x: x + 0.25, y: 3.45, w: 0.7, h: 0.7, fontFace: HF, fontSize: 22, bold: true, color: WHITE, align: "center", valign: "middle" });
    s.addText(title, { x: x + 1.05, y: 3.45, w: 2.7, h: 0.7, fontFace: BF, fontSize: 15, bold: true, color: NAVY, valign: "middle", margin: 0 });
    s.addText(lines, { x: x + 0.3, y: 4.35, w: 3.3, h: 1.7, fontFace: BF, fontSize: 12.5, color: INK, valign: "top" });
  };
  role(0.75, "1", "RTU Master", "Polls XY-MD02 + SDM230 over RS-485 @ 9600 baud every 2 s.", TEAL);
  role(4.74, "2", "MQTT Publisher", "Forwards readings as JSON to the Mosquitto broker (QoS 1).", NAVY);
  role(8.73, "3", "TCP Slave", "Exposes HR0–HR20 on port 502 for diagnostic IP reads.", AMBER);
}

/* ---------- 9. IT LAYER ---------- */
{
  const s = content("IT Layer — TIG Stack on Docker", "IT · Purdue Level 3");
  img(s, "img/grafana.jpg", 4080, 3060, 0.75, 1.6, 6.0, 4.9);
  s.addText(bullets([
    "Raspberry Pi 4 runs 11 services in Docker Compose — reproducible & version-controlled.",
    "Pipeline: Mosquitto (1883) → Telegraf → InfluxDB 2 → Grafana.",
    "Grafana dashboards served full-screen on a 7\" touchscreen kiosk.",
  ]), { x: 7.05, y: 1.7, w: 5.7, h: 2.2, valign: "top" });
  // pipeline chips
  const chips = ["Mosquitto", "Telegraf", "InfluxDB 2", "Grafana"];
  let x = 7.05;
  chips.forEach((c, i) => {
    s.addShape(p.shapes.ROUNDED_RECTANGLE, { x, y: 4.4, w: 1.25, h: 0.6, fill: { color: i % 2 ? NAVY : TEAL }, rectRadius: 0.08 });
    s.addText(c, { x, y: 4.4, w: 1.25, h: 0.6, fontFace: BF, fontSize: 10.5, bold: true, color: WHITE, align: "center", valign: "middle", margin: 0 });
    if (i < chips.length - 1) s.addText("›", { x: x + 1.22, y: 4.4, w: 0.22, h: 0.6, fontFace: BF, fontSize: 18, bold: true, color: MUTED, align: "center", valign: "middle", margin: 0 });
    x += 1.44;
  });
}

/* ---------- 10. STUDY A ---------- */
{
  const s = content("Study A — Modbus Gateway Library Benchmark", "Results");
  s.addText("FC03 mean round-trip latency on real hardware (lower is better)", { x: 0.75, y: 1.6, w: 8, h: 0.35, fontFace: BF, fontSize: 13, italic: true, color: MUTED, margin: 0 });
  s.addChart(p.charts.BAR, [{
    name: "FC3 mean (ms)",
    labels: ["NamNamIoT", "tobiasfaust", "esp-modbus", "eModbus", "emelianov ★"],
    values: [24.5, 27.7, 28.0, 30.3, 33.4],
  }], {
    x: 0.6, y: 2.0, w: 7.3, h: 4.3, barDir: "col",
    chartColors: [TEAL], chartArea: { fill: { color: WHITE } },
    catAxisLabelColor: INK, valAxisLabelColor: MUTED, catAxisLabelFontSize: 11,
    valGridLine: { color: "E2E8F0", size: 0.5 }, catGridLine: { style: "none" },
    showValue: true, dataLabelPosition: "outEnd", dataLabelColor: INK, dataLabelFontSize: 11, dataLabelFormatCode: "0.0",
    showLegend: false, valAxisHidden: true,
  });
  s.addShape(p.shapes.RECTANGLE, { x: 8.3, y: 2.0, w: 4.4, h: 4.3, fill: { color: PANEL }, line: { color: LINE, width: 1 } });
  s.addText("Key findings", { x: 8.55, y: 2.2, w: 4, h: 0.4, fontFace: BF, fontSize: 15, bold: true, color: TEAL, margin: 0 });
  s.addText([
    { text: "10 libraries tested across 10 dimensions; all passed the 20/20 stress runs.", options: { bullet: { code: "2022" }, breakLine: true, paraSpaceAfter: 8, fontSize: 13, color: INK } },
    { text: "NamNamIoT/ModbusMaster was the fastest (24.5 ms mean).", options: { bullet: { code: "2022" }, breakLine: true, paraSpaceAfter: 8, fontSize: 13, color: INK } },
    { text: "emelianov/modbus-esp8266 selected for production: it alone provides a combined TCP-slave + RTU-master in one library.", options: { bullet: { code: "2022" }, breakLine: true, fontSize: 13, color: INK } },
  ], { x: 8.55, y: 2.7, w: 3.95, h: 3.4, fontFace: BF, valign: "top" });
}

/* ---------- 11. STUDY B ---------- */
{
  const s = content("Study B — Node-RED vs Telegraf", "Results");
  s.addText("MQTT → InfluxDB pipeline: which tool for production?", { x: 0.75, y: 1.6, w: 11, h: 0.35, fontFace: BF, fontSize: 13, italic: true, color: MUTED, margin: 0 });
  const col = (x, title, color, lines, win) => {
    s.addShape(p.shapes.RECTANGLE, { x, y: 2.1, w: 5.7, h: 4.2, fill: { color: WHITE }, line: { color: LINE, width: 1 }, shadow: shadow() });
    s.addShape(p.shapes.RECTANGLE, { x, y: 2.1, w: 5.7, h: 0.65, fill: { color } });
    s.addText(title, { x, y: 2.1, w: 5.7, h: 0.65, fontFace: HF, fontSize: 18, bold: true, color: WHITE, align: "center", valign: "middle" });
    s.addText(lines.map((t) => ({ text: t, options: { bullet: { code: "2022", indent: 14 }, breakLine: true, paraSpaceAfter: 8, fontSize: 13, color: INK, fontFace: BF } })), { x: x + 0.3, y: 2.95, w: 5.1, h: 2.6, valign: "top" });
    s.addText(win, { x: x + 0.3, y: 5.7, w: 5.1, h: 0.5, fontFace: BF, fontSize: 12.5, bold: true, italic: true, color });
  };
  col(0.75, "Telegraf  ✓", TEAL, ["Low idle memory (~20–40 MB)", "Lower latency — no V8 event-loop overhead", "Higher throughput ceiling", "Git-friendly TOML config (version-controllable)"], "→ Selected for the production pipeline");
  col(6.95, "Node-RED", NAVY, ["Visual flow-based debugging", "Rapid prototyping & wiring", "Higher idle memory (~80–120 MB)", "Heavier runtime footprint"], "→ Best for prototyping, not production");
}

/* ---------- 12. SECURITY ---------- */
{
  const s = content("Security Demonstration — IoT-Sniffer", "Results · Security");
  img(s, "img/sniffer.png", 1440, 900, 0.75, 1.65, 6.6, 4.7);
  s.addText(bullets([
    "Custom passive analyser decodes Modbus TCP & MQTT frame-by-frame on the wire.",
    "Modbus FC05 Write Single Coil appears as a plaintext 12-byte frame — no authentication field.",
    "Anonymous MQTT lets any LAN host subscribe to all telemetry and publish forged data.",
    "mosquitto_pub spoofing injects a false sensor spike straight into Grafana.",
  ]), { x: 7.6, y: 1.7, w: 5.1, h: 3.6, valign: "top" });
  s.addShape(p.shapes.RECTANGLE, { x: 7.6, y: 5.5, w: 5.1, h: 0.95, fill: { color: "FBEEDB" }, line: { color: AMBER, width: 1 } });
  s.addText("Implication: OT protocols demand network segmentation, TLS, and authentication.", { x: 7.8, y: 5.5, w: 4.8, h: 0.95, fontFace: BF, fontSize: 12.5, bold: true, color: "8A5A12", valign: "middle" });
}

/* ---------- 13. MCU vs SBC vs PLC ---------- */
{
  const s = content("Right Device at the Right Purdue Level", "Discussion");
  const col = (x, tag, name, color, lines) => {
    s.addShape(p.shapes.RECTANGLE, { x, y: 1.7, w: 3.85, h: 4.6, fill: { color: WHITE }, line: { color: LINE, width: 1 }, shadow: shadow() });
    s.addShape(p.shapes.RECTANGLE, { x, y: 1.7, w: 3.85, h: 0.85, fill: { color } });
    s.addText(tag, { x, y: 1.78, w: 3.85, h: 0.3, fontFace: BF, fontSize: 11, bold: true, color: "EAF4F4", align: "center", charSpacing: 1, margin: 0 });
    s.addText(name, { x, y: 2.02, w: 3.85, h: 0.45, fontFace: HF, fontSize: 16, bold: true, color: WHITE, align: "center", valign: "middle", margin: 0 });
    s.addText(lines.map((t) => ({ text: t, options: { bullet: { code: "2022", indent: 13 }, breakLine: true, paraSpaceAfter: 8, fontSize: 12.5, color: INK, fontFace: BF } })), { x: x + 0.28, y: 2.75, w: 3.35, h: 3.4, valign: "top" });
  };
  col(0.75, "LEVEL 2 · EDGE", "MCU — ESP32-S3", TEAL, ["Direct hardware I/O, low cost & power", "Soft real-time cooperative loop", "Best at the field edge & protocol bridging"]);
  col(4.74, "LEVEL 3 · SITE OPS", "SBC — Raspberry Pi 4", NAVY, ["Full Linux + Docker ecosystem", "Non-deterministic (preemptive kernel)", "Best for brokering, storage & dashboards"]);
  col(8.73, "LEVEL 1 · CONTROL", "PLC — LOGO! 8.4", AMBER, ["Deterministic, certified actuation", "Industrial I/O (24 V, relay 10 A)", "Best for safety-critical control"]);
  s.addText("Not competitors — complementary layers of one IT/OT system.", { x: 0.75, y: 6.45, w: 12, h: 0.35, fontFace: BF, fontSize: 13, italic: true, bold: true, color: NAVY, align: "center", margin: 0 });
}

/* ---------- 14. CONCLUSION ---------- */
{
  const s = p.addSlide();
  s.background = { color: NAVY };
  s.addShape(p.shapes.RECTANGLE, { x: 0, y: 0, w: W, h: 0.22, fill: { color: TEAL } });
  s.addText("CONCLUSION & FUTURE WORK", { x: 0.9, y: 0.55, w: 11.5, h: 0.5, fontFace: BF, fontSize: 15, bold: true, color: TEAL2, charSpacing: 2 });
  s.addText("Conclusions", { x: 0.9, y: 1.2, w: 5.6, h: 0.4, fontFace: HF, fontSize: 20, bold: true, color: WHITE });
  s.addText([
    "End-to-end IT/OT integration successfully implemented across MCU, SBC, and PLC.",
    "ESP32-S3 bridges two Modbus RTU instruments into Modbus TCP and QoS-1 MQTT.",
    "emelianov library + Telegraf chosen for the production gateway and pipeline.",
    "Security weaknesses of unauthenticated OT traffic demonstrated end-to-end.",
  ].map((t) => ({ text: t, options: { bullet: { code: "2022", indent: 14 }, breakLine: true, paraSpaceAfter: 9, fontSize: 13.5, color: "DCE6EF", fontFace: BF } })), { x: 0.9, y: 1.7, w: 5.7, h: 4.6, valign: "top" });
  s.addText("Future Work", { x: 6.95, y: 1.2, w: 5.6, h: 0.4, fontFace: HF, fontSize: 20, bold: true, color: WHITE });
  s.addText([
    "Security: MQTT auth + TLS, VLAN segregation, firewall on port 502.",
    "Firmware: NVS ring buffer for outage replay; OTA updates.",
    "Protocol: evaluate OPC-UA (open62541) as a secure OT alternative.",
    "Monitoring: Grafana threshold alerting; multi-site InfluxDB federation.",
  ].map((t) => ({ text: t, options: { bullet: { code: "2022", indent: 14 }, breakLine: true, paraSpaceAfter: 9, fontSize: 13.5, color: "DCE6EF", fontFace: BF } })), { x: 6.95, y: 1.7, w: 5.6, h: 4.6, valign: "top" });
  s.addShape(p.shapes.RECTANGLE, { x: 0.9, y: 6.5, w: 11.5, h: 0.02, fill: { color: TEAL } });
  s.addText("Thank you  ·  Questions & Discussion", { x: 0.9, y: 6.6, w: 11.5, h: 0.5, fontFace: HF, fontSize: 17, bold: true, italic: true, color: TEAL2 });
}

p.writeFile({ fileName: "IT-OT_Integration_Defense.pptx" }).then((f) => console.log("WROTE", f));
