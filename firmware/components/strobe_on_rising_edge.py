"""
This component can be used to create strobes on the rising edge of a signal.
While strobes are useful internally and for MQTT, external protocols often use clock signals instead.
"""

from color_text import ColorText as ct
from components import Component, Signal
class StrobeOnRisingEdge(Component):
    #default, min, max
    inputs = {
        "input":    (None, None, None)
    }

    outputs = {
        "output":   (None, None, None)
    }

    def first_eval(self):
        self.output.value = 0

    # for better performance we could remove this instance from the fanout of increment, decrement, relaod_value, load_value and enable
    
    def on_input_change(self, signal):
        if signal.rising_edge():
            self.output.value += 1
