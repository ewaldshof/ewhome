from machine import Timer
import micropython
import utime

class Task():

    def __init__(self):
        self.countdown = self.interval = 1000

# this method is called when the scheduling even occurs
    def update(self, scheduler):
        pass

class Scheduler():
    @staticmethod
    def print_exception(e, msg="Exception in Part:"):
        print( "\033[91m{0}: {1}: {2}\x1b[0m".format(msg, type(e).__name__, str(e)))

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
        try:
            self.timer = Timer(-1)
            self.timer.init(period=interval_ms, mode=Timer.PERIODIC, callback=self.tick)
        except Exception as e:
            Scheduler.print_exception(e, "could not initialize timer")

    def run_due_tasks(self, dummy=None):
        for task in self.tasks:
            if task.countdown <= 0:
                task.countdown = task.interval + task.countdown
                task.update(self)
