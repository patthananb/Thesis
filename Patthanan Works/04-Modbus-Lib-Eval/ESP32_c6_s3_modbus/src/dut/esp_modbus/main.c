// DUT: espressif/esp-modbus
// Library tested: esp-modbus v2.1.2 (ESP-IDF component, Modbus RTU master)
// Wiring: UART1 RX=GPIO8, TX=GPIO9, 9600 8N1, slave id 1
// Style: plain ESP-IDF C (app_main + while-loop, no custom objects)

#ifdef DUT_ESP_MODBUS

#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/uart.h"
#include "esp_log.h"
#include "esp_err.h"
#include "mbcontroller.h"
#include "esp_timer.h"

#define DUT_UART_PORT   UART_NUM_1
#define DUT_UART_TX     9
#define DUT_UART_RX     8
#define DUT_SLAVE_ID    1
#define DUT_BAUD        9600

static const char *TAG = "DUT_ESP_MODBUS";

static void *master_handle = NULL;
static unsigned long testsRun = 0;
static unsigned long testsPassed = 0;
static unsigned long cycle = 0;

static void run_step(const char *label, bool ok, uint64_t us) {
    testsRun++;
    if (ok) testsPassed++;
    ESP_LOGI(TAG, ">> %s: %s [us=%llu]", label, ok ? "PASS" : "FAIL", us);
}

static bool fc_request(uint8_t cmd, uint16_t addr, uint16_t qty, void *buf) {
    mb_param_request_t req = {
        .slave_addr = DUT_SLAVE_ID,
        .command    = cmd,
        .reg_start  = addr,
        .reg_size   = qty,
    };
    esp_err_t err = mbc_master_send_request(master_handle, &req, buf);
    if (err != ESP_OK) {
        ESP_LOGW(TAG, "send_request cmd=0x%02X err=0x%x", cmd, err);
        return false;
    }
    return true;
}

void app_main(void) {
    ESP_LOGI(TAG, "=== DUT: esp-modbus (ESP-IDF master) ===");

    mb_communication_info_t comm = {0};
    comm.ser_opts.mode             = MB_RTU;
    comm.ser_opts.port             = DUT_UART_PORT;
    comm.ser_opts.baudrate         = DUT_BAUD;
    comm.ser_opts.data_bits        = UART_DATA_8_BITS;
    comm.ser_opts.stop_bits        = UART_STOP_BITS_1;
    comm.ser_opts.parity           = UART_PARITY_DISABLE;
    comm.ser_opts.response_tout_ms = 1000;

    ESP_ERROR_CHECK(mbc_master_create_serial(&comm, &master_handle));
    ESP_ERROR_CHECK(uart_set_pin(DUT_UART_PORT, DUT_UART_TX, DUT_UART_RX,
                                 UART_PIN_NO_CHANGE, UART_PIN_NO_CHANGE));
    ESP_ERROR_CHECK(mbc_master_start(master_handle));
    ESP_LOGI(TAG, "esp-modbus master started");

    while (1) {
        cycle++;
        ESP_LOGI(TAG, "--- Cycle %lu ---", cycle);

        uint16_t rv[5] = {0};
        int64_t t0 = esp_timer_get_time();
        bool t1 = fc_request(0x03, 0, 5, rv);
        uint64_t us1 = (uint64_t)(esp_timer_get_time() - t0);
        if (t1) {
            for (int i = 0; i < 5; i++) ESP_LOGI(TAG, "  reg[%d]=%u", i, rv[i]);
            t1 = (rv[0] == 100 && rv[4] == 500);
        }
        run_step("T1 FC3 read 0..4", t1, us1);
        vTaskDelay(pdMS_TO_TICKS(200));

        uint16_t writeVal = 4242;
        t0 = esp_timer_get_time();
        bool t2 = fc_request(0x06, 0, 1, &writeVal);
        uint64_t us2 = (uint64_t)(esp_timer_get_time() - t0);
        run_step("T2 FC6 write reg 0", t2, us2);
        vTaskDelay(pdMS_TO_TICKS(200));

        uint16_t v = 0;
        t0 = esp_timer_get_time();
        bool t3 = fc_request(0x03, 0, 1, &v);
        uint64_t us3 = (uint64_t)(esp_timer_get_time() - t0);
        if (t3) {
            ESP_LOGI(TAG, "  reg[0]=%u", v);
            t3 = (v == 4242);
        }
        run_step("T3 FC3 verify write", t3, us3);
        vTaskDelay(pdMS_TO_TICKS(200));

        uint16_t restore[3] = {100, 200, 300};
        t0 = esp_timer_get_time();
        bool t4 = fc_request(0x10, 0, 3, restore);
        uint64_t us4 = (uint64_t)(esp_timer_get_time() - t0);
        run_step("T4 FC16 restore", t4, us4);
        vTaskDelay(pdMS_TO_TICKS(200));

        ESP_LOGI(TAG, "CYCLE SUMMARY: %lu/%lu PASS", testsPassed, testsRun);
        vTaskDelay(pdMS_TO_TICKS(3000));
    }
}

#endif // DUT_ESP_MODBUS
