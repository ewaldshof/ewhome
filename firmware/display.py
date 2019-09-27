from task import Task

class Display(Task):

    def __init__(self, driver):
        super().__init__()
        self.driver = driver
        self.set_mac("00:00:00:00:00:00")
        self.blip = True
        self.rhythm = [.05, .1, .1, .9]
        self.rhythm_index = len(self.rhythm) - 1
        self.countdown = self.interval = 0

    def set_mac(self, mac):
        self.mac = mac[-12:]

    def update(self, scheduler):
        # Clear display.
        self.driver.fill(0)

        # Status bar.
        self.driver.text(self.mac, 0, 57)
        self.driver.text("<3", 113, 57, int(self.blip))

        # Show result and update things.
        self.driver.show()
        self.blip = not self.blip
        self.rhythm_index = (self.rhythm_index + 1) % len(self.rhythm)
        self.countdown = self.interval = self.rhythm[self.rhythm_index]

    def clear(self):
        self.driver.fill(0)
        self.driver.show()
