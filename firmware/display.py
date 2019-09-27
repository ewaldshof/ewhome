from task import Task

class Display(Task):

    def __init__(self, driver):
        super().__init__()
        self.driver = driver
        self.mac = "..."
        self.lines = [""] * 6
        self.network = None
        self.mqtt = None
        self.blip = True
        self.mqtt_status = None
        self.wlan_status = None
        self.interval = 400
        self.clear()

    def set_network(self, network):
        self.network = network
        self.mac = network.mac[-15:]
        self.redraw()

    def set_mqtt(self, mqtt):
        self.mqtt = mqtt

    def text(self, text, line):
        if line > 5:
            raise RuntimeError("You may only access lines 0 to 5.")
        self.lines[line] = text
        self.redraw()

    def show_heartbeat(self, show):
        self.blip = bool(show)
        self.redraw()

    def redraw(self):
        # Clear display.
        self.driver.fill(0)

        # User-defined lines.
        for row in range(6):
            if self.lines[row] != "":
                self.driver.text(self.lines[row], 0, 8 * row)

        # Status bar.
        self.driver.text(self.mac, 0, 49)
        if self.mqtt is not None and self.mqtt.connected:
            self.driver.text("M", 0, 57)
        if self.network is not None:
            self.driver.text("WL " + self.network.wlan_msg, 16, 57)
        self.driver.text("<3", 113, 57, int(self.blip))

        # Show result and update things.
        self.driver.show()


    def update(self, scheduler):
        mqtt_status = "M" if (self.mqtt is not None and self.mqtt.connected) else " "
        wlan_status = ("WL " + self.network.wlan_msg) if (self.network is not None) else "WL?"

        if mqtt_status != self.mqtt_status or wlan_status != self.wlan_status:
            self.mqtt_status = mqtt_status
            self.wlan_status = wlan_status
            self.redraw()

    def clear(self):
        self.driver.fill(0)
        self.driver.show()
