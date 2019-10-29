#!/bin/sh
set -e

usage() {
	cat >&2 <<-END
		usage: ./sync-to-board.sh [-a|-r] [-c] [-w WAIT] [PORT]

		Replace PORT with the serial port path or name where the board can be found.
		It defaults to the value of the EWHOME_PORT environment variable, if set.

		This upload all files in firmware/ to the board.

		Options:

		  -a       Use ampy, even if rshell is available.
		  -c       Clear the board first (i.e., remove all files).
		  -r       Use rshell, even if ampy is available.
		  -w WAIT  Instruct the tool to wait/delay WAIT seconds. This defaults to 1
		           when using ampy, use -w 0 to disable it explicitly.
END
	exit 1

}

tool=''
clean=''
wait=''
while getopts ':acrw:' opt; do
	case "$opt" in
		a)
			tool=ampy
			;;
		r)
			tool=rshell
			;;
		c)
			clean=1
			;;
		w)
			wait="$OPTARG"
			;;
		*)
			usage
			;;
	esac
done
shift $((OPTIND - 1))

# Make sure we have a port.
PORT="${1:-$EWHOME_PORT}"
[ "$PORT" = '' ] && usage

# If there was no tool selected manually, find one.
if [ -z "$tool" ]; then
	if which rshell >/dev/null 2>&1; then
		tool='rshell'
	elif which ampy >/dev/null 2>&1; then
		tool='ampy'
	else
		echo 'Could neither find rshell nor ampy in the PATH, please install one of them!' >&2
		exit 1
	fi
fi
echo "Using $tool."


cd firmware


case "$tool" in
	rshell)
		if [ -n "$clean" ]; then
			echo '-c has not been implemented for rshell yet!' >&2
			exit 1
		fi
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
		;;
	ampy)
		echo
		echo 'WARNING: This is using an ampy directory upload to the root directory.'
		echo '         For this to work, you need ampy > 1.0.7, which is unreleased as of 2019-10-29.'
		echo "         In other words, if no new release is available yet, get ampy's master from GitHub."
		echo
		waitarg="-d ${wait:-1}"
		if [ -n "$clean" ]; then
			echo 'Cleaning existing files ...'
			ampy -p "$PORT" $waitarg rmdir / 2>/dev/null || true # It's okay if this crashes, it can't remove / itself, but will get rid of all children.
			echo
		fi

		echo 'Uploading drivers ...' # I have no idea why, but when I don't upload these first (on my board), ampy breaks down _every_ time.
		ampy -p "$PORT" $waitarg put drivers /drivers
		echo 'Uploading files ...'
		ampy -p "$PORT" $waitarg put . /
		;;
esac
