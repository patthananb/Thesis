#ifdef ARDUINO
// DUT: vwetter/esp32-modbus-gateway
// Library tested: none — vwetter's gateway hand-rolls Modbus RTU frames on
// HardwareSerial. This DUT mirrors that approach.
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

void drainRx() {
  while (modbusSerial.available()) modbusSerial.read();
}

int readFrame(uint8_t *buf, int maxLen) {
  unsigned long deadline = millis() + RESPONSE_TIMEOUT_MS;
  while (!modbusSerial.available()) if (millis() > deadline) return 0;
  int len = 0;
  unsigned long last = millis();
  while (millis() - last < FRAME_GAP_MS) {
    if (modbusSerial.available() && len < maxLen) {
      buf[len++] = modbusSerial.read();
      last = millis();
    }
  }
  return len;
}

int txFrame(uint8_t *buf, int len) {
  uint16_t c = crc16(buf, len);
  buf[len++] = c & 0xFF;
  buf[len++] = (c >> 8) & 0xFF;
  drainRx();
  modbusSerial.write(buf, len);
  modbusSerial.flush();
  return len;
}

bool fc3(uint16_t addr, uint16_t qty, uint16_t *out) {
  uint8_t f[8] = {MODBUS_SLAVE_ID, 0x03,
                  (uint8_t)(addr >> 8), (uint8_t)(addr & 0xFF),
                  (uint8_t)(qty >> 8), (uint8_t)(qty & 0xFF)};
  txFrame(f, 6);
  uint8_t r[256];
  int n = readFrame(r, sizeof(r));
  if (n < 5 || r[0] != MODBUS_SLAVE_ID || r[1] != 0x03) return false;
  if (crc16(r, n - 2) != (uint16_t)(r[n - 2] | (r[n - 1] << 8))) return false;
  uint8_t bc = r[2];
  if (bc != qty * 2) return false;
  for (int i = 0; i < qty; i++) out[i] = (r[3 + i * 2] << 8) | r[3 + i * 2 + 1];
  return true;
}

bool fc6(uint16_t addr, uint16_t val) {
  uint8_t f[8] = {MODBUS_SLAVE_ID, 0x06,
                  (uint8_t)(addr >> 8), (uint8_t)(addr & 0xFF),
                  (uint8_t)(val >> 8), (uint8_t)(val & 0xFF)};
  txFrame(f, 6);
  uint8_t r[8];
  int n = readFrame(r, sizeof(r));
  return n == 8 && r[0] == MODBUS_SLAVE_ID && r[1] == 0x06;
}

bool fc16(uint16_t addr, uint16_t qty, const uint16_t *vals) {
  uint8_t f[256];
  f[0] = MODBUS_SLAVE_ID;
  f[1] = 0x10;
  f[2] = addr >> 8;
  f[3] = addr & 0xFF;
  f[4] = qty >> 8;
  f[5] = qty & 0xFF;
  f[6] = qty * 2;
  for (int i = 0; i < qty; i++) {
    f[7 + i * 2] = vals[i] >> 8;
    f[7 + i * 2 + 1] = vals[i] & 0xFF;
  }
  txFrame(f, 7 + qty * 2);
  uint8_t r[16];
  int n = readFrame(r, sizeof(r));
  return n == 8 && r[0] == MODBUS_SLAVE_ID && r[1] == 0x10;
}

void runStep(const char *label, bool ok, unsigned long us) {
  testsRun++;
  if (ok) testsPassed++;
  Serial.printf(">> %s: %s [us=%lu]\n", label, ok ? "PASS" : "FAIL", us);
}

void setup() {
  Serial.begin(115200);
  delay(2000);
  Serial.println("\n=== DUT: vwetter (raw RTU on HardwareSerial) ===");
  modbusSerial.begin(BAUD, SERIAL_8N1, RS485_RX_PIN, RS485_TX_PIN);
  Serial.println("[DUT] HardwareSerial ready");
}

void loop() {
  cycle++;
  Serial.printf("\n--- Cycle %lu ---\n", cycle);

  uint16_t rv[5] = {0};
  unsigned long t0 = micros();
  bool t1 = fc3(0, 5, rv);
  unsigned long us1 = micros() - t0;
  t1 = t1 && rv[0] == 100 && rv[4] == 500;
  for (int i = 0; i < 5; i++) Serial.printf("  reg[%d]=%u\n", i, rv[i]);
  runStep("T1 FC3 read 0..4", t1, us1);
  delay(200);

  t0 = micros();
  bool t2 = fc6(0, 4242);
  unsigned long us2 = micros() - t0;
  runStep("T2 FC6 write reg 0", t2, us2);
  delay(200);

  uint16_t v = 0;
  t0 = micros();
  bool t3 = fc3(0, 1, &v);
  unsigned long us3 = micros() - t0;
  t3 = t3 && v == 4242;
  Serial.printf("  reg[0]=%u\n", v);
  runStep("T3 FC3 verify write", t3, us3);
  delay(200);

  uint16_t restore[3] = {100, 200, 300};
  t0 = micros();
  bool t4 = fc16(0, 3, restore);
  unsigned long us4 = micros() - t0;
  runStep("T4 FC16 restore", t4, us4);
  delay(200);

  Serial.printf("CYCLE SUMMARY: %lu/%lu PASS\n", testsPassed, testsRun);
  delay(3000);
}
#endif // ARDUINO
