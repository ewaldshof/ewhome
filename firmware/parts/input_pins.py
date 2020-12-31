from machine import Pin
from parts import Part
from color_text import ColorText as ct

# Example configuration:
# input_pins:
#   A1.2/window_open: 5-1
#   A1.2/door_closed: 5-3

class InputPins(Part):

    # "key" is topic the input should be bound to
    # content is a single pin name
    # "content" is an expression to be assigned to the pin
    def __init__(self, key, content):
        ct.print_debug("assigning topic {} to output pin {}".format(content, key))

        self.topic = key 
        self.pin = Part.board.get_pin(content)
        self.pin.irq(trigger=Pin.IRQ_RISING|Pin.IRQ_FALLING, handler=self._on_change)

        try:
            self.pin(bool(self.expression.evaluate()))
        except:
            pass
 
    def _on_change(self, pin):
        # TODO: Debouncing.
        Part.publish(self.topic, bool(pin()))
