#ifdef ARDUINO
// DUT: eModbus/eModbus
// Library tested: eModbus (ModbusClientRTU master) — pure library use,
// modeled on the upstream examples/RTU04example/main.cpp.
// Wiring: UART1 RX=GPIO8, TX=GPIO9, 9600 8N1, slave id 1
// Style: plain Arduino sketch (setup/loop, no custom classes)

#include <Arduino.h>
#include <HardwareSerial.h>
#include "ModbusClientRTU.h"

#define RS485_RX_PIN 8
#define RS485_TX_PIN 9
#define MODBUS_SLAVE_ID 1
#define BAUD 9600

HardwareSerial modbusSerial(1);
ModbusClientRTU mb;

volatile bool responseReady = false;
volatile bool responseError = false;
ModbusMessage lastResponse;
uint32_t nextToken = 1;

unsigned long testsRun = 0;
unsigned long testsPassed = 0;
unsigned long cycle = 0;

void onData(ModbusMessage response, uint32_t token) {
  lastResponse = response;
  responseError = false;
  responseReady = true;
}

void onError(Error err, uint32_t token) {
  responseError = true;
  responseReady = true;
}

bool waitResponse(unsigned long timeoutMs) {
  unsigned long start = millis();
  while (!responseReady) {
    if (millis() - start > timeoutMs) return false;
    delay(2);
  }
  return !responseError;
}

void runStep(const char *label, bool ok, unsigned long us) {
  testsRun++;
  if (ok) testsPassed++;
  Serial.printf(">> %s: %s [us=%lu]\n", label, ok ? "PASS" : "FAIL", us);
}

void setup() {
  Serial.begin(115200);
  delay(2000);
  Serial.println("\n=== DUT: eModbus (ModbusClientRTU) ===");

  RTUutils::prepareHardwareSerial(modbusSerial);
  modbusSerial.begin(BAUD, SERIAL_8N1, RS485_RX_PIN, RS485_TX_PIN);

  mb.onDataHandler(&onData);
  mb.onErrorHandler(&onError);
  mb.setTimeout(2000);
  mb.begin(modbusSerial);
  Serial.println("[DUT] eModbus client started");
}

void loop() {
  cycle++;
  Serial.printf("\n--- Cycle %lu ---\n", cycle);

  responseReady = false;
  unsigned long t0 = micros();
  mb.addRequest(nextToken++, MODBUS_SLAVE_ID, READ_HOLD_REGISTER, 0, 5);
  bool t1 = waitResponse(2000);
  unsigned long us1 = micros() - t0;
  uint16_t rv[5] = {0};
  if (t1) {
    for (int i = 0; i < 5; i++) lastResponse.get(3 + i * 2, rv[i]);
    for (int i = 0; i < 5; i++) Serial.printf("  reg[%d]=%u\n", i, rv[i]);
    t1 = rv[0] == 100 && rv[4] == 500;
  }
  runStep("T1 FC3 read 0..4", t1, us1);
  delay(200);

  responseReady = false;
  t0 = micros();
  mb.addRequest(nextToken++, MODBUS_SLAVE_ID, WRITE_HOLD_REGISTER, (uint16_t)0, (uint16_t)4242);
  bool t2 = waitResponse(2000);
  unsigned long us2 = micros() - t0;
  runStep("T2 FC6 write reg 0", t2, us2);
  delay(200);

  responseReady = false;
  t0 = micros();
  mb.addRequest(nextToken++, MODBUS_SLAVE_ID, READ_HOLD_REGISTER, 0, 1);
  bool t3 = waitResponse(2000);
  unsigned long us3 = micros() - t0;
  uint16_t v = 0;
  if (t3) {
    lastResponse.get(3, v);
    Serial.printf("  reg[0]=%u\n", v);
    t3 = v == 4242;
  }
  runStep("T3 FC3 verify write", t3, us3);
  delay(200);

  responseReady = false;
  uint16_t restore[3] = {100, 200, 300};
  t0 = micros();
  mb.addRequest(nextToken++, MODBUS_SLAVE_ID, WRITE_MULT_REGISTERS,
                (uint16_t)0, (uint16_t)3, (uint8_t)6, restore);
  bool t4 = waitResponse(2000);
  unsigned long us4 = micros() - t0;
  runStep("T4 FC16 restore", t4, us4);
  delay(200);

  Serial.printf("CYCLE SUMMARY: %lu/%lu PASS\n", testsPassed, testsRun);
  delay(3000);
}
#endif // ARDUINO
