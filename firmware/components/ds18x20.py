from components import Component, Signal
from task import Task, CallbackTask

from ds18x20 import DS18X20
from onewire import OneWire
import time
from ubinascii import hexlify
from color_text import ColorText as ct 

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

class Ds18x20(Component, Task):
    inputs = {
        "period":   (60, 0.1, 60*60*24)
    }

    # overriding init_name prevents creation of an output signal in the netlist
    # instead we use that as pin name
    def init_name(self, config):
        self.pin = Component.board.get_pin(self.name)
        self.ds = DS18X20(OneWire(self.pin))
        addresses = self.ds.scan()
        self.sensors = set()
        for address in addresses:
            self.sensors.add(Sensor(address, self, config))
        ct.print_info("Found {} DS18x20 sensors.".format(len(self.sensors)))
        ct.print_debug("\n".join(str(x) for x in self.sensors))


    #during post_init the config contains only sensor ids
    def post_init(self, config):
        self.readout_task = CallbackTask(self.readout, 750)
        self.interval = self.countdown = self.period.value * 1000
        if len(self.sensors) > 0:
            Component.scheduler.register(self)
        
    def update(self, scheduler):
        self.interval = self.countdown = self.period.value * 1000

        # Ask for the results in 750ms or more (required by the sensors).
        self.readout_task.countdown =750
        scheduler.register(self.readout_task)
        # Request the temperature conversion.
        self.ds.convert_temp()
        ct.print_debug("converting temperatures")


    def readout(self):
        ct.print_debug("reading temperatures from pin {}".format(self.name))

        # We've waited enough for the sensor(s). Read the temperatures.
        for sensor in self.sensors:
            sensor.read_temp(self.ds)

class Sensor:
    def __init__(self, address, component, mappings={}):
        self.address = address
         # get n´signal name from info or create a generic name if sensor is not configured
        signal_name = mappings.pop(self.hex_address(), "ds18x20/{}".format(self.hex_address()))
        ct.print_debug("mapped sensor {} to {}".format(self.hex_address(), signal_name))
        self.signal = Signal.get_by_name(signal_name, component)

    def read_temp(self, ds):
        ct.print_debug("reading temperatures from {} for {}".format(self.hex_address(), self.signal.name))
        try:
            temperature = ds.read_temp(self.address)
            self.signal.value = round(temperature,2)
        except Exception as e:
            ct.format_exception(e, "Exception in ds18x20 update for {}".format(self.signal.name))        


    def hex_address(self):
        return hexlify(self.address).decode("utf-8") 

    def __str__(self):
            return "{} = temperature[{}]".format(self.signal.name, self.hex_address())
