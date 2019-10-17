from .base import Board as BaseBoard
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
