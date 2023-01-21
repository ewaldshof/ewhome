# list_sensors.py

import machine
from onewire import OneWire
from ds18x20 import DS18X20

pin = machine.Pin(0)
ds = DS18X20(OneWire(pin))
roms = ds.scan()
for rom im roms:
    print(rom)