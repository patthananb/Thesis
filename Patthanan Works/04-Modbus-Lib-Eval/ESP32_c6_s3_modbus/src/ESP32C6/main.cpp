#ifdef ARDUINO
#include <Arduino.h>
#include <HardwareSerial.h>

// RS485 Pin Configuration for ESP32-C6 SuperMini
// Auto-direction transceiver (e.g. MAX13487): no DE/RE pins needed.
// SuperMini does NOT expose GPIO 16/17. Avoid strap (8,9,15) and USB (12,13).
#define RS485_RX_PIN 5       // RX pin (to transceiver RO)
#define RS485_TX_PIN 4       // TX pin (to transceiver DI)

// Modbus configuration
#define MODBUS_SLAVE_ID 1
#define BAUDRATE 9600

// Inter-byte silence (>= 3.5 char times) marks Modbus RTU frame end.
// At 9600 8N1: 1 char = 10 bits / 9600 = ~1.042 ms -> 3.5 char ~= 3.65 ms.
#define FRAME_GAP_MS 4

// Holding registers for testing (Modbus holding registers 0-9)
uint16_t holdingRegisters[10] = {100, 200, 300, 400, 500, 600, 700, 800, 900, 1000};

HardwareSerial modbusSerial(1);  // UART1 for ESP32-C6

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
  Serial.println("[SLAVE] RS485 configured (auto-direction transceiver)");
}

// Block until a full Modbus RTU frame is read (terminated by FRAME_GAP_MS silence).
// Returns frame length, 0 if nothing arrived.
int readFrame(uint8_t *buffer, int maxLen) {
  if (!modbusSerial.available()) return 0;

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

void sendResponse(uint8_t *response, int len) {
  // Append CRC
  uint16_t crc = calculateCRC(response, len);
  response[len++] = crc & 0xFF;
  response[len++] = (crc >> 8) & 0xFF;

  modbusSerial.write(response, len);
  modbusSerial.flush();
}

void sendException(uint8_t slaveID, uint8_t fc, uint8_t code) {
  uint8_t resp[5];
  resp[0] = slaveID;
  resp[1] = fc | 0x80;
  resp[2] = code;
  sendResponse(resp, 3);
  Serial.printf("[SLAVE] Sent exception fc=0x%02X code=%d\n", resp[1], code);
}

void handleModbus() {
  uint8_t buffer[256];
  int len = readFrame(buffer, sizeof(buffer));
  if (len == 0) return;

  Serial.printf("[SLAVE] RX %d bytes: ", len);
  for (int i = 0; i < len; i++) Serial.printf("%02X ", buffer[i]);
  Serial.println();

  if (len < 4) {
    Serial.println("[SLAVE] Frame too short, drop");
    return;
  }

  // Verify CRC
  uint16_t rxCrc = buffer[len - 2] | (buffer[len - 1] << 8);
  uint16_t calcCrc = calculateCRC(buffer, len - 2);
  if (rxCrc != calcCrc) {
    Serial.printf("[SLAVE] CRC mismatch rx=%04X calc=%04X, drop\n", rxCrc, calcCrc);
    return;
  }

  uint8_t slaveID = buffer[0];
  uint8_t fc = buffer[1];

  if (slaveID != MODBUS_SLAVE_ID) {
    Serial.printf("[SLAVE] Not for me (id=%d), drop\n", slaveID);
    return;
  }

  // FC3: Read Holding Registers
  if (fc == 3 && len == 8) {
    uint16_t startAddr = (buffer[2] << 8) | buffer[3];
    uint16_t quantity = (buffer[4] << 8) | buffer[5];
    Serial.printf("[SLAVE] FC3 addr=%d qty=%d\n", startAddr, quantity);

    if (quantity == 0 || quantity > 125) {
      sendException(slaveID, fc, 0x03);  // illegal data value
      return;
    }
    if (startAddr + quantity > 10) {
      sendException(slaveID, fc, 0x02);  // illegal data address
      return;
    }

    uint8_t response[256];
    response[0] = slaveID;
    response[1] = fc;
    response[2] = quantity * 2;
    int idx = 3;
    for (int i = 0; i < quantity; i++) {
      response[idx++] = (holdingRegisters[startAddr + i] >> 8) & 0xFF;
      response[idx++] = holdingRegisters[startAddr + i] & 0xFF;
    }
    sendResponse(response, idx);
    Serial.printf("[SLAVE] FC3 reply %d data bytes\n", quantity * 2);
    return;
  }

  // FC6: Write Single Holding Register
  if (fc == 6 && len == 8) {
    uint16_t address = (buffer[2] << 8) | buffer[3];
    uint16_t value = (buffer[4] << 8) | buffer[5];
    Serial.printf("[SLAVE] FC6 addr=%d value=%d\n", address, value);

    if (address >= 10) {
      sendException(slaveID, fc, 0x02);
      return;
    }

    holdingRegisters[address] = value;
    uint8_t response[8];
    memcpy(response, buffer, 6);
    sendResponse(response, 6);
    Serial.println("[SLAVE] FC6 reply sent");
    return;
  }

  // FC16: Write Multiple Holding Registers
  if (fc == 16 && len >= 9) {
    uint16_t startAddr = (buffer[2] << 8) | buffer[3];
    uint16_t quantity = (buffer[4] << 8) | buffer[5];
    uint8_t byteCount = buffer[6];
    Serial.printf("[SLAVE] FC16 addr=%d qty=%d\n", startAddr, quantity);

    if (quantity == 0 || quantity > 123 || byteCount != quantity * 2) {
      sendException(slaveID, fc, 0x03);
      return;
    }
    if (startAddr + quantity > 10) {
      sendException(slaveID, fc, 0x02);
      return;
    }

    for (int i = 0; i < quantity; i++) {
      holdingRegisters[startAddr + i] = (buffer[7 + i * 2] << 8) | buffer[7 + i * 2 + 1];
      Serial.printf("[SLAVE] Reg[%d] = %d\n", startAddr + i, holdingRegisters[startAddr + i]);
    }

    uint8_t response[8];
    response[0] = slaveID;
    response[1] = fc;
    response[2] = (startAddr >> 8) & 0xFF;
    response[3] = startAddr & 0xFF;
    response[4] = (quantity >> 8) & 0xFF;
    response[5] = quantity & 0xFF;
    sendResponse(response, 6);
    Serial.println("[SLAVE] FC16 reply sent");
    return;
  }

  Serial.printf("[SLAVE] Unsupported fc=0x%02X\n", fc);
  sendException(slaveID, fc, 0x01);  // illegal function
}

void setup() {
  Serial.begin(115200);
  delay(2000);

  Serial.println("\n\n=== ESP32-C6 Modbus Slave ===");
  Serial.printf("Slave ID: %d, Baudrate: %d\n", MODBUS_SLAVE_ID, BAUDRATE);

  setupRS485();

  Serial.println("[SLAVE] Ready");
  Serial.println("Holding Registers initial: 100,200,300,400,500,600,700,800,900,1000");
}

void loop() {
  handleModbus();
}
#endif // ARDUINO
