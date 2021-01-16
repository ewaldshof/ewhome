from components import Component, Signal
from task import Task
from color_text import ColorText as ct

class Monoflop(Component, Task):
    #default, min, max
    inputs = {
        "clk":    (False, None, None),   # creates a pulse on rising edge of clk
        "strobe": (False, None, None),   # or on any change of strobe
        "time":   (1, None, None),       # this is the length of the pulse in seconds
    }

    outputs = {
        "output":   (None, None, None)
    }

    def first_eval(self):
        self.output.value = 0
        self.interval=-1

    # for better performance we could remove this instance from the fanout of time
    
    def on_input_change(self, signal):
        if (signal is self.clk and signal.rising_edge()) or (signal is self.strobe and signal.has_changed()):
            ct.print_debug("startet {}s pulse".format(self.time.value))
            self.output.value = 1
            self.countdown = self.time.value * 1000
            Component.scheduler.register(self) 

    def update(self, scheduler):
        self.output.value = 0
