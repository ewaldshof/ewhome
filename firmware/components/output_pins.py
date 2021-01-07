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
class OutputPins(Component):
    #default, min, max
    inputs = {
        "input":          (0, None, None)
    }

    # overriding init_name prevents creation of an output signal in the netli
    def init_name(self, config):
        self.pin = Component.board.get_pin(self.name)

    def eval(self):
        self.pin(self.input.value >= 0.5)
