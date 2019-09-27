from machine import Timer
import micropython
import utime

class Task():

    def __init__(self):
        self.countdown = self.interval = 1000

    def update(self, scheduler):
        pass

class Scheduler():

    def __init__(self):
        self.tasks = []
        self.timer = None
        self.interval = None

    def register(self, task):
        if task not in self.tasks:
            self.tasks.append(task)

    def tick(self, timer):
        interval = self.interval
        for task in self.tasks:
            task.countdown -= interval
        micropython.schedule(self.run_due_tasks, None)

    def start(self, interval_ms):
        interval_ms = int(interval_ms)
        self.interval = interval_ms
        self.timer = Timer(-1)
        self.timer.init(period=interval_ms, mode=Timer.PERIODIC, callback=self.tick)

    def run_due_tasks(self, dummy=None):
        for task in self.tasks:
            if task.countdown <= 0:
                task.countdown = task.interval + task.countdown
                task.update(self)
