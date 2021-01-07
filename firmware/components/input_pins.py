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

from components import Component, Signal
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
        component.pin = Component.board.get_pin(value)


    def eval(self):
        self.output.value = bool(self.pin)
