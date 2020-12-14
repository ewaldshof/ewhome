#!/bin/sh
set -e

# Make sure we're running from the right directory.
[ -e build.sh -a -d firmware -a -d config ] || {
	echo 'This script has to run from the top level of the repository.' >&2
	exit 1
}

usage() {
	cat <<-"END"
		Usage: ./build.sh [-hcdMorS] [-i NUM]

		  -c  Clear all files (including configs!) from board before deploy.
		  -d  Run a deployment using `rshell rsync` after building.
		  -h  Display this help message.
		  -M  Disable module precompilation (i.e. mpy-cross).
		  -o  Optimize bytecode size by removing asserts and line numbers.
		      Should probably be used with -c, else the files won't be
		      updated with their optimized versions.
		  -r  At the end, open a REPL to the board.
		  -S  Skip updating the Git submodules.
	END
}

# Read options.
clear=n
deploy=n
id=''
optimize=0
repl=n
update_submodules=y
mpy_cross=y
while getopts ':cdhMorS' arg; do
	case "$arg" in
		c)
			clear=y
			;;
		d)
			deploy=y
			;;
		h)
			usage
			exit
			;;
		M)
			mpy_cross=n
			;;
		o)
			optimize=3
			;;
		r)
			repl=y
			;;
		S)
			update_submodules=n
			;;
		:)
			printf 'Argument required for -%s\n\n' "$OPTARG" >&2
			usage >&2
			exit 1
			;;
		'?')
			printf 'Invalid option: -%s\n\n' "$OPTARG" >&2
			usage >&2
			exit 1
			;;
	esac
done

if [ "$update_submodules" = 'y' ]; then
	# Make sure the submodules are there.
	git submodule update --init
else
	echo 'Skipping submodule update as requested.'
fi

# Make sure there is a main.py.
[ -e firmware/boot.py ] || {
	echo 'Please create a main.py first. See "Configuring your ESP board" in the readme.' >&2
	exit 1
}

my_rsync() {
	rsync -av --delete-excluded --exclude __pycache__ --exclude wlan.json.example "$@"
}

# Get the contents of the "firmware" directory (and only these).
my_rsync --del firmware/ deploy

# Precompile using mpy-cross, if available.
if [ "$mpy_cross" = 'n' ]; then
	echo 'Skipping precompilation as requested.'
elif ! command -v mpy-cross >/dev/null 2>&1; then
	echo 'mpy-cross is not available, will not precompile!' >&2
else
	echo 'Precompiling ...'
	cd deploy
	find . -name '*.py' | while read -r file; do
		file="${file##./}"  # remove "./" prefix, if present
		# Don't precompile boot.py/main.py, else they won't run.
		if [ "$file" != 'boot.py' -a "$file" != 'main.py' ]; then
			# xtensawin is apparently the arch our uPy version is using.
			# See <https://docs.micropython.org/en/latest/reference/mpyfiles.html>
			mpy-cross -march=xtensawin "-O$optimize" "$file"
			# Set mod time to original file to avoid re-syncing.
			touch -r "$file" "${file%.py}.mpy"
			# Remove it and thus only deploy the generated file.
			rm "$file"
		fi
	done
	cd - >/dev/null
	echo '... done.'
fi

# Build an rshell command line in order to only call it once.
rshell_cmd=''
# If asked to, clear the board.
[ "$clear" = 'y' ] && rshell_cmd='rm -r /pyboard/*'
# If asked to, run a deployment.
if [ "$deploy" = 'y' ]; then
	[ -n "$rshell_cmd" ] && rshell_cmd="$rshell_cmd ; "
	rshell_cmd="${rshell_cmd}rsync -m deploy /pyboard"
fi
# If asked to, connect to REPL.
if [ "$repl" = 'y' ]; then
	[ -n "$rshell_cmd" ] && rshell_cmd="$rshell_cmd ; "
	rshell_cmd="${rshell_cmd}repl"
fi

# Run rshell commands, if we have any.
[ -n "$rshell_cmd" ] && rshell $rshell_cmd
