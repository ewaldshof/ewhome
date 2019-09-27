import network
from ubinascii import hexlify

class Network:

    ssid     = "Wohnis"
    password = "y0ur_W1F1_p@sswORD"

    def __init__(self):
        self.wlan = network.WLAN()
        self.mac = hexlify(self.wlan.config("mac"), ":").decode()
