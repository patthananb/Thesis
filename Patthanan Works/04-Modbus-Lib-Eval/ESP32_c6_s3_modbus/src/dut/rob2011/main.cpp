#ifdef ARDUINO
// DUT: Rob2011/ESP32.Modbus-TCP-gateway
// Library tested: emelianov/modbus-esp8266 (ModbusRTU master)
// Wiring: UART1 RX=GPIO8, TX=GPIO9, 9600 8N1, slave id 1
// Style: plain Arduino sketch (setup/loop, no custom classes)

#include <Arduino.h>
#include <HardwareSerial.h>
#include <ModbusRTU.h>

#define RS485_RX_PIN 8
#define RS485_TX_PIN 9
#define MODBUS_SLAVE_ID 1
#define BAUD 9600

HardwareSerial modbusSerial(1);
ModbusRTU mb;

unsigned long testsRun = 0;
unsigned long testsPassed = 0;
unsigned long cycle = 0;

// Block until current transaction finishes or timeout.
bool waitForSlave(unsigned long timeoutMs) {
  unsigned long start = millis();
  while (mb.slave()) {
    mb.task();
    if (millis() - start > timeoutMs) return false;
    delay(2);
  }
  return true;
}

void runStep(const char *label, bool ok, unsigned long us) {
  testsRun++;
  if (ok) testsPassed++;
  Serial.printf(">> %s: %s [us=%lu]\n", label, ok ? "PASS" : "FAIL", us);
}

void setup() {
  Serial.begin(115200);
  delay(2000);
  Serial.println("\n=== DUT: rob2011 (emelianov ModbusRTU) ===");

  modbusSerial.begin(BAUD, SERIAL_8N1, RS485_RX_PIN, RS485_TX_PIN);
  mb.begin(&modbusSerial);
  mb.master();
  Serial.println("[DUT] ModbusRTU master ready");
}

void loop() {
  cycle++;
  Serial.printf("\n--- Cycle %lu ---\n", cycle);

  uint16_t readVals[5] = {0};
  Serial.println("T1: FC3 read regs 0..4");
  unsigned long t0 = micros();
  mb.readHreg(MODBUS_SLAVE_ID, 0, readVals, 5);
  bool t1ok = waitForSlave(2000);
  unsigned long us1 = micros() - t0;
  t1ok = t1ok && readVals[0] == 100 && readVals[1] == 200 &&
         readVals[2] == 300 && readVals[3] == 400 && readVals[4] == 500;
  for (int i = 0; i < 5; i++) Serial.printf("  reg[%d]=%u\n", i, readVals[i]);
  runStep("T1 FC3 read 0..4", t1ok, us1);
  delay(200);

  Serial.println("T2: FC6 write reg 0 = 4242");
  t0 = micros();
  mb.writeHreg(MODBUS_SLAVE_ID, 0, (uint16_t)4242);
  bool t2 = waitForSlave(2000);
  unsigned long us2 = micros() - t0;
  runStep("T2 FC6 write reg 0", t2, us2);
  delay(200);

  Serial.println("T3: FC3 read reg 0 (verify)");
  uint16_t verifyVal = 0;
  t0 = micros();
  mb.readHreg(MODBUS_SLAVE_ID, 0, &verifyVal, 1);
  bool t3 = waitForSlave(2000);
  unsigned long us3 = micros() - t0;
  t3 = t3 && verifyVal == 4242;
  Serial.printf("  reg[0]=%u\n", verifyVal);
  runStep("T3 FC3 verify write", t3, us3);
  delay(200);

  Serial.println("T4: FC16 write regs 0..2 = 100,200,300 (restore)");
  uint16_t restoreVals[3] = {100, 200, 300};
  t0 = micros();
  mb.writeHreg(MODBUS_SLAVE_ID, 0, restoreVals, 3);
  bool t4 = waitForSlave(2000);
  unsigned long us4 = micros() - t0;
  runStep("T4 FC16 restore", t4, us4);
  delay(200);

  Serial.printf("CYCLE SUMMARY: %lu/%lu PASS\n", testsPassed, testsRun);
  delay(3000);
}
#endif // ARDUINO
