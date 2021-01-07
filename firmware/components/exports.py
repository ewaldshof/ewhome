# publish signals over mqtt
# boards should not subscribe to the topics they export, use local signals instead

from components import Component, Signal
from mqtt import MQTT
from color_text import ColorText as ct
class Exports(Component):
    inputs = {
        "input":          (None, None, None)
    }

    # TODO
    # add a mechanism that republishes on mqtt connect

    # overriding init_name prevents creation of an output signal in the netlist
    def init_name(self, config):
        pass

    def eval(self):
        MQTT.publish(self.name, self.input.value, True, True )
        #MQTT.client.publish(self.name, str(self.input.value), True)
 