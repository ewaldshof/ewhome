#!/bin/sh

# Erase board
pipenv run erase-flash

# Flash firmware
pipenv run flash-micropython

# Transfer code
pipenv run sync-code
