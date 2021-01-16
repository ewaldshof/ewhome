from components import Component, Signal
from task import Task, CallbackTask
from color_text import ColorText as ct 
import os 
if os.__name__ == "uos":
    import utime as utime
else:
    import time as utime 

class Time(Component, Task):
    #default, min, max

    outputs = {
        "output":  (None, None, None),
        "year":    (None, None, None),
        "month":   (None, None, None),
        "day":     (None, None, None),
        "hour":    (None, None, None),
        "minute":  (None, None, None),
        "second":  (None, None, None),
        "weekday": (None, None, None),
        "yearday": (None, None, None),
        "phase":   (None, None, None)
    }

# later this should check for the minimum necessary freuency and schedule on that

    def post_init(self, config):
        self.update(Component.scheduler)
        self.interval = 1000
        Component.scheduler.register(self)


    def update(self, scheduler):
        self.output.value = utime.localtime()
        (self.year.value,
         self.month.value,
         self.hour.value,
         self.day.value,
         self.minute.value,
         self.second.value,
         self.weekday.value,
         self.yearday.value) =  self.output.value

        # implemnt a dll to make sure we don't skip seconds
        # we try to be run in the middle of each second
        self.phase.value = utime.ticks_ms()%1000
        self.countdown = 1500 - self.phase.value
