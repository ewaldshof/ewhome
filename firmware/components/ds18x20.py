from components import Component, Signal
from task import Task

from ds18x20 import DS18X20
from onewire import OneWire, OneWireError
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
            start_conversion:  minutes   # from time component
            conversion_finished:         # changes after temperatures are read, about 800ms afer conversion was startet
            28ff3482b0160315:   1st_sensor_pin_2_1
            28fff97c90170532:   2nd_sensor_pin_2_1
        1-5:
            28ff1282b0160315:   only_sensor_pin_1_5
"""

class Ds18x20(Component, Task):
    inputs = {
        "start_conversion":   (None, None, None),
    }
    outputs = {
        "stable":              (None, None, None), # False during conversion, True otherwise
        "ids":                 (None, None, None), # list of all IDs
        "temperatures":        (None, None, None)  # list of all temperatures 
    }


    # overriding init_name prevents creation of an output signal in the netlist
    # instead we use that as pin name
    def init_name(self, config):
        self.pin = Component.board.get_pin(self.name)
        self.ds = DS18X20(OneWire(self.pin))
        addresses = self.ds.scan()
        self.sensors = []

        read_all_sensors = ("ids" in config) or ("temperatures" in config)

        for address in addresses:
            hex_address = Sensor.to_hex_address(address)
            signal_name = None

            if  hex_address in config:
                sensor = Sensor(address, self, config.pop(hex_address))
                self.sensors.append(sensor)         
            elif read_all_sensors:
                sensor = Sensor(address, self, None)
                self.sensors.append(sensor)
            
        ct.print_info("Found {} DS18x20 sensors.".format(len(self.sensors)))
        ct.print_debug("\n".join(str(x) for x in self.sensors))
        self.countdown = self.interval = -1


    def first_eval(self):
        self.stable.value = False        
        self.ids.value = [s.hex_address() for s in self.sensors]
        self.ids.notify_fanouts()
        
    def on_input_change(self, signal):
        if signal == self.start_conversion and self.countdown <= 0:
            self.countdown = 750
            self.interval = -1
            Component.scheduler.register(self)
            self.stable.value = False
            try:
                self.ds.convert_temp()
            except OneWireError:
                ct.print_debug("OneWireError in convert_temp ...")
            ct.print_debug("converting temperatures")

    def update(self, scheduler):
        ct.print_debug("reading temperatures from pin {}".format(self.name))
        # We've waited enough for the sensor(s). Read the temperatures.      
        self.temperatures.value = [s.read_temp(self.ds) for s in self.sensors]
        self.stable.value = True
        self.temperatures.notify_fanouts()
        
        


class Sensor:
    @classmethod
    def to_hex_address(cls, address):
        return  hexlify(address).decode("utf-8") 

    def __init__(self, address, component, signal_name):
        self.address = address
        if signal_name is None:
            signal_name = "t_{}".format(self.hex_address())
        ct.print_debug("mapped sensor {} to {}".format(self.hex_address(), signal_name))
        self.signal = Signal.get_by_name(signal_name, component)

    
    def read_temp(self, ds):
        ct.print_debug("reading temperatures from {} for {}".format(self.hex_address(), self.signal.name))
        temperature = -272.0
        try:
            temperature = ds.read_temp(self.address)
            if self.signal is not None:
                self.signal.value = round(temperature,2)
        except Exception as e:
            ct.format_exception(e, "Exception in ds18x20 update for {}".format(self.signal.name))        
        return temperature

    def hex_address(self):
        return Sensor.to_hex_address(self.address)

    def __str__(self):
            return "{} = temperature[{}]".format(self.signal.value, self.hex_address())
