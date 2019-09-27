from task import Task

class Heartbeat(Task):

    def __init__(self, display):
        super().__init__()
        self.display = display
        self.rhythm = [100, 200, 100, 600]
        self.rhythm_index = len(self.rhythm) - 1
        self.countdown = self.interval = 0

    def update(self, scheduler):
        self.rhythm_index = (self.rhythm_index + 1) % len(self.rhythm)
        self.display.show_heartbeat(self.rhythm_index % 2 == 0)
        self.countdown = self.interval = self.rhythm[self.rhythm_index]
