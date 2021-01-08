# use  mqtt as signals

from components import Component, Signal
from mqtt import MQTT
from color_text import ColorText as ct

class Imports(Component):
    # create a signal connection for the left hand side of the yaml line
    outputs = {
        "output": (None, None, None)
    }

    #this is the topic to subscrube to, but the name of the right hand side of a single line components must be "input"
    params = {
        "input": (None, None, None)
    }

    @classmethod
    def init_param(cls, value, component, param_name):
        assert param_name == "input", "the only parameter of an input_pin must be named 'input'"
        MQTT.subscribe(value, component.callback, True)

    def callback(self, topic, msg):
        self.output.value = msg