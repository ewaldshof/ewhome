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
        self.interval = int(1000 / 30)
        self.clear()

    def set_network(self, network):
        self.network = network
        self.mac = network.mac[-15:]

    def set_mqtt(self, mqtt):
        self.mqtt = mqtt

    def text(self, text, line):
        if line > 5:
            raise RuntimeError("You may only access lines 0 to 5.")
        self.lines[line] = text

    def update(self, scheduler):
        # Clear display.
        self.driver.fill(0)

        # User-defined lines.
        for row in range(6):
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

    def clear(self):
        self.driver.fill(0)
        self.driver.show()
