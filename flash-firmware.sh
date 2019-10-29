#!/bin/sh
set -e

PORT="${1:-$EWHOME_PORT}"
BIN_FILE="bins/esp32-20190529-v1.11.bin"

if [ "$PORT" = '' ]; then
	noport=1
	usageto=2
fi
case "$PORT" in
	''|-h|--help|/?)
		cat >&"${usageto:-1}" <<-END
			usage: ./flash-firmware.sh [PORT]

			Replace PORT with the serial port path or name where the board can be found.
			It defaults to the value of the EWHOME_PORT environment variable, if set.

			This will flash $BIN_FILE to the board.
END
		exit "${noport:-0}"
		;;
esac


esptool.py --chip esp32 --port "$PORT" erase_flash

esptool.py --chip esp32 --port "$PORT" --baud 460800 write_flash -z 0x1000 "$BIN_FILE"
