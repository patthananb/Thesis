#ifdef ARDUINO
#include <Arduino.h>
#include <HardwareSerial.h>

// RS485 Pin Configuration for ESP32-S3
// Auto-direction transceiver (e.g. MAX13487): no DE/RE pins needed.
#define RS485_RX_PIN 8       // RX pin (to transceiver RO)
#define RS485_TX_PIN 9       // TX pin (to transceiver DI)

// Modbus configuration
#define MODBUS_SLAVE_ID 1
#define BAUDRATE 9600
#define RESPONSE_TIMEOUT 1000  // ms total wait for first byte
#define FRAME_GAP_MS 4         // 3.5 char silence @ 9600 8N1

HardwareSerial modbusSerial(1);  // UART1

// Test counters
unsigned long testsRun = 0;
unsigned long testsPassed = 0;

uint16_t calculateCRC(const uint8_t *data, size_t length) {
  uint16_t crc = 0xFFFF;
  for (size_t i = 0; i < length; i++) {
    crc ^= data[i];
    for (int j = 0; j < 8; j++) {
      if (crc & 1) {
        crc = (crc >> 1) ^ 0xA001;
      } else {
        crc >>= 1;
      }
    }
  }
  return crc;
}

void setupRS485() {
  modbusSerial.begin(BAUDRATE, SERIAL_8N1, RS485_RX_PIN, RS485_TX_PIN);
  Serial.println("[MASTER] RS485 configured (auto-direction transceiver)");
}

// Drain any stale bytes in RX buffer before sending a new request.
void drainRx() {
  while (modbusSerial.available()) modbusSerial.read();
}

// Read one Modbus frame: wait up to RESPONSE_TIMEOUT for first byte,
// then collect bytes until FRAME_GAP_MS of silence.
int readFrame(uint8_t *buffer, int maxLen) {
  unsigned long deadline = millis() + RESPONSE_TIMEOUT;
  while (!modbusSerial.available()) {
    if (millis() > deadline) return 0;
  }

  int len = 0;
  unsigned long lastByteMs = millis();
  while (millis() - lastByteMs < FRAME_GAP_MS) {
    if (modbusSerial.available() && len < maxLen) {
      buffer[len++] = modbusSerial.read();
      lastByteMs = millis();
    }
  }
  return len;
}

// Verify response: slaveID, fc, CRC. Returns true if frame valid.
bool validateResponse(const uint8_t *resp, int len, uint8_t expectedId, uint8_t expectedFc) {
  if (len < 5) {
    Serial.printf("[MASTER] FAIL: frame too short (%d)\n", len);
    return false;
  }
  uint16_t rxCrc = resp[len - 2] | (resp[len - 1] << 8);
  uint16_t calcCrc = calculateCRC(resp, len - 2);
  if (rxCrc != calcCrc) {
    Serial.printf("[MASTER] FAIL: CRC rx=%04X calc=%04X\n", rxCrc, calcCrc);
    return false;
  }
  if (resp[0] != expectedId) {
    Serial.printf("[MASTER] FAIL: wrong slave id %d (want %d)\n", resp[0], expectedId);
    return false;
  }
  if (resp[1] == (expectedFc | 0x80)) {
    Serial.printf("[MASTER] FAIL: exception fc=0x%02X code=%d\n", resp[1], resp[2]);
    return false;
  }
  if (resp[1] != expectedFc) {
    Serial.printf("[MASTER] FAIL: wrong fc 0x%02X (want 0x%02X)\n", resp[1], expectedFc);
    return false;
  }
  return true;
}

// FC3: Read Holding Registers. Returns count read, -1 on error.
int readHoldingRegisters(uint8_t slaveID, uint16_t startAddr, uint16_t quantity, uint16_t *values) {
  uint8_t request[8];
  request[0] = slaveID;
  request[1] = 3;
  request[2] = (startAddr >> 8) & 0xFF;
  request[3] = startAddr & 0xFF;
  request[4] = (quantity >> 8) & 0xFF;
  request[5] = quantity & 0xFF;
  uint16_t crc = calculateCRC(request, 6);
  request[6] = crc & 0xFF;
  request[7] = (crc >> 8) & 0xFF;

  Serial.printf("[MASTER] TX FC3 addr=%d qty=%d\n", startAddr, quantity);
  drainRx();
  modbusSerial.write(request, 8);
  modbusSerial.flush();

  uint8_t response[256];
  int respLen = readFrame(response, sizeof(response));
  if (respLen == 0) {
    Serial.println("[MASTER] FAIL: timeout, no response");
    return -1;
  }

  Serial.printf("[MASTER] RX %d bytes: ", respLen);
  for (int i = 0; i < respLen; i++) Serial.printf("%02X ", response[i]);
  Serial.println();

  if (!validateResponse(response, respLen, slaveID, 3)) return -1;

  uint8_t byteCount = response[2];
  uint16_t regCount = byteCount / 2;
  if (regCount != quantity) {
    Serial.printf("[MASTER] FAIL: register count %d (want %d)\n", regCount, quantity);
    return -1;
  }
  for (int i = 0; i < regCount; i++) {
    values[i] = (response[3 + i * 2] << 8) | response[3 + i * 2 + 1];
  }

  Serial.printf("[MASTER] PASS: read %d regs\n", regCount);
  for (int i = 0; i < regCount; i++) {
    Serial.printf("  Reg[%d] = %d\n", startAddr + i, values[i]);
  }
  return regCount;
}

// FC16: Write Multiple Holding Registers. Returns true on success.
bool writeHoldingRegisters(uint8_t slaveID, uint16_t startAddr, uint16_t quantity, const uint16_t *values) {
  uint8_t request[256];
  request[0] = slaveID;
  request[1] = 16;
  request[2] = (startAddr >> 8) & 0xFF;
  request[3] = startAddr & 0xFF;
  request[4] = (quantity >> 8) & 0xFF;
  request[5] = quantity & 0xFF;
  request[6] = quantity * 2;
  for (int i = 0; i < quantity; i++) {
    request[7 + i * 2] = (values[i] >> 8) & 0xFF;
    request[7 + i * 2 + 1] = values[i] & 0xFF;
  }
  int reqLen = 7 + quantity * 2;
  uint16_t crc = calculateCRC(request, reqLen);
  request[reqLen++] = crc & 0xFF;
  request[reqLen++] = (crc >> 8) & 0xFF;

  Serial.printf("[MASTER] TX FC16 addr=%d qty=%d\n", startAddr, quantity);
  for (int i = 0; i < quantity; i++) {
    Serial.printf("  Val[%d] = %d\n", startAddr + i, values[i]);
  }
  drainRx();
  modbusSerial.write(request, reqLen);
  modbusSerial.flush();

  uint8_t response[256];
  int respLen = readFrame(response, sizeof(response));
  if (respLen == 0) {
    Serial.println("[MASTER] FAIL: timeout, no response");
    return false;
  }

  Serial.printf("[MASTER] RX %d bytes: ", respLen);
  for (int i = 0; i < respLen; i++) Serial.printf("%02X ", response[i]);
  Serial.println();

  if (!validateResponse(response, respLen, slaveID, 16)) return false;

  uint16_t echoAddr = (response[2] << 8) | response[3];
  uint16_t echoQty = (response[4] << 8) | response[5];
  if (echoAddr != startAddr || echoQty != quantity) {
    Serial.printf("[MASTER] FAIL: echo mismatch addr=%d qty=%d\n", echoAddr, echoQty);
    return false;
  }

  Serial.println("[MASTER] PASS: write ok");
  return true;
}

void runStep(const char *label, bool ok) {
  testsRun++;
  if (ok) testsPassed++;
  Serial.printf(">> %s: %s\n", label, ok ? "PASS" : "FAIL");
}

void setup() {
  Serial.begin(115200);
  delay(2000);

  Serial.println("\n\n=== ESP32-S3 Modbus Master ===");
  Serial.printf("Slave ID: %d, Baudrate: %d\n", MODBUS_SLAVE_ID, BAUDRATE);

  setupRS485();

  Serial.println("[MASTER] Setup complete\n");
}

void loop() {
  uint16_t readValues[10];

  Serial.println("\n========== TEST 1: Read Regs 0-4 ==========");
  int n1 = readHoldingRegisters(MODBUS_SLAVE_ID, 0, 5, readValues);
  runStep("T1 FC3 read 0-4", n1 == 5);
  delay(500);

  Serial.println("\n========== TEST 2: Write Regs 0-2 (1111,2222,3333) ==========");
  uint16_t writeValues[3] = {1111, 2222, 3333};
  bool w2 = writeHoldingRegisters(MODBUS_SLAVE_ID, 0, 3, writeValues);
  runStep("T2 FC16 write 0-2", w2);
  delay(500);

  Serial.println("\n========== TEST 3: Read Regs 0-4 (verify write) ==========");
  int n3 = readHoldingRegisters(MODBUS_SLAVE_ID, 0, 5, readValues);
  bool match = (n3 == 5) && readValues[0] == 1111 && readValues[1] == 2222 && readValues[2] == 3333;
  runStep("T3 FC3 verify write", match);
  delay(500);

  Serial.println("\n========== TEST 4: Read Regs 5-9 ==========");
  int n4 = readHoldingRegisters(MODBUS_SLAVE_ID, 5, 5, readValues);
  runStep("T4 FC3 read 5-9", n4 == 5);
  delay(500);

  Serial.println("\n========== TEST 5: Restore Originals ==========");
  uint16_t originalValues[3] = {100, 200, 300};
  bool w5 = writeHoldingRegisters(MODBUS_SLAVE_ID, 0, 3, originalValues);
  runStep("T5 FC16 restore", w5);
  delay(500);

  Serial.printf("\n========== CYCLE SUMMARY: %lu/%lu PASS ==========\n", testsPassed, testsRun);
  Serial.println("Restarting cycle in 3s...\n");
  delay(3000);
}
#endif // ARDUINO
