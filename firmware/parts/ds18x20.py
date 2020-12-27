from parts import FixedPeriodPart, Part

from ds18x20 import DS18X20
from onewire import OneWire
import time
from ubinascii import hexlify
import ujson


# one wire temperature sensor. One instance per 1-wire-bus with one line per ID
# eg:
# the update period can be specified in a seperate line in seconds.
# It defaults to 60s

"""
    ds18x20:
        2-1:
            period:             10
            28ff3482b0160315:   1st_sensor_pin_2_1
            28fff97c90170532:   2nd_sensor_pin_2_1
        1-5:
            28ff1282b0160315:   only_sensor_pin_1_5
"""

class Ds18x20(FixedPeriodPart):
    def __init__(self, key, content):
        self.temperature = None
        self.converting = False
        self.name = key
        self.pin = Part.board.get_pin(self.name)
        print("temperature pin", self.pin)
        self.ds = DS18X20(OneWire(self.pin))
    	
        addresses = self.ds.scan()
        
        self.sensors = set()
        for address in addresses:
            print(address)
            self.sensors.add(Sensor(address, content))
        print("Found {0} DS18x20 sensors.".format(len(self.sensors)))
        print(self.sensors)

        # this removes "period" from the dictionary if it exists, therefore it should be run before counting the elements
        # at the same time it should be run as late as possible
        self.schedule_period_from_dict(content, 60, 2)
        if len(content) > 0:
            print("configured sensors that are not connceted:\n", content)
 

    def update(self, scheduler):
        if self.converting:
            print("reading temperatures")
            # We've waited enough for the sensor(s). Read the temperatures.
            for sensor in self.sensors:
                print("reading temperature from", sensor.hex_address(), "for", sensor.topic)
                try:
                    temperature = self.ds.read_temp(sensor.address)
                    print("publishing temperature=", temperature)
                    Part.mqtt.publish(sensor.topic, temperature, retain=True)
                except Exception as e:
                    Part.print_exception(e, "Exception in ds18x20 update")
                    pass
            # Reset our update interval to the configured one, minus convert time.
            self.interval = self.countdown = 1000 * self.period - 750
        else:
            print("converting temperatures")
            # Request the temperature conversion.
            self.ds.convert_temp()
            # Ask for the results in 750ms or more (required by the sensors).
            self.interval = self.countdown = 750
        # Flip the "converting" flag.
        self.converting = not self.converting

class Sensor:
    def __init__(self, address, mappings={}):
        self.address = address
         # get topic from info or create a generic topic if sensor is not configured
        self.topic = mappings.pop(self.hex_address(), "ds18x20/{}".format(self.hex_address()))
        print("mapped sensor", self.hex_address(), "to topic", self.topic)

    def hex_address(self):
        return hexlify(self.address).decode("utf-8") 