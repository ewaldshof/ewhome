from display import Display
import drivers.ssd1306 as ssd1306
from machine import I2C, Pin
import ure
#from temperature import Temperature

class Board():

    def __init__(self, network):
        self.network = network
        self.display = None      # Both will need to be initialized by the actual board, at least with a noop class,
        self.pins_by_num = {}
        self.pins_by_name = {}
        self.digits_re = ure.compile("^[\d]+$")

    def init_ssd1306i2c(self, reset_pin, scl_pin, sda_pin):
        print("Initializing SSD1306.")
        # Reset display.
        reset_pin.value(0)
        reset_pin.value(1)

        print("scl_pin ", scl_pin)
        print("sda_pin ", sda_pin)

        oled_i2c = I2C(-1, scl=scl_pin, sda=sda_pin)

        try:
            driver = ssd1306.SSD1306_I2C(128, 64, oled_i2c)
        except OSError as err:
           print("OS error: {0}".format(err))
           driver = None
        print("Display driver: ", driver)   
        self.display = Display(
            driver,
            self.network
        )
        print("Display: ", Display)
        self.display.clear()
        print("SSD1306 initialized.")
    

    def init_pin(self, number, name, mode=-1, pull=None):
        number = int(number)
        name = str(name)
        if number in self.pins_by_num:
            raise RuntimeError(
                "attempted second initialization of pin {0} as {1}; do you have a pin conflict?".format(number, name)
            )
        if name in self.pins_by_name:
            raise RuntimeError("pin name {0} already in use".format(name))
        pin = Pin(number, mode, pull)
        self.pins_by_num[number] = pin
        self.pins_by_name[name] = pin
        return pin

    def get_pin(self, pin_id):
        try:
            x = int(pin_id)
            return self.pins_by_num[x]
        except ValueError:
            if type(pin_id) is str:
                return self.pins_by_name[pin_id]
        raise TypeError("pin_id has to be int or str, not {0}".format(type(pin_id)))
