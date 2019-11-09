from display import Display
import drivers.ssd1306 as ssd1306
from machine import I2C
from temperature import Temperature

class Board():

    def __init__(self, network, mqtt):
        self.network = network
        self.mqtt = mqtt
        self.display = None      # Both will need to be initialized by the actual board, at least with a noop class,
        self.temperature = None  # because the current code relies on these being set.

    def init_ds18x20(self, ow_pin):
        print("Initializing DS18X20.")
        self.temperature = Temperature(ow_pin, self.mqtt)
        print("DS18X20 initialized.")

    def init_ssd1306i2c(self, reset_pin, scl_pin, sda_pin):
        print("Initializing SSD1306.")
        # Reset display.
        reset_pin.value(0)
        reset_pin.value(1)

        print("scl_pin ", scl_pin)
        print("sda_pin ", sda_pin)

        oled_i2c = I2C(-1, scl=scl_pin, sda=sda_pin)

        try:
            self.display = Display(
                ssd1306.SSD1306_I2C(128, 64, oled_i2c),
                self.network,
                self.mqtt,
            )
            self.display.clear()
            print("SSD1306 initialized.")
        except OSError as err:
           print("OS error: {0}".format(err))
