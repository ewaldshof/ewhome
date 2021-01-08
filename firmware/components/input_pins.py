# create an output pin
# values below 0.5 are interpreted as o, other values as 1
#
# pins can be given as pin numbers or as connector names
#
# example usage in yaml:
# output_pins:
#   2-1: 0
#   3-1: temperature > 21
#   34:  window_open and alarm_set

# IDEA: We could make this a multi line component and make the pullup configurable
from machine import Pin
from components import Component, Signal
from color_text import ColorText as ct
class InputPins(Component):

    # create a signal connection for the left hand side of the yaml line
    outputs = {
        "output": (None, None, None)
    }

    #this is the pin name, but the name of the right hand side of a single line components must be "input"
    params = {
        "input": (None, None, None)
    }

    @classmethod
    def init_param(cls, value, component, param_name):
        assert param_name == "input", "the only parameter of an input_pin must be named 'input'"
        try:
            component.pin = Component.board.get_pin(value)
            component.pin.init(mode=Pin.IN)
            component.pin.irq(trigger=Pin.IRQ_RISING|Pin.IRQ_FALLING, handler=lambda p: component.eval())
        except:
            component.pin = None
            self.output.value = 0

    def eval(self):
        if self.pin is not None:
            ct.print_debug("Pin {} input is {}".format(self.name, self.pin.value()))
            self.output.value = bool(self.pin.value())
