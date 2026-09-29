# Project-root CMakeLists.txt used by PlatformIO when framework=espidf.
# Arduino envs ignore this file; only the ESP-IDF envs hit it.
cmake_minimum_required(VERSION 3.16)
list(APPEND EXTRA_COMPONENT_DIRS "${CMAKE_CURRENT_LIST_DIR}/lib/esp-modbus")
include($ENV{IDF_PATH}/tools/cmake/project.cmake)
project(modbus_dut)
