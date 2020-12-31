from task import Task
from mqtt import MQTT

class Display(Task):

    def __init__(self, driver, network):
        super().__init__()
        self.driver = driver
        self.lines = [""] * 6
        self.network = network
        self.mac = network.mac.split(":")
        self.blip = True
        self.mqtt_status = None
        self.wlan_status = None
        self.interval = 400
        self.clear()

    def text(self, text, line):
        if line > 5:
            raise RuntimeError("You may only access lines 0 to 5.")
        self.lines[line] = text
        self.redraw()

    def show_heartbeat(self, show):
        self.blip = bool(show)
        self.redraw()

    def redraw(self):
        
        if self.driver is None:
            return 

        # Clear display.
        self.driver.fill(0)

        # User-defined lines.
        for row in range(6):
            if self.lines[row] != "":
                self.driver.text(self.lines[row], 0, 8 * row)

        # MAC address.
        # The display only allows for 16 characters (each 7 pixels wide plus 1 pixel of spacing), but the MAC address
        # has 17. We cheat by positioning the characters manually.
        for byte in range(6):
            self.driver.text(self.mac[byte], 22 * byte + 1, 49)

        # Status bar.
        if MQTT.connected:
            self.driver.text("M", 0, 57)
        self.driver.text("WL " + self.network.wlan_msg, 16, 57)
        self.driver.text("<3", 113, 57, int(self.blip))

        # Show result and update things.
        self.driver.show()


    def update(self, scheduler):
        mqtt_status = "M" if MQTT.connected else " "
        wlan_status = ("WL " + self.network.wlan_msg) if (self.network is not None) else "WL?"

        if mqtt_status != self.mqtt_status or wlan_status != self.wlan_status:
            self.mqtt_status = mqtt_status
            self.wlan_status = wlan_status
            self.redraw()

    def clear(self):
        if self.driver is None:
            return 

        self.driver.fill(0)
        self.driver.show()
