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
        "output":  (None, None, None), # the 8 tupel returned from utime.localtime()
        "year":    (None, None, None),
        "month":   (None, None, None),
        "day":     (None, None, None),
        "hour":    (None, None, None),
        "minute":  (None, None, None),
        "second":  (None, None, None),  
        "weekday": (None, None, None),  # 0 = monday, 6= sunday
        "yearday": (None, None, None),  # 1 for januar first up to 365
        "phase":   (None, None, None),  # time of update in ms since interval startet, shoudd be about 500
        "time":    (None, None, None)   # seconds since epoch
    }

# later this should check for the minimum necessary freuency and schedule on that

    def post_init(self, config):
        self.interval = 1000
        self.update(Component.scheduler)
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

        self.time.value = utime.time()
        # implemnt a dll to make sure we don't skip seconds
        # we try to brun half a second after the interval started
        self.phase.value = utime.ticks_ms() % self.interval
        self.countdown = self.interval + 500 - self.phase.value
