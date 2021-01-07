from components import Component, Signal
class SchmittTrigger(Component):
    #default, min, max
    inputs = {
        "threshold":    (0.5, 0.0001, 0.0009),
        "hysteresis":   (0.2, 0, 0.49),
        "input":          (0, None, None)
    }

    outputs = {
        "output":   (None, None, None)
    }

    def eval(self):
        if self.output.value == 0:
            if self.input.value > (self.threshold.value + self.hysteresis.value):
                self.output.value = 1
        elif self.output.value == 1:
            if self.input.value < (self.threshold.value - self.hysteresis.value):
                self.output.value = 0
        else:
             assert False, "Output value has illegal assignment {}".format(self.output.value)

