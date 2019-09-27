from task import Task

class Display(Task):

    def __init__(self, driver):
        super().__init__()
        self.driver = driver
        self.mac = "..."
        self.network = None
        self.mqtt = None
        self.blip = True
        self.rhythm = [.05, .1, .1, .9]
        self.rhythm_index = len(self.rhythm) - 1
        self.countdown = self.interval = 0

    def set_network(self, network):
        self.network = network
        self.mac = network.mac[-15:]

    def set_mqtt(self, mqtt):
        self.mqtt = mqtt

    def update(self, scheduler):
        # Clear display.
        self.driver.fill(0)

        # Status bar.
        self.driver.text(self.mac, 0, 49)
        if self.mqtt is not None and self.mqtt.connected:
            self.driver.text("M", 0, 57)
        if self.network is not None:
            self.driver.text("WL " + self.network.wlan_msg, 16, 57)
        self.driver.text("<3", 113, 57, int(self.blip))

        # Show result and update things.
        self.driver.show()
        self.blip = not self.blip
        self.rhythm_index = (self.rhythm_index + 1) % len(self.rhythm)
        self.countdown = self.interval = self.rhythm[self.rhythm_index]

    def clear(self):
        self.driver.fill(0)
        self.driver.show()
