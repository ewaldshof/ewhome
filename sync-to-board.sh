#!/bin/sh
set -e

cd firmware

#set -x

PORT=${1:-"/dev/tty.SLAB_USBtoUART"}

QUIET="--quiet"

echo "Creating directories ..."
for dir in $(find . -type d | cut -c 3-); do
	if [ "$dir" = '' ]; then
		continue
	fi
	echo "  $dir"
	rshell $QUIET --port $PORT cp -r "$dir" "/pyboard/" && {
		echo "Done."
	} || {
		echo "rshell failed!"
		exit 1
	}
done

echo "Copying files ..."
echo "  *.py files"
rshell $QUIET --port $PORT cp "*.py" "/pyboard/" && {
	echo "Done."
} || {
	echo "rshell failed!"
	exit 1
}
