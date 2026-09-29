/*
 * ╔═══════════════════════════════════════════════════════════╗
 * ║  ESP32-C6 — Modbus TCP Master                            ║
 * ║  Reads temperature & humidity from ESP32-S3 TCP Slave     ║
 * ╚═══════════════════════════════════════════════════════════╝
 *
 * Architecture:
 *   [ESP32-C6 TCP Master] --WiFi/TCP--> [ESP32-S3 TCP Slave :502]
 *
 * This device:
 *   1. Connects to the same WiFi network as the ESP32-S3
 *   2. Polls the ESP32-S3 TCP slave every 3 seconds
 *   3. Reads holding registers 0..3 via FC03
 *   4. Prints temperature, humidity, status, and poll count
 *
 * ESP32-S3 Slave Holding Register Map (FC03, 0-based):
 *   HREG 0: Temperature (raw × 0.1 °C)
 *   HREG 1: Humidity    (raw × 0.1 %RH)
 *   HREG 2: Status      (0=OK, 1=timeout, 2=CRC, 3=exception)
 *   HREG 3: Poll count
 *
 * Library: "modbus-esp8266" by emelianov (install via Library Manager)
 *   Arduino IDE → Sketch → Include Library → Manage Libraries
 *   Search: "modbus-esp8266" → Install
 *
 * Board Settings:
 *   Board:       "ESP32C6 Dev Module"
 *   USB CDC:     "Enabled"
 */

#include <WiFi.h>
#include <ModbusIP_ESP8266.h>

/* ─── WiFi Configuration ─── */
const char* WIFI_SSID = "YOUR_SSID";       /* Same network as ESP32-S3 */
const char* WIFI_PASS = "YOUR_PASSWORD";

/* ─── ESP32-S3 Slave IP ─── */
/*
 * Set this to the IP address printed by the ESP32-S3 on boot.
 * Or use a static IP on the slave side for reliability.
 */
IPAddress slaveIP(192, 168, 1, 100);  /* ← CHANGE to your ESP32-S3 IP */

/* ─── Modbus TCP Parameters ─── */
#define SLAVE_PORT      502
#define SLAVE_ID        1       /* Unit ID (usually 1 for simple slaves) */
#define HREG_START      0       /* First holding register to read */
#define HREG_COUNT      4       /* Read 4 registers: temp, humi, status, count */

/* ─── Timing ─── */
#define POLL_INTERVAL_MS  3000

/* ─── Objects ─── */
ModbusIP mb;

/* ─── Callback: called when response arrives ─── */
/*
 * The modbus-esp8266 library uses a transactional model:
 *   1. You call mb.readHreg() which returns a transaction ID
 *   2. The library sends the TCP request in the background
 *   3. mb.task() processes the response
 *   4. After mb.isTransaction() returns false, data is ready
 *
 * The library writes response data directly into the result[]
 * array you pass to readHreg().
 */

uint16_t result[HREG_COUNT] = {0};
bool     dataReady = false;
uint16_t transID   = 0;

/* ─── Setup ─── */
void setup() {
    Serial.begin(115200);
    while (!Serial) delay(10);

    Serial.println();
    Serial.println("╔═══════════════════════════════════════════╗");
    Serial.println("║  ESP32-C6 — Modbus TCP Master             ║");
    Serial.println("║  Reads from ESP32-S3 TCP Slave (:502)     ║");
    Serial.println("╚═══════════════════════════════════════════╝");

    /* WiFi */
    WiFi.begin(WIFI_SSID, WIFI_PASS);
    Serial.printf("Connecting to WiFi '%s'", WIFI_SSID);
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.printf("\nWiFi connected! IP: %s\n", WiFi.localIP().toString().c_str());
    Serial.printf("Target slave: %s:%d\n\n", slaveIP.toString().c_str(), SLAVE_PORT);

    /* Modbus TCP Master — connect to slave */
    mb.client();
}

/* ─── Main Loop ─── */
unsigned long lastPoll = 0;
bool     waitingResp = false;
uint32_t okCount     = 0;
uint32_t errCount    = 0;

void loop() {
    /* Service Modbus stack */
    mb.task();

    /* Check if previous transaction completed */
    if (waitingResp && !mb.isTransaction(transID)) {
        waitingResp = false;

        /* Data is now in result[] array */
        int16_t  tempRaw   = (int16_t)result[0];
        uint16_t humiRaw   = result[1];
        uint16_t status    = result[2];
        uint16_t pollCount = result[3];

        if (status == 0) {
            okCount++;
            Serial.println("┌──────────────────────────────────────┐");
            Serial.printf("│  Temperature: %7.1f °C              │\n", tempRaw / 10.0);
            Serial.printf("│  Humidity:    %7.1f %%RH             │\n", humiRaw / 10.0);
            Serial.printf("│  Slave polls: %-5u  Status: OK      │\n", pollCount);
            Serial.printf("│  [Master OK: %lu  ERR: %lu]           │\n", okCount, errCount);
            Serial.println("└──────────────────────────────────────┘\n");
        } else {
            errCount++;
            Serial.printf("[WARN] Slave reports sensor error (status=%u)\n\n", status);
        }
    }

    /* Send new request at interval */
    if (!waitingResp && (millis() - lastPoll >= POLL_INTERVAL_MS)) {
        lastPoll = millis();

        if (!mb.isConnected(slaveIP)) {
            mb.connect(slaveIP, SLAVE_PORT);
            Serial.printf("Connecting to slave %s:%d...\n",
                          slaveIP.toString().c_str(), SLAVE_PORT);
        }

        /*
         * readHreg(IP, start_reg, result_array, count)
         *
         * Sends FC03 (Read Holding Registers) to the slave.
         * Response data is written directly into result[].
         * Returns a transaction ID to track completion.
         */
        transID = mb.readHreg(slaveIP, HREG_START, result, HREG_COUNT);

        if (transID) {
            waitingResp = true;
        } else {
            errCount++;
            Serial.println("[ERR] Failed to send Modbus request\n");
        }
    }
}
