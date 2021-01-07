# proportional: # outputs value in range [0.0:1.0]
# creates a linear ramp with width "spread" centered around "midpoint"
# 0.0 if sensor <= (midpoint - spread/2)
# 1.0 if sensor >= (midpoint + spread/2)
# useful for pid controllers
# Example configuration:
#
#   A1_1_heating:
#     sensor: A1_1_luft
#     midpoint: 21 #in °C
#     spread: 2
#     interval: 60
#
# this is equivalten to:
# assign:
#     A1_1_heating: min(1.0, max(0.0, 0.5 + (21-A1_1_luft)/2))

from components import Component, Signal
class Proportional(Component):
    #default, min, max
    inputs = {
        "sensor":   (None, None, None),
        "midpoint": (0, None, None),
        "spread":   (1, 0, None)
    }

    outputs = {
        "output":   (None, None, None)
    }

    def eval(self):
        print(str(self))
        diff = self.midpoint.value - self.sensor.value
        result = 0.5 + (diff / self.spread.value)
        self.output.value = min(1.0, max(0.0, result))
