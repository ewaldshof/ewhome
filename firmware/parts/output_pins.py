from parts import Part
from color_text import ColorText as ct 

# Example configuration:
# output_pins:
#   1-1: A1.2/allow_fan and A1.2/temperature > 25
#   1-3: A1.2/ceiling_light

class OutputPins(Part):
    # "key" is the name of the pin
    # "content" is an expression to be assigned to the pin
    def __init__(self, key, content):
        ct.print_debug("assigning topic {} to output pin {}".format(content, key))
     
        self.name = key 
        self.pin = Part.board.get_pin(self.name)
        self.expression = Part.mqtt.subscribe_expression(content, self._on_change)
        try:
            self.pin(bool(self.expression.evaluate()))
        except:
            pass
            
    def _on_change(self, expression, value):
        self.pin(bool(value))



