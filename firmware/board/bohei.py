from .base import Board as BaseBoard
from machine import Pin

class Board(BaseBoard):

    def init(self):
        self.init_ssd1306i2c(
            reset_pin=self.init_pin(16, "Display Reset", Pin.OUT),
            scl_pin=self.init_pin(15, "Display SCL"),
            sda_pin=self.init_pin(4, "Display SDA"),
        )

        out_mapping = {
            "1-1": 25,
            "1-3": 12,
            "1-5": 13,
            "2-1": 17,
            "2-3":  2,
            "2-5": 23,
            "2-7": 22,
            "4-1": 0
        }
        for name, num in out_mapping.items():
            self.init_pin(num, name, Pin.OUT)

        in_mapping = {
            "5-1": 34,
            "5-3": 35,
            "5-5": 32,
            "5-7": 33,
        }
        for name, num in in_mapping.items():
            self.init_pin(num, name, Pin.IN)
