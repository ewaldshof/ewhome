#!/bin/sh

export AMPY_DELAY=0.5
export AMPY_PORT=/dev/tty.SLAB_USBtoUART

filelist="heating.py
task.py
drivers/ssd1306.py
drivers/__init__.py
config.py
board/bohei.py
board/__init__.py
board/base.py
boot.py
ewh_net.py
mqtt.py
temperature.py"


echo "Creating directories ..."
for dir in $(find . -type d | cut -c 3-); do
    if [ "$dir" = '' ]; then
        continue
    fi
    echo "  $dir"
    ampy mkdir "$dir" 2>/dev/null
done

echo "Copying files ..."
for file in $(find . -name '*.py' | cut -c 3-); do
#for file in $filelist; do
    echo "  $file"
    ampy put "$file" "$file"
done
