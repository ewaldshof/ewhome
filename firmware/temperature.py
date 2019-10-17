from ds18x20 import DS18X20
from onewire import OneWire
from task import Task
import time
from ubinascii import hexlify
import ujson

class Temperature(Task):

    def __init__(self, pin, interval_s=10):
        super().__init__()
        self.pin = pin
        self.interval_s = max(interval_s, 2) # no faster than 2s
        self.converting = False
        self.mqtt = None
        self.ds = DS18X20(OneWire(pin))
        self.sensors = list(map(Sensor, self.ds.scan()))
        self.interval = self.countdown = 1000 * self.interval_s

    def update(self, scheduler):
        if self.converting:
            # We've waited enough for the sensor(s). Read the temperatures.
            for sensor in self.sensors:
                try:
                    sensor.temperature = self.ds.read_temp(sensor.address)
                    if self.mqtt:
                        self.mqtt.publish(
                            "ewhome/ds18x20/" + sensor.hex_address,
                            str(sensor),
                            retain=True,
                        )
                except:
                    # Ignore things like CRC errors.
                    pass
            # Print the results.
            for sensor in self.sensors:
                print(sensor)
            # Reset our update interval to the configured one.
            self.interval = self.countdown = 1000 * self.interval_s
        else:
            # Request the temperature conversion.
            self.ds.convert_temp()
            # Ask for the results in 750ms or more (required by the sensors).
            self.interval = self.countdown = 750
        # Flip the "converting" flag.
        self.converting = not self.converting

class Sensor:

    def __init__(self, address):
        self.address = address
        self.hex_address = hexlify(self.address).decode("utf-8")
        self.pretty_address = hexlify(self.address, ":").decode("utf-8")
        self.temperature = None

    def __str__(self):
        return ujson.dumps({
            "id": self.hex_address,
            "address": self.pretty_address,
            "temperature_c": self.temperature,
        })
