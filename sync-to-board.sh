#!/bin/sh
set -e

cd firmware

PORT="${1:-$EWHOME_PORT}"

if [ "$PORT" = '' ]; then
	noport=1
	usageto=2
fi
case "$PORT" in
	''|-h|--help|/?)
		cat >&"${usageto:-1}" <<-END
			usage: ./sync-to-board.sh [PORT]

			Replace PORT with the serial port path or name where the board can be found.
			It defaults to the value of the EWHOME_PORT environment variable, if set.

			This upload all files in firmware/ to the board.
END
		exit "${noport:-0}"
		;;
esac


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
