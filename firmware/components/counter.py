"""
Imeplment an up/down counter.
Counts down by decrement on each down_strobe change.
Counting down stops at 0 unless there is a reload value set, in which case counter=reload_value upon next down_strobe.
Counts up by increment on each up_strobe change.
Loads load_value on load_strobe change.
All of the above does not happen if enable < 0.5
"""

from color_text import ColorText as ct
from components import Component, Signal
class Counter(Component):
    #default, min, max
    inputs = {
        "down":         (False, None, None),
        "up":           (False, None, None),
        "increment":    (1, None, None),
        "decrement":    (1, None, None),
        "reload_value": (0, None, None),
        "load_value":   (1, None, None),
        "load":         (False, None, None),
        "enable":       (1, None, None)    
    }

    outputs = {
        "output":   (None, None, None)
    }

    def first_eval(self):
        self.output.value = self.load_value.value

    # for better performance we could remove this instance from the fanout of increment, decrement, relaod_value, load_value and enable
    
    def on_input_change(self, signal):
        ct.print_debug("updating counter for signal {} with value {}".format(signal.name, signal.value))
        if self.enable.value < 0.5:
            return
        
        if signal.has_changed():
            if signal is self.down:
                self.output.value = self.reload_value.value if self.output.value <= 0 else self.output.value - self.decrement.value 
                return 

            if signal is self.up:
                self.output.value += self.increment.value 
                return 

            if signal is self.load:
                self.output.value = self.load_value.value  
                return