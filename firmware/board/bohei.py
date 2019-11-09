from .base import Board as BaseBoard
from machine import Pin

class Board(BaseBoard):

    def init(self):
        self.init_ssd1306i2c(
            reset_pin=self.init_pin(16, "Display Reset", Pin.OUT),
            scl_pin=self.init_pin(15, "Display SCL"),
            sda_pin=self.init_pin(4, "Display SDA"),
        )
        self.init_ds18x20(
            ow_pin=self.init_pin(0, "Temperature 1-Wire", Pin.OUT)
        )
        mapping = {
            "1_1": 25,
            "1_3": 12,
            "1_5": 13,
            "2_1": 17,
            "2_3":  2,
            "2_5": 23,
            "2_7": 22,
        }
        for name, num in mapping.items():
            self.init_pin(num, name, Pin.OUT)
