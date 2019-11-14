from machine import Pin
from parts import Part

# Example configuration:
# input_pins:
#   A1.2/window_open: 5-1
#   A1.2/door_closed: 5-3

class InputPins(Part):

    def boot(self):
        self.handlers = {}
        for topic, pin_name in self.config.items():
            if pin_name in self.handlers:
                raise RuntimeError("cannot associate topic {0} to pin {1}, pin already in use".format(topic, pin_name))
            self.handlers[pin_name] = InputPinHandler(self.mqtt, self.board.get_pin(pin_name), topic)

class InputPinHandler:

    def __init__(self, mqtt, pin, topic):
        self.mqtt = mqtt
        self.pin = pin
        self.topic = topic
        pin.irq(trigger=Pin.IRQ_RISING|Pin.IRQ_FALLING, handler=self._on_change)

    def _on_change(self, pin):
        # TODO: Debouncing.
        self.mqtt.publish(self.topic, bool(pin()))
