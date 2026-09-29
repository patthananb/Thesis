idf_component_register(
    SRCS "dut/esp_modbus/main.c"
         "dut/maxx_ukoo/main.c"
    INCLUDE_DIRS "."
    REQUIRES driver esp-modbus
)
