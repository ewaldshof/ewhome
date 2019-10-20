#!/bin/sh

PORT=${1:-"/dev/tty.SLAB_USBtoUART"}
export BIN_FILE="../bins/esp32-20190529-v1.11.bin"

esptool.py --chip esp32 --port $PORT erase_flash

esptool.py --chip esp32 --port $PORT --baud 460800 write_flash -z 0x1000 $BIN_FILE
