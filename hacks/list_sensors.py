# list_sensors.py

import machine
from onewire import OneWire
from ds18x20 import DS18X20
from ubinascii import hexlify

pin = machine.Pin(0)
ds = DS18X20(OneWire(pin))
addresses = ds.scan()
for address in addresses:
    print(hexlify(address).decode("utf-8"))
