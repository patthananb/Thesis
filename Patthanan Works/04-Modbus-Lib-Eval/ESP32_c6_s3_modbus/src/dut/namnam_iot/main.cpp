#ifdef ARDUINO
// DUT: NamNamIoT/ESP32
// Library tested: 4-20ma/ModbusMaster (Doc Walker's classic RTU master lib).
// NamNamIoT's Modbus_RTU.ino example uses this library via their
// Canopus_Modbus.h alias. This sketch mirrors that example but uses plain
// Serial1 instead of their Canopus board-specific aliases.
// Wiring: UART1 RX=GPIO8, TX=GPIO9, 9600 8N1, slave id 1
// Style: plain Arduino sketch (setup/loop, no custom classes)

#include <Arduino.h>
#include <HardwareSerial.h>
#include <ModbusMaster.h>

#define RS485_RX_PIN 8
#define RS485_TX_PIN 9
#define MODBUS_SLAVE_ID 1
#define BAUD 9600

HardwareSerial modbusSerial(1);
ModbusMaster node;

unsigned long testsRun = 0;
unsigned long testsPassed = 0;
unsigned long cycle = 0;

void runStep(const char *label, bool ok, unsigned long us) {
  testsRun++;
  if (ok) testsPassed++;
  Serial.printf(">> %s: %s [us=%lu]\n", label, ok ? "PASS" : "FAIL", us);
}

void setup() {
  Serial.begin(115200);
  delay(2000);
  Serial.println("\n=== DUT: namnam_iot (4-20ma ModbusMaster) ===");
  modbusSerial.begin(BAUD, SERIAL_8N1, RS485_RX_PIN, RS485_TX_PIN);
  node.begin(MODBUS_SLAVE_ID, modbusSerial);
  Serial.println("[DUT] ModbusMaster ready");
}

void loop() {
  cycle++;
  Serial.printf("\n--- Cycle %lu ---\n", cycle);

  unsigned long t0 = micros();
  uint8_t r = node.readHoldingRegisters(0, 5);
  unsigned long us1 = micros() - t0;
  bool t1 = (r == node.ku8MBSuccess);
  uint16_t rv[5] = {0};
  if (t1) {
    for (int i = 0; i < 5; i++) rv[i] = node.getResponseBuffer(i);
    for (int i = 0; i < 5; i++) Serial.printf("  reg[%d]=%u\n", i, rv[i]);
    t1 = rv[0] == 100 && rv[4] == 500;
  } else {
    Serial.printf("  err=0x%02X\n", r);
  }
  runStep("T1 FC3 read 0..4", t1, us1);
  delay(200);

  t0 = micros();
  r = node.writeSingleRegister(0, 4242);
  unsigned long us2 = micros() - t0;
  bool t2 = (r == node.ku8MBSuccess);
  runStep("T2 FC6 write reg 0", t2, us2);
  delay(200);

  t0 = micros();
  r = node.readHoldingRegisters(0, 1);
  unsigned long us3 = micros() - t0;
  bool t3 = (r == node.ku8MBSuccess);
  uint16_t v = 0;
  if (t3) {
    v = node.getResponseBuffer(0);
    Serial.printf("  reg[0]=%u\n", v);
    t3 = (v == 4242);
  }
  runStep("T3 FC3 verify write", t3, us3);
  delay(200);

  node.setTransmitBuffer(0, 100);
  node.setTransmitBuffer(1, 200);
  node.setTransmitBuffer(2, 300);
  t0 = micros();
  r = node.writeMultipleRegisters(0, 3);
  unsigned long us4 = micros() - t0;
  bool t4 = (r == node.ku8MBSuccess);
  runStep("T4 FC16 restore", t4, us4);
  delay(200);

  Serial.printf("CYCLE SUMMARY: %lu/%lu PASS\n", testsPassed, testsRun);
  delay(3000);
}
#endif // ARDUINO
