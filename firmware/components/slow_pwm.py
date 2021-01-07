from components import Component, Signal
from task import Task, CallbackTask
from color_text import ColorText as ct 

class SlowPwm(Component, Task):
    #default, min, max
    inputs = {
        "period":   (60, 0.1, 60*60*24),
        "ratio":    (0.5, 0, 1),
    }

    outputs = {
        "output":   (None, None, None)
    }

    def post_init(self):
        self.reset_task = CallbackTask(self.reset)
        self.update(Component.scheduler)
        Component.scheduler.register(self)

    def update(self, scheduler):
        self.interval = self.countdown = self.period.value * 1000
        self.output.value = 1
        self.reset_task.countdown = self.interval * self.ratio.value
        scheduler.register(self.reset_task)

    def reset(self):
        self.output.value = 0

