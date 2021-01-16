"""
Implement a transparent latch. 
If clk is high, the output reflects the input.
If clk is high, the output is held
"""

from components import Component, Signal
class Latch(Component):
    #default, min, max
    inputs = {
        "clk":    (False, None, None),
        "input":  (0, None, None),
    }

    outputs = {
        "output":   (None, None, None)
    }

    # for better performance we could remove this instance from the fanout of clk in post_init
        
    def on_input_change(self, signal):
        if self.clk.value >= 0.5:
            self.output.value = self.input.value 
        return