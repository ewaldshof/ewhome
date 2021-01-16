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
        "yearday": (None, None, None),  # 1 for januar first up to 366
        "phase":   (None, None, None),  # time of update in ms since interval startet, shoudd be about 500
        "tupel":   (None, None, None)   # seconds since epoch
    }

# later this should check for the minimum necessary freuency and schedule on that

    def post_init(self, config):
        # self.create_all_outputs()
        self.interval = 1000
        self.update(Component.scheduler)
        Component.scheduler.register(self)

    def update(self, scheduler):
        tupel = utime.localtime()
        Signal.set(self.tupel,   tupel)
        Signal.set(self.year,    tupel[0])
        Signal.set(self.month,   tupel[1])
        Signal.set(self.day,     tupel[2])
        Signal.set(self.hour,    tupel[3])
        Signal.set(self.minute,  tupel[4])
        Signal.set(self.second,  tupel[5])
        Signal.set(self.weekday, tupel[6])
        Signal.set(self.yearday, tupel[7])
        Signal.set(self.phase,   utime.ticks_ms())
        self.output.value = utime.time()

        # implemnt a dll to make sure we don't skip seconds
        # we try to brun half a second after the interval started
        self.phase.value = utime.ticks_ms() % self.interval
        self.countdown = self.interval + 500 - self.phase.value
