from ds18x20 import DS18X20
from onewire import OneWire
from task import Task
import time
from ubinascii import hexlify
import ujson

class Temperature(Task):

    def __init__(self, pin, mqtt, interval_s=10):
        super().__init__()
        self.names = {}
        self.pin = pin
        self.interval_s = max(interval_s, 2) # no faster than 2s
        self.converting = False
        self.mqtt = mqtt
        self.ds = DS18X20(OneWire(pin))
        self.sensors = list(map(Sensor, self.ds.scan()))
        print("Found {0} DS18x20 sensors.".format(len(self.sensors)))
        self.interval = self.countdown = 1000 * self.interval_s

    def _on_config_update(self, config):
        self.names = config.data.get("ds18x20", {})

    def update(self, scheduler):
        if self.converting:
            # We've waited enough for the sensor(s). Read the temperatures.
            for sensor in self.sensors:
                try:
                    sensor.temperature = self.ds.read_temp(sensor.address)
                    sensor_data = sensor.get_data()
                    self.mqtt.publish(
                        "ds18x20/" + sensor.hex_address,
                        sensor.get_data(),
                        retain=True,
                    )
                    if sensor_data["id"] in self.names:
                        self.mqtt.publish(
                            self.names[sensor_data["id"]],
                            sensor_data["temperature_c"],
                            retain=True
                        )
                except:
                    # Ignore things like CRC errors.
                    pass
            # Reset our update interval to the configured one, minus convert time.
            self.interval = self.countdown = 1000 * self.interval_s - 750
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

    def get_data(self):
        return {
            "id": self.hex_address,
            "address": self.pretty_address,
            "temperature_c": self.temperature,
        }

    def __str__(self):
        return ujson.dumps(self.get_data())
