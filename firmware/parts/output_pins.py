from parts import Part

# Example configuration:
# output_pins:
#   1-1: A1.2/allow_fan and A1.2/temperature > 25
#   1-3: A1.2/ceiling_light

class OutputPins(Part):

    def boot(self):
        self.handlers = {}
        for pin_name, expression in self.config.items():
            if pin_name in self.handlers:
                raise RuntimeError("cannot associate expression {0} to pin {1}, pin already in use".format(expression, pin_name))
            self.handlers[pin_name] = OutputPinHandler(self.mqtt, self.board.get_pin(pin_name), expression)

class OutputPinHandler:

    def __init__(self, mqtt, pin, expression):
        self.pin = pin
        self.expression = mqtt.subscribe_expression(expression, self._on_change)
        try:
            self.pin(bool(self.expression.evaluate()))
        except:
            pass

    def _on_change(self, expression, value):
        self.pin(bool(value))
