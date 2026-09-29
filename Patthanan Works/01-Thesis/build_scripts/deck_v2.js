const pptxgen = require("pptxgenjs");
const p = new pptxgen();
p.layout = "LAYOUT_WIDE";              // 13.33 x 7.5 in
p.author = "Patthanan Bhandhumanee";
p.title = "IT/OT Integration in IIoT Applications";

const W = 13.33, H = 7.5;
const NAVY = "0F2A43", INK = "1E293B", TEAL = "0E7C86", TEAL2 = "14B8A6",
      AMBER = "C9821B", RED = "B23A48", MUTED = "6B7C8F", PANEL = "EEF3F6",
      WHITE = "FFFFFF", LINE = "D6E0E7";
const KRED = "7C1A16", GOLD = "C8A12C";   // KMUTNB brand: ripe-betel-nut red + crown gold
const LOGO = "img/kmutnb_logo.png";       // official crest if present; else wordmark fallback
const fs = require("fs");
const HAS_LOGO = fs.existsSync(LOGO);
function brand(s, dark) {                  // top-right KMUTNB lockup
  if (HAS_LOGO) { s.addImage({ path: LOGO, x: 12.05, y: 0.28, w: 0.95, h: 0.95, sizing: { type: "contain", w: 0.95, h: 0.95 } }); return; }
  s.addText("KMUTNB", { x: 9.93, y: 0.3, w: 3.05, h: 0.36, fontFace: HF, fontSize: 16, bold: true, color: dark ? GOLD : KRED, align: "right", charSpacing: 1, margin: 0 });
}
function badge(s, num) {                    // appealing slide-number chip in KMUTNB red
  s.addShape(p.shapes.ROUNDED_RECTANGLE, { x: 12.2, y: 6.88, w: 0.66, h: 0.42, fill: { color: KRED }, rectRadius: 0.07, shadow: { type: "outer", color: "000000", blur: 4, offset: 1, angle: 90, opacity: 0.25 } });
  s.addText([{ text: String(num), options: { bold: true, color: WHITE, fontSize: 13 } }, { text: " / 16", options: { color: "E8C9B8", fontSize: 8 } }], { x: 12.2, y: 6.88, w: 0.66, h: 0.42, fontFace: BF, align: "center", valign: "middle", margin: 0 });
}
const HF = "Georgia", BF = "Calibri";
const FOOT = "Design & Implementation of IT/OT Integration in IIoT Applications";
const sh = () => ({ type: "outer", color: "0F2A43", blur: 7, offset: 3, angle: 135, opacity: 0.16 });

function fit(ow, oh, bw, bh) { const r = Math.min(bw / ow, bh / oh); return { w: ow * r, h: oh * r }; }
function img(s, path, ow, oh, bx, by, bw, bh, frame = true) {
  const d = fit(ow, oh, bw, bh); const x = bx + (bw - d.w) / 2, y = by + (bh - d.h) / 2;
  if (frame) s.addShape(p.shapes.RECTANGLE, { x: x - 0.06, y: y - 0.06, w: d.w + 0.12, h: d.h + 0.12, fill: { color: WHITE }, line: { color: LINE, width: 1 }, shadow: sh() });
  s.addImage({ path, x, y, w: d.w, h: d.h });
}
let n = 0;
function content(title, kicker) {
  const s = p.addSlide(); s.background = { color: WHITE };
  s.addShape(p.shapes.RECTANGLE, { x: 0, y: 0, w: 0.18, h: H, fill: { color: KRED } });
  s.addText(kicker.toUpperCase(), { x: 0.75, y: 0.33, w: 8.8, h: 0.3, fontFace: BF, fontSize: 12, bold: true, color: KRED, charSpacing: 2, margin: 0 });
  s.addText(title, { x: 0.73, y: 0.6, w: 12.2, h: 0.7, fontFace: HF, fontSize: 27, bold: true, color: NAVY, margin: 0 });
  n++;
  brand(s, false);
  s.addText(FOOT, { x: 0.75, y: 7.04, w: 10.5, h: 0.3, fontFace: BF, fontSize: 8, color: MUTED, margin: 0 });
  badge(s, n);
  return s;
}
function bullets(arr, fs = 15) {
  return arr.map((t) => ({ text: t, options: { bullet: { code: "2022", indent: 16 }, breakLine: true, paraSpaceAfter: 9, color: INK, fontSize: fs, fontFace: BF } }));
}

/* ---------- 1. TITLE ---------- */
{
  const s = p.addSlide(); s.background = { color: NAVY };
  s.addShape(p.shapes.RECTANGLE, { x: 0, y: 0, w: W, h: 0.22, fill: { color: KRED } });
  s.addShape(p.shapes.RECTANGLE, { x: 0, y: H - 0.22, w: W, h: 0.22, fill: { color: GOLD } });
  brand(s, true);
  s.addText("SENIOR PROJECT  ·  KMUTNB  ·  2026", { x: 1.0, y: 1.5, w: 11, h: 0.4, fontFace: BF, fontSize: 15, bold: true, color: GOLD, charSpacing: 3 });
  s.addText("Design and Implementation of\nIT/OT Integration in IIoT Applications", { x: 1.0, y: 2.0, w: 11.3, h: 2.0, fontFace: HF, fontSize: 40, bold: true, color: WHITE, lineSpacingMultiple: 1.05 });
  s.addShape(p.shapes.RECTANGLE, { x: 1.05, y: 4.25, w: 2.6, h: 0.06, fill: { color: AMBER } });
  s.addText([
    { text: "Patthanan Bhandhumanee (Bean)", options: { bold: true, color: WHITE, fontSize: 18, breakLine: true } },
    { text: "Faculty of Engineering, King Mongkut's University of Technology North Bangkok", options: { color: "C7D6E2", fontSize: 13, breakLine: true } },
    { text: "Project Advisor: ____________________", options: { color: "C7D6E2", fontSize: 13 } },
  ], { x: 1.0, y: 4.55, w: 11, h: 1.4, fontFace: BF, paraSpaceAfter: 6 });
}

/* ---------- 2. WHY / THE IT-OT DISCONNECT ---------- */
{
  const s = p.addSlide(); s.background = { color: NAVY };
  s.addShape(p.shapes.RECTANGLE, { x: 0, y: 0, w: W, h: 0.22, fill: { color: KRED } });
  brand(s, true);
  s.addText("WHY THIS PROJECT", { x: 0.9, y: 0.5, w: 9.0, h: 0.35, fontFace: BF, fontSize: 14, bold: true, color: GOLD, charSpacing: 2 });
  s.addText("OT and IT don't speak the same language.", { x: 0.9, y: 0.9, w: 11.5, h: 0.8, fontFace: HF, fontSize: 30, bold: true, color: WHITE });
  const box = (x, label, sub, color, lines) => {
    s.addShape(p.shapes.ROUNDED_RECTANGLE, { x, y: 2.1, w: 4.7, h: 2.7, fill: { color: WHITE }, rectRadius: 0.08, shadow: sh() });
    s.addShape(p.shapes.RECTANGLE, { x, y: 2.1, w: 4.7, h: 0.7, fill: { color } });
    s.addText(label, { x, y: 2.16, w: 4.7, h: 0.36, fontFace: HF, fontSize: 18, bold: true, color: WHITE, align: "center", margin: 0 });
    s.addText(sub, { x, y: 2.5, w: 4.7, h: 0.28, fontFace: BF, fontSize: 11, color: "EAF4F4", align: "center", margin: 0 });
    s.addText(lines.map((t) => ({ text: t, options: { bullet: { code: "2022", indent: 12 }, breakLine: true, paraSpaceAfter: 6, fontSize: 12.5, color: INK, fontFace: BF } })), { x: x + 0.3, y: 2.95, w: 4.1, h: 1.7, valign: "top" });
  };
  box(0.9, "OT — the factory floor", "Operational Technology", AMBER, ["PLCs, sensors, actuators", "Modbus over RS-485 / serial", "Air-gapped, deterministic, proprietary"]);
  box(7.73, "IT — the data world", "Information Technology", TEAL, ["Servers, cloud, dashboards", "MQTT, HTTP, databases", "Networked, flexible, analytical"]);
  s.addShape(p.shapes.OVAL, { x: 5.95, y: 3.0, w: 1.43, h: 0.9, fill: { color: RED } });
  s.addText("✗", { x: 5.95, y: 3.0, w: 1.43, h: 0.9, fontFace: BF, fontSize: 30, bold: true, color: WHITE, align: "center", valign: "middle", margin: 0 });
  s.addText("no common\nprotocol", { x: 5.85, y: 3.92, w: 1.63, h: 0.6, fontFace: BF, fontSize: 11, bold: true, color: "FFD9DE", align: "center", margin: 0 });
  s.addText("The pain:", { x: 0.9, y: 5.15, w: 2, h: 0.4, fontFace: BF, fontSize: 14, bold: true, color: GOLD });
  s.addText([
    { text: "Field data trapped on the floor", options: { bullet: { code: "2022" }, breakLine: true, color: "DCE6EF", fontSize: 13, paraSpaceAfter: 4 } },
    { text: "Manual meter readings, no live visibility", options: { bullet: { code: "2022" }, breakLine: true, color: "DCE6EF", fontSize: 13, paraSpaceAfter: 4 } },
  ], { x: 0.9, y: 5.5, w: 5.8, h: 1.3, fontFace: BF, valign: "top" });
  s.addText([
    { text: "Engineers can't see operations data", options: { bullet: { code: "2022" }, breakLine: true, color: "DCE6EF", fontSize: 13, paraSpaceAfter: 4 } },
    { text: "Security blind spots when finally connected", options: { bullet: { code: "2022" }, breakLine: true, color: "DCE6EF", fontSize: 13, paraSpaceAfter: 4 } },
  ], { x: 7.0, y: 5.5, w: 5.5, h: 1.3, fontFace: BF, valign: "top" });
}

/* ---------- 3. OBJECTIVES & SCOPE ---------- */
{
  const s = content("Objectives & Scope", "Goals");
  s.addText("This project bridges that gap — and measures how well.", { x: 0.75, y: 1.55, w: 12, h: 0.4, fontFace: BF, fontSize: 14, italic: true, color: MUTED, margin: 0 });
  s.addText("OBJECTIVES", { x: 0.75, y: 2.0, w: 7.3, h: 0.35, fontFace: BF, fontSize: 14, bold: true, color: TEAL, margin: 0 });
  s.addText(bullets([
    "Build a reproducible IT/OT testbed: ESP32-S3 MCU + Raspberry Pi 4 SBC + Siemens LOGO! 8.4 PLC over Modbus TCP and MQTT.",
    "Benchmark 10 open-source ESP32 Modbus-TCP gateway libraries (latency, throughput, resources, fault recovery).",
    "Compare Node-RED vs Telegraf as the MQTT-to-InfluxDB pipeline.",
    "Demonstrate the security impact of unauthenticated Modbus and anonymous MQTT.",
  ], 14.5), { x: 0.75, y: 2.4, w: 7.4, h: 4.0, valign: "top" });
  s.addShape(p.shapes.RECTANGLE, { x: 8.5, y: 2.0, w: 4.2, h: 4.4, fill: { color: PANEL }, line: { color: LINE, width: 1 } });
  s.addShape(p.shapes.RECTANGLE, { x: 8.5, y: 2.0, w: 4.2, h: 0.5, fill: { color: NAVY } });
  s.addText("SCOPE", { x: 8.5, y: 2.0, w: 4.2, h: 0.5, fontFace: BF, fontSize: 14, bold: true, color: WHITE, align: "center", valign: "middle" });
  s.addText([
    { text: "In scope", options: { bold: true, color: TEAL, fontSize: 13, breakLine: true, paraSpaceAfter: 3 } },
    { text: "Modbus RTU/TCP, MQTT, TIG stack, Docker Compose, passive traffic analysis, open-source library evaluation.", options: { color: INK, fontSize: 12.5, breakLine: true, paraSpaceAfter: 12 } },
    { text: "Out of scope", options: { bold: true, color: AMBER, fontSize: 13, breakLine: true, paraSpaceAfter: 3 } },
    { text: "OPC-UA, industrial certification, production-grade security hardening, cloud deployment.", options: { color: INK, fontSize: 12.5 } },
  ], { x: 8.75, y: 2.7, w: 3.7, h: 3.6, fontFace: BF, valign: "top" });
}

/* ---------- 4. BACKGROUND ---------- */
{
  const s = content("Background: Purdue Model & Protocols", "Background");
  s.addText(bullets([
    "The Purdue / ISA-95 model defines where each device sits: L0 field sensors → L1 control → L2 edge → L3 site operations.",
    "Convergence means moving field data up these layers without breaking OT protocols at the bottom.",
  ]), { x: 0.75, y: 1.7, w: 12.0, h: 1.4, valign: "top" });
  const card = (x, name, color, lines) => {
    s.addShape(p.shapes.RECTANGLE, { x, y: 3.25, w: 5.7, h: 3.1, fill: { color: WHITE }, line: { color: LINE, width: 1 }, shadow: sh() });
    s.addShape(p.shapes.RECTANGLE, { x, y: 3.25, w: 5.7, h: 0.6, fill: { color } });
    s.addText(name, { x, y: 3.25, w: 5.7, h: 0.6, fontFace: HF, fontSize: 18, bold: true, color: WHITE, align: "center", valign: "middle" });
    s.addText(lines.map((t) => ({ text: t, options: { bullet: { code: "2022", indent: 14 }, breakLine: true, paraSpaceAfter: 7, fontSize: 13, color: INK, fontFace: BF } })), { x: x + 0.25, y: 4.0, w: 5.2, h: 2.2, valign: "top" });
  };
  card(0.75, "Modbus", TEAL, ["Master/slave; RTU over RS-485 + TCP (port 502)", "Register & coil data model (FC03/04 read, FC05 write)", "Simple, deterministic — but no auth or encryption"]);
  card(6.95, "MQTT", NAVY, ["Lightweight publish/subscribe over TCP (broker)", "QoS 0/1/2 delivery guarantees; topic hierarchy", "Ideal northbound IT transport for telemetry"]);
}

/* ---------- 5. IT vs OT: SOFTWARE & HARDWARE ---------- */
{
  const s = content("IT vs OT: Software & Hardware", "The two worlds");
  const col = (x, title, color, hw, sw) => {
    s.addShape(p.shapes.RECTANGLE, { x, y: 1.7, w: 5.85, h: 4.9, fill: { color: WHITE }, line: { color: LINE, width: 1 }, shadow: sh() });
    s.addShape(p.shapes.RECTANGLE, { x, y: 1.7, w: 5.85, h: 0.62, fill: { color } });
    s.addText(title, { x, y: 1.7, w: 5.85, h: 0.62, fontFace: HF, fontSize: 18, bold: true, color: WHITE, align: "center", valign: "middle" });
    s.addText("Hardware", { x: x + 0.3, y: 2.45, w: 5.2, h: 0.3, fontFace: BF, fontSize: 13, bold: true, color: color, margin: 0 });
    s.addText(hw.map((t) => ({ text: t, options: { bullet: { code: "2022", indent: 12 }, breakLine: true, paraSpaceAfter: 4, fontSize: 12, color: INK, fontFace: BF } })), { x: x + 0.3, y: 2.78, w: 5.25, h: 1.7, valign: "top" });
    s.addText("Software & protocols", { x: x + 0.3, y: 4.55, w: 5.2, h: 0.3, fontFace: BF, fontSize: 13, bold: true, color: color, margin: 0 });
    s.addText(sw.map((t) => ({ text: t, options: { bullet: { code: "2022", indent: 12 }, breakLine: true, paraSpaceAfter: 4, fontSize: 12, color: INK, fontFace: BF } })), { x: x + 0.3, y: 4.88, w: 5.25, h: 1.6, valign: "top" });
  };
  col(0.75, "OT — Operational Technology", AMBER,
    ["Siemens LOGO! 24CE PLC", "ESP32-S3 edge controller", "XY-MD02 sensor, SDM230 meter", "RS-485 field bus"],
    ["IEC 61131-3 Ladder (LOGO! Soft Comfort)", "Modbus RTU & Modbus TCP", "Arduino / PlatformIO firmware (C/C++)"]);
  col(6.73, "IT — Information Technology", TEAL,
    ["Raspberry Pi 4 (4 GB)", "7\" DSI touchscreen kiosk", "Standard TCP/IP LAN"],
    ["Linux (Raspberry Pi OS) + Docker Compose", "Mosquitto (MQTT), Telegraf, Node-RED", "InfluxDB (time-series) + Grafana dashboards"]);
}

/* ---------- 6. ARCHITECTURE (data flow) ---------- */
{
  const s = content("System Architecture — Bridging the Gap", "Design");
  img(s, "img/dataflow.png", 1505, 858, 0.75, 1.55, 8.5, 5.0);
  s.addShape(p.shapes.RECTANGLE, { x: 9.45, y: 1.7, w: 3.25, h: 2.3, fill: { color: PANEL }, line: { color: TEAL, width: 1.5 } });
  s.addText([
    { text: "The bridge", options: { bold: true, color: TEAL, fontSize: 13, breakLine: true, paraSpaceAfter: 3 } },
    { text: "ESP32-S3 translates Modbus (OT) ↔ MQTT (IT) at the edge, decoupling the two worlds.", options: { color: INK, fontSize: 12, breakLine: true } },
  ], { x: 9.6, y: 1.85, w: 2.95, h: 2.0, fontFace: BF, valign: "top" });
  s.addShape(p.shapes.RECTANGLE, { x: 9.45, y: 4.2, w: 3.25, h: 2.3, fill: { color: PANEL }, line: { color: NAVY, width: 1.5 } });
  s.addText([
    { text: "Colour = protocol", options: { bold: true, color: NAVY, fontSize: 13, breakLine: true, paraSpaceAfter: 3 } },
    { text: "Blue Modbus TCP · Green WebSocket · Orange MQTT · Dashed monitoring flow to InfluxDB & Grafana.", options: { color: INK, fontSize: 12, breakLine: true } },
  ], { x: 9.6, y: 4.35, w: 2.95, h: 2.0, fontFace: BF, valign: "top" });
}

/* ---------- 7. HARDWARE TESTBED ---------- */
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

/* ---------- 8. OT LAYER ---------- */
{
  const s = content("OT Layer — Siemens LOGO! 8.4", "OT · Purdue Level 1");
  img(s, "img/plc.jpg", 4080, 3060, 0.75, 1.6, 5.6, 4.9);
  s.addText(bullets([
    "Compact micro-PLC programmed in IEC 61131-3 Ladder Diagram.",
    "Program 1: pump start/stop with self-latching output (Q1) + non-volatile runtime counter (VW4).",
    "Program 2: analogue threshold control on a 0–10 V input.",
    "Model 24CE: 24 V DC supply, transistor outputs (Q1–Q4, 0.3 A); native Modbus TCP server (HR0–HR9).",
    "Deterministic scan cycle: bounded, repeatable, certified (CE/UL/FM/ATEX).",
  ]), { x: 6.7, y: 1.7, w: 6.0, h: 4.8, valign: "top" });
}

/* ---------- 9. EDGE GATEWAY ---------- */
{
  const s = content("Edge Gateway — ESP32-S3 Firmware", "Edge · Purdue Level 2");
  s.addText(bullets([
    "PlatformIO + Arduino core; one cooperative, non-blocking loop() — no delay() calls.",
    "Bridges OT field instruments to IT messaging while keeping Modbus intact at the field edge.",
  ]), { x: 0.75, y: 1.7, w: 12.0, h: 1.3, valign: "top" });
  const role = (x, num, title, lines, color) => {
    s.addShape(p.shapes.ROUNDED_RECTANGLE, { x, y: 3.2, w: 3.85, h: 3.0, fill: { color: WHITE }, line: { color: LINE, width: 1 }, rectRadius: 0.08, shadow: sh() });
    s.addShape(p.shapes.OVAL, { x: x + 0.25, y: 3.45, w: 0.7, h: 0.7, fill: { color } });
    s.addText(num, { x: x + 0.25, y: 3.45, w: 0.7, h: 0.7, fontFace: HF, fontSize: 22, bold: true, color: WHITE, align: "center", valign: "middle" });
    s.addText(title, { x: x + 1.05, y: 3.45, w: 2.7, h: 0.7, fontFace: BF, fontSize: 15, bold: true, color: NAVY, valign: "middle", margin: 0 });
    s.addText(lines, { x: x + 0.3, y: 4.35, w: 3.3, h: 1.7, fontFace: BF, fontSize: 12.5, color: INK, valign: "top" });
  };
  role(0.75, "1", "RTU Master", "Polls XY-MD02 + SDM230 over RS-485 @ 9600 baud every 2 s.", TEAL);
  role(4.74, "2", "MQTT Publisher", "Forwards readings as JSON to the Mosquitto broker (QoS 1).", NAVY);
  role(8.73, "3", "TCP Slave", "Exposes HR0–HR20 on port 502 for diagnostic IP reads.", AMBER);
}

/* ---------- 10. IT LAYER ---------- */
{
  const s = content("IT Layer — TIG Stack on Docker", "IT · Purdue Level 3");
  img(s, "img/powermeter.png", 1367, 1128, 0.75, 1.6, 6.2, 4.9);
  s.addText(bullets([
    "Raspberry Pi 4 runs 11 services in Docker Compose — reproducible & version-controlled.",
    "Pipeline: Mosquitto (1883) → Telegraf → InfluxDB 2 → Grafana.",
    "Four Grafana dashboards (Temp/Humidity, SDM230 power, Pi telemetry, networking) on a 7\" kiosk.",
  ]), { x: 7.2, y: 1.7, w: 5.5, h: 2.4, valign: "top" });
  const chips = ["Mosquitto", "Telegraf", "InfluxDB 2", "Grafana"]; let x = 7.2;
  chips.forEach((c, i) => {
    s.addShape(p.shapes.ROUNDED_RECTANGLE, { x, y: 4.5, w: 1.2, h: 0.6, fill: { color: i % 2 ? NAVY : TEAL }, rectRadius: 0.08 });
    s.addText(c, { x, y: 4.5, w: 1.2, h: 0.6, fontFace: BF, fontSize: 10, bold: true, color: WHITE, align: "center", valign: "middle", margin: 0 });
    if (i < chips.length - 1) s.addText("›", { x: x + 1.18, y: 4.5, w: 0.22, h: 0.6, fontFace: BF, fontSize: 18, bold: true, color: MUTED, align: "center", valign: "middle", margin: 0 });
    x += 1.4;
  });
}

/* ---------- 11. WHAT-IF ANALYSIS ---------- */
{
  const s = content("What If? — Architecture & Reliability", "Design analysis");
  const col = (x, title, color, rows) => {
    s.addShape(p.shapes.RECTANGLE, { x, y: 1.7, w: 5.85, h: 4.9, fill: { color: WHITE }, line: { color: LINE, width: 1 }, shadow: sh() });
    s.addShape(p.shapes.RECTANGLE, { x, y: 1.7, w: 5.85, h: 0.62, fill: { color } });
    s.addText(title, { x, y: 1.7, w: 5.85, h: 0.62, fontFace: HF, fontSize: 17, bold: true, color: WHITE, align: "center", valign: "middle" });
    let yy = 2.55;
    rows.forEach((r) => {
      s.addText([
        { text: "What if " + r.q + "  ", options: { bold: true, color: NAVY, fontSize: 12.5 } },
        { text: "→ " + r.c, options: { color: RED, fontSize: 12.5, breakLine: true } },
        { text: "Mitigation: " + r.m, options: { italic: true, color: TEAL, fontSize: 11.5 } },
      ], { x: x + 0.3, y: yy, w: 5.25, h: 1.2, fontFace: BF, valign: "top", paraSpaceAfter: 2 });
      yy += 1.32;
    });
  };
  col(0.75, "Architecture", AMBER, [
    { q: "there were no edge gateway?", c: "IT must poll OT directly — tight coupling, no Modbus↔MQTT translation, polling load on the PLC.", m: "ESP32-S3 decouples & translates protocols." },
    { q: "a new protocol is added?", c: "Point-to-point links multiply and become brittle.", m: "Broker + gateway = one integration point." },
  ]);
  col(6.73, "Reliability", TEAL, [
    { q: "Wi-Fi drops or the broker dies?", c: "Telemetry gap; in-flight readings are lost.", m: "QoS 1 + retained msgs now; NVS replay buffer (future)." },
    { q: "the microSD card fails?", c: "Single point of failure for the IT host & data.", m: "Scheduled backups + Docker healthchecks (future)." },
  ]);
}

/* ---------- 12. STUDY A ---------- */
{
  const s = content("Study A — Modbus Gateway Library Benchmark", "Results");
  s.addText("FC03 mean round-trip latency on real hardware (lower is better)", { x: 0.75, y: 1.6, w: 8, h: 0.35, fontFace: BF, fontSize: 13, italic: true, color: MUTED, margin: 0 });
  s.addChart(p.charts.BAR, [{ name: "FC3 mean (ms)", labels: ["NamNamIoT", "tobiasfaust", "esp-modbus", "eModbus", "emelianov ★"], values: [24.5, 27.7, 28.0, 30.3, 33.4] }], {
    x: 0.6, y: 2.0, w: 7.3, h: 4.3, barDir: "col", chartColors: [TEAL], chartArea: { fill: { color: WHITE } },
    catAxisLabelColor: INK, valAxisLabelColor: MUTED, catAxisLabelFontSize: 11, valGridLine: { color: "E2E8F0", size: 0.5 }, catGridLine: { style: "none" },
    showValue: true, dataLabelPosition: "outEnd", dataLabelColor: INK, dataLabelFontSize: 11, dataLabelFormatCode: "0.0", showLegend: false, valAxisHidden: true,
  });
  s.addShape(p.shapes.RECTANGLE, { x: 8.3, y: 2.0, w: 4.4, h: 4.3, fill: { color: PANEL }, line: { color: LINE, width: 1 } });
  s.addText("Key findings", { x: 8.55, y: 2.2, w: 4, h: 0.4, fontFace: BF, fontSize: 15, bold: true, color: TEAL, margin: 0 });
  s.addText([
    { text: "10 libraries tested across 10 dimensions; all passed the 20/20 stress runs.", options: { bullet: { code: "2022" }, breakLine: true, paraSpaceAfter: 8, fontSize: 13, color: INK } },
    { text: "NamNamIoT/ModbusMaster was the fastest (24.5 ms mean).", options: { bullet: { code: "2022" }, breakLine: true, paraSpaceAfter: 8, fontSize: 13, color: INK } },
    { text: "emelianov/modbus-esp8266 selected for production: it alone offers a combined TCP-slave + RTU-master.", options: { bullet: { code: "2022" }, breakLine: true, fontSize: 13, color: INK } },
  ], { x: 8.55, y: 2.7, w: 3.95, h: 3.4, fontFace: BF, valign: "top" });
}

/* ---------- 13. STUDY B + SECURITY ---------- */
{
  const s = content("Pipeline Choice & Security Demonstration", "Results");
  s.addShape(p.shapes.RECTANGLE, { x: 0.75, y: 1.7, w: 5.7, h: 4.8, fill: { color: WHITE }, line: { color: LINE, width: 1 }, shadow: sh() });
  s.addShape(p.shapes.RECTANGLE, { x: 0.75, y: 1.7, w: 5.7, h: 0.6, fill: { color: TEAL } });
  s.addText("Study B — Node-RED vs Telegraf", { x: 0.75, y: 1.7, w: 5.7, h: 0.6, fontFace: HF, fontSize: 15, bold: true, color: WHITE, align: "center", valign: "middle" });
  s.addText(bullets([
    "Telegraf: ~20–40 MB idle, lower latency, Git-friendly TOML.",
    "Node-RED: visual debugging, but ~80–120 MB and heavier.",
    "→ Telegraf selected for the production pipeline.",
  ], 13), { x: 1.0, y: 2.45, w: 5.2, h: 3.8, valign: "top" });
  s.addShape(p.shapes.RECTANGLE, { x: 6.95, y: 1.7, w: 5.7, h: 4.8, fill: { color: WHITE }, line: { color: LINE, width: 1 }, shadow: sh() });
  s.addShape(p.shapes.RECTANGLE, { x: 6.95, y: 1.7, w: 5.7, h: 0.6, fill: { color: RED } });
  s.addText("Security — IoT-Sniffer", { x: 6.95, y: 1.7, w: 5.7, h: 0.6, fontFace: HF, fontSize: 15, bold: true, color: WHITE, align: "center", valign: "middle" });
  s.addText(bullets([
    "Modbus FC05 appears as a plaintext frame — no authentication.",
    "Anonymous MQTT: any LAN host can read all telemetry and publish forged data.",
    "mosquitto_pub spoof injects a false spike into Grafana.",
  ], 13), { x: 7.2, y: 2.45, w: 5.2, h: 3.0, valign: "top" });
  s.addShape(p.shapes.RECTANGLE, { x: 7.2, y: 5.6, w: 5.25, h: 0.8, fill: { color: "FBEEDB" }, line: { color: AMBER, width: 1 } });
  s.addText("Needs segmentation, TLS, and authentication.", { x: 7.35, y: 5.6, w: 4.95, h: 0.8, fontFace: BF, fontSize: 12.5, bold: true, color: "8A5A12", valign: "middle" });
}

/* ---------- 14. MCU vs SBC vs PLC ---------- */
{
  const s = content("Right Device at the Right Purdue Level", "Discussion");
  const col = (x, tag, name, color, lines) => {
    s.addShape(p.shapes.RECTANGLE, { x, y: 1.7, w: 3.85, h: 4.5, fill: { color: WHITE }, line: { color: LINE, width: 1 }, shadow: sh() });
    s.addShape(p.shapes.RECTANGLE, { x, y: 1.7, w: 3.85, h: 0.85, fill: { color } });
    s.addText(tag, { x, y: 1.78, w: 3.85, h: 0.3, fontFace: BF, fontSize: 11, bold: true, color: "EAF4F4", align: "center", charSpacing: 1, margin: 0 });
    s.addText(name, { x, y: 2.02, w: 3.85, h: 0.45, fontFace: HF, fontSize: 16, bold: true, color: WHITE, align: "center", valign: "middle", margin: 0 });
    s.addText(lines.map((t) => ({ text: t, options: { bullet: { code: "2022", indent: 13 }, breakLine: true, paraSpaceAfter: 8, fontSize: 12.5, color: INK, fontFace: BF } })), { x: x + 0.28, y: 2.75, w: 3.35, h: 3.3, valign: "top" });
  };
  col(0.75, "LEVEL 2 · EDGE", "MCU — ESP32-S3", TEAL, ["Direct hardware I/O, low cost & power", "Soft real-time cooperative loop", "Best at the field edge & bridging"]);
  col(4.74, "LEVEL 3 · SITE OPS", "SBC — Raspberry Pi 4", NAVY, ["Full Linux + Docker ecosystem", "Non-deterministic (preemptive kernel)", "Best for brokering, storage, dashboards"]);
  col(8.73, "LEVEL 1 · CONTROL", "PLC — LOGO! 24CE", AMBER, ["Deterministic, certified actuation", "Industrial I/O (24 V DC, transistor 0.3 A)", "Best for safety-critical control"]);
  s.addText("Not competitors — complementary layers of one IT/OT system.", { x: 0.75, y: 6.35, w: 12, h: 0.35, fontFace: BF, fontSize: 13, italic: true, bold: true, color: NAVY, align: "center", margin: 0 });
}

/* ---------- 15. SYSTEM LIMITATIONS ---------- */
{
  const s = content("System Limitations", "Honest assessment");
  const lim = (x, y, title, body, color) => {
    s.addShape(p.shapes.RECTANGLE, { x, y, w: 5.85, h: 1.95, fill: { color: WHITE }, line: { color: LINE, width: 1 }, shadow: sh() });
    s.addShape(p.shapes.RECTANGLE, { x, y, w: 0.14, h: 1.95, fill: { color } });
    s.addText(title, { x: x + 0.35, y: y + 0.18, w: 5.3, h: 0.4, fontFace: BF, fontSize: 14, bold: true, color: NAVY, margin: 0 });
    s.addText(body, { x: x + 0.35, y: y + 0.6, w: 5.35, h: 1.25, fontFace: BF, fontSize: 12, color: INK, valign: "top", margin: 0 });
  };
  lim(0.75, 1.7, "Security", "Anonymous MQTT + unauthenticated Modbus on the LAN; no TLS or access control yet.", RED);
  lim(6.73, 1.7, "Determinism", "The IT path (Linux + Wi-Fi) is non-deterministic — unsuitable for hard real-time control.", AMBER);
  lim(0.75, 3.85, "Resilience", "No on-device telemetry buffering; microSD is a single point of failure; Wi-Fi dependency.", AMBER);
  lim(6.73, 3.85, "Scale & scope", "Single-site lab testbed; not industrially certified; no OPC-UA or production hardening.", TEAL);
  s.addShape(p.shapes.RECTANGLE, { x: 0.75, y: 6.05, w: 11.95, h: 0.7, fill: { color: PANEL }, line: { color: TEAL, width: 1 } });
  s.addText("Every limitation maps to a concrete item in Future Work →", { x: 0.95, y: 6.05, w: 11.6, h: 0.7, fontFace: BF, fontSize: 13, bold: true, italic: true, color: NAVY, valign: "middle" });
}

/* ---------- 16. CONCLUSION ---------- */
{
  const s = p.addSlide(); s.background = { color: NAVY };
  s.addShape(p.shapes.RECTANGLE, { x: 0, y: 0, w: W, h: 0.22, fill: { color: KRED } });
  brand(s, true);
  s.addText("CONCLUSION & FUTURE WORK", { x: 0.9, y: 0.55, w: 9.0, h: 0.5, fontFace: BF, fontSize: 15, bold: true, color: GOLD, charSpacing: 2 });
  s.addText("Conclusions", { x: 0.9, y: 1.2, w: 5.6, h: 0.4, fontFace: HF, fontSize: 20, bold: true, color: WHITE });
  s.addText([
    "The IT/OT gap is bridged end-to-end across MCU, SBC, and PLC.",
    "ESP32-S3 translates two Modbus RTU instruments into Modbus TCP + QoS-1 MQTT.",
    "emelianov library + Telegraf chosen via empirical benchmarking.",
    "Security weaknesses of unauthenticated OT traffic demonstrated live.",
  ].map((t) => ({ text: t, options: { bullet: { code: "2022", indent: 14 }, breakLine: true, paraSpaceAfter: 9, fontSize: 13.5, color: "DCE6EF", fontFace: BF } })), { x: 0.9, y: 1.7, w: 5.7, h: 4.6, valign: "top" });
  s.addText("Future Work", { x: 6.95, y: 1.2, w: 5.6, h: 0.4, fontFace: HF, fontSize: 20, bold: true, color: WHITE });
  s.addText([
    "Security: MQTT auth + TLS, VLAN segregation, firewall on port 502.",
    "Reliability: NVS ring buffer for outage replay; OTA updates; SD backups.",
    "Protocol: evaluate OPC-UA (open62541) as a secure OT alternative.",
    "Monitoring: Grafana alerting; multi-site InfluxDB federation.",
  ].map((t) => ({ text: t, options: { bullet: { code: "2022", indent: 14 }, breakLine: true, paraSpaceAfter: 9, fontSize: 13.5, color: "DCE6EF", fontFace: BF } })), { x: 6.95, y: 1.7, w: 5.6, h: 4.6, valign: "top" });
  s.addShape(p.shapes.RECTANGLE, { x: 0.9, y: 6.5, w: 11.5, h: 0.03, fill: { color: GOLD } });
  s.addText("Thank you  ·  Questions & Discussion", { x: 0.9, y: 6.6, w: 11.5, h: 0.5, fontFace: HF, fontSize: 17, bold: true, italic: true, color: GOLD });
}

p.writeFile({ fileName: "IT-OT_Integration_Defense.pptx" }).then((f) => console.log("WROTE", f));
