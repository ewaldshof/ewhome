#!/bin/sh

export AMPY_DELAY=0.5
#export AMPY_PORT=/dev/tty.SLAB_USBtoUART
export AMPY_PORT=COM4
#export BIN_FILE="../bins/esp32-20191011-v1.11-422-g98c2eabaf.bin"
export BIN_FILE="../bins/esp32-20190529-v1.11.bin"

esptool.py --chip esp32 --port $AMPY_PORT erase_flash

esptool.py --chip esp32 --port $AMPY_PORT --baud 460800 write_flash -z 0x1000 $BIN_FILE
