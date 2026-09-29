#ifdef ARDUINO
// DUT: harihanv/esp32-modbus-gateway
// Library tested: none — harihanv's upstream sketch pulls ArduinoRS485 1.1.1
// which does not compile on ESP32 (expects SERIAL_PORT_HARDWARE / A5 / A6).
// Their own code hand-rolls Modbus RTU on a HardwareSerial anyway. This DUT
// mirrors that approach so the candidate still gets an honest evaluation.
// Wiring: UART1 RX=GPIO8, TX=GPIO9, 9600 8N1, slave id 1
// Style: plain Arduino sketch (setup/loop, no custom classes)

#include <Arduino.h>
#include <HardwareSerial.h>

#define RS485_RX_PIN 8
#define RS485_TX_PIN 9
#define MODBUS_SLAVE_ID 1
#define BAUD 9600
#define RESPONSE_TIMEOUT_MS 1000
#define FRAME_GAP_MS 4

HardwareSerial modbusSerial(1);

unsigned long testsRun = 0;
unsigned long testsPassed = 0;
unsigned long cycle = 0;

uint16_t crc16(const uint8_t *data, size_t len) {
  uint16_t crc = 0xFFFF;
  for (size_t i = 0; i < len; i++) {
    crc ^= data[i];
    for (int j = 0; j < 8; j++) crc = (crc & 1) ? (crc >> 1) ^ 0xA001 : (crc >> 1);
  }
  return crc;
}

int sendAndReceive(uint8_t *buf, int len, uint8_t *resp, int respMax) {
  uint16_t c = crc16(buf, len);
  buf[len++] = c & 0xFF;
  buf[len++] = (c >> 8) & 0xFF;
  while (modbusSerial.available()) modbusSerial.read();
  modbusSerial.write(buf, len);
  modbusSerial.flush();

  unsigned long deadline = millis() + RESPONSE_TIMEOUT_MS;
  while (!modbusSerial.available()) if (millis() > deadline) return 0;
  int n = 0;
  unsigned long last = millis();
  while (millis() - last < FRAME_GAP_MS) {
    if (modbusSerial.available() && n < respMax) {
      resp[n++] = modbusSerial.read();
      last = millis();
    }
  }
  if (n < 4) return 0;
  if (crc16(resp, n - 2) != (uint16_t)(resp[n - 2] | (resp[n - 1] << 8))) return 0;
  return n;
}

void runStep(const char *label, bool ok, unsigned long us) {
  testsRun++;
  if (ok) testsPassed++;
  Serial.printf(">> %s: %s [us=%lu]\n", label, ok ? "PASS" : "FAIL", us);
}

void setup() {
  Serial.begin(115200);
  delay(2000);
  Serial.println("\n=== DUT: harihanv (raw RTU; ArduinoRS485 not usable on ESP32) ===");
  modbusSerial.begin(BAUD, SERIAL_8N1, RS485_RX_PIN, RS485_TX_PIN);
  Serial.println("[DUT] HardwareSerial ready");
}

void loop() {
  cycle++;
  Serial.printf("\n--- Cycle %lu ---\n", cycle);

  uint8_t r[256];

  // T1 FC3 read 0..4
  uint8_t f1[8] = {MODBUS_SLAVE_ID, 0x03, 0, 0, 0, 5};
  unsigned long t0 = micros();
  int n = sendAndReceive(f1, 6, r, sizeof(r));
  unsigned long us1 = micros() - t0;
  bool t1 = (n > 0 && r[1] == 0x03 && r[2] == 10);
  uint16_t rv[5] = {0};
  if (t1) {
    for (int i = 0; i < 5; i++) rv[i] = (r[3 + i * 2] << 8) | r[3 + i * 2 + 1];
    for (int i = 0; i < 5; i++) Serial.printf("  reg[%d]=%u\n", i, rv[i]);
    t1 = rv[0] == 100 && rv[4] == 500;
  }
  runStep("T1 FC3 read 0..4", t1, us1);
  delay(200);

  // T2 FC6 write reg 0 = 4242
  uint8_t f2[8] = {MODBUS_SLAVE_ID, 0x06, 0, 0, 0x10, 0x92};
  t0 = micros();
  n = sendAndReceive(f2, 6, r, sizeof(r));
  unsigned long us2 = micros() - t0;
  bool t2 = (n > 0 && r[1] == 0x06);
  runStep("T2 FC6 write reg 0", t2, us2);
  delay(200);

  // T3 verify
  uint8_t f3[8] = {MODBUS_SLAVE_ID, 0x03, 0, 0, 0, 1};
  t0 = micros();
  n = sendAndReceive(f3, 6, r, sizeof(r));
  unsigned long us3 = micros() - t0;
  uint16_t v = 0;
  bool t3 = (n > 0 && r[1] == 0x03 && r[2] == 2);
  if (t3) {
    v = (r[3] << 8) | r[4];
    Serial.printf("  reg[0]=%u\n", v);
    t3 = (v == 4242);
  }
  runStep("T3 FC3 verify write", t3, us3);
  delay(200);

  // T4 FC16 restore
  uint8_t f4[13] = {MODBUS_SLAVE_ID, 0x10, 0, 0, 0, 3, 6,
                    0, 100, 0, 200, 1, 44};  // 1*256+44=300
  t0 = micros();
  n = sendAndReceive(f4, 13, r, sizeof(r));
  unsigned long us4 = micros() - t0;
  bool t4 = (n > 0 && r[1] == 0x10);
  runStep("T4 FC16 restore", t4, us4);
  delay(200);

  Serial.printf("CYCLE SUMMARY: %lu/%lu PASS\n", testsPassed, testsRun);
  delay(3000);
}
#endif // ARDUINO
