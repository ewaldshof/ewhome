# publish signals over mqtt
# boards should not subscribe to the topics they export, use local signals instead

from components import Component, Signal
from mqtt import MQTT
from color_text import ColorText as ct
class Exports(Component):
    inputs = {
        "input":        (None, None, None),
        "auto":         (True, None, None), # if set, any change is published immediately. Otherwise wait for strobe
        "strobe":       (0, None, None)     # publish if this signal changes
    }

    # TODO
    # add a mechanism that republishes on mqtt connect

    # overriding init_name prevents creation of an output signal in the netlist
    def init_name(self, config):
        pass

    def first_eval(self):
        MQTT.publish(self.name, self.input.value, True, True )

    def on_input_change(self, signal):
        if  ( signal == self.strobe or
             (signal == self.input and self.auto.value >= 0.5)):  
            MQTT.publish(self.name, self.input.value, True, True )
            
 