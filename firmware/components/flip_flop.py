"""
Implement a D-Flip-Flop with optional asynchronous set and reset signals.
Precendence of input is Reset > Set > CLK (rising edge)
Enable does not affect set and reset
"""
from color_text import ColorText as ct
from components import Component, Signal
class FlipFlop(Component):
    #default, min, max
    inputs = {
        "clk":    (False, None, None),
        "input":  (0, None, None),
        "enable": (True, None, None),
        "set":    (False, None, None),
        "reset":  (False, None, None)    
    }

    outputs = {
        "output":   (None, None, None)
    }

    def first_eval(self):
        self.output.value = 0
        self.on_input_change(self.reset)

    # for better performance we could remove this instance from the fanout of  input and enable in post_init
    
    def on_input_change(self, signal):
        ct.print_debug("updating dff for signal {} with value {}".format(signal.name, signal.value))
        if self.reset.value >= 0.5:
            self.output.value = 0
            return
        
        if self.set.value >= 0.5:
            self.output.value = 1
            return

        if self.enable.value < 0.5:
            return            

        if signal is self.clk and signal.rising_edge():
            self.output.value = self.input.value 
