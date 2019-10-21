#!/bin/bash

#set -x

PORT=${1:-"/dev/tty.SLAB_USBtoUART"}

cd firmware

./fw_flash.sh "$PORT"

./sync-to-board.sh "$PORT"

cd ..

rshell --port "$PORT" repl
