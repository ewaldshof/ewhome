from .base import Board as BaseBoard
from heating import Actuator
from machine import Pin

class Board(BaseBoard):

    def init(self):
        self.init_ssd1306i2c(
            reset_pin=Pin(16, Pin.OUT),
            scl_pin=Pin(15),
            sda_pin=Pin(4),
        )
        self.init_ds18x20(
            ow_pin=Pin(0, Pin.OUT)
        )
        # TODO: right now, actuators are dummys
        self.actuators = {
            "1_1": Actuator(Pin(25, Pin.OUT)),
            "1_3": Actuator(Pin(12, Pin.OUT)),
            "1_5": Actuator(Pin(13, Pin.OUT)),
            "2_1": Actuator(Pin(17, Pin.OUT)),
            "2_3": Actuator(Pin( 2, Pin.OUT)),
            "2_5": Actuator(Pin(23, Pin.OUT)),
            "2_7": Actuator(Pin(22, Pin.OUT)),
        }
