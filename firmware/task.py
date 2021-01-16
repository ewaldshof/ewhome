from machine import Timer
import micropython
import utime
from color_text import ColorText as ct

class Task():

    
    # a task with an interval < 0 is only run once and then discarded
    def __init__(self, countdown = 1000, interval = 1000):
        self.countdown = countdown
        self.interval = interval

# this method is called when the scheduling event occurs
    def update(self, scheduler):
        pass

class CallbackTask(Task):
    #callback task only run once per default, set interval if you intend otherwise
    def __init__(self, callback=None, countdown = 1000, interval = -1):
        self.callback = callback
        super().__init__(countdown, interval)
        
    def update(self, scheduler):
        self.callback()

class Scheduler():
    def __init__(self):
        self.tasks = set()
        self.timer = None
        self.interval = None

    # create a new task for a callback and register it. 
    # per default the task is only run once
    def schedule_callback(self, callback, countdown=1000, interval = -1):
        self.register(CallbackTask(callback, countdown, interval))

    def register(self, task):
        self.tasks.add(task)

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
            ct.format_exception(e, "could not initialize timer")
    
    def run_due_tasks(self, dummy=None):
        for task in self.tasks:
            if task.countdown <= 0:
                task.countdown += task.interval
                task.update(self)
                # we remove one time task at the end so that update() gets a chance to update the interval
                if task.interval < 0: 
                    self.tasks.discard(task)

