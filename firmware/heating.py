class Actuator:

    def __init__(self, pin, default=0):
        self.pin = pin
        self.default = default
        pin.value(self.default)
