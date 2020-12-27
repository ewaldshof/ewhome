from parts import Part
from task import Task
from color_text import ColorText as ct 

#slow_pwm: # control signal  duty cycle 
# Example configuration:
#
#   A1.1/slow_pwm:
#     period: 60     #pwm perdiod is 60 seconds
#     ration: 0.6    #60% of the period the signal is high

class SlowPwm(Part, Task):

    def __init__(self, key, content):
    # mqtt, topic, period=60, ratio=0):
        self.topic = key
        self.value = True
        self.period = Part.mqtt.subscribe_expression(content.get("period", "60"), self._on_change)
        self.ratio = Part.mqtt.subscribe_expression(content.get("ratio", "0.5"), self._on_change)
        Part.scheduler.register(self)
        self.update()

    def eval_period(self):
        try:
            self.current_period = self.period.evaluate()
            self.current_ratio = self.ratio.evaluate()
        except:
            ct.format_exception(e, "Exception in SlowPwm.eval_period for instance {}".format(topic))
            self.current_period = 60
            self.current_ratio = 0.5

    def update(self, scheduler=None):
        if self.value:
            self.eval_period()
            self.countdown = self.interval = 1000 * self.current_period * (1-self.current_ratio)
        else:
            self.countdown = self.interval = 1000 * self.current_period * self.current_ratio
        self.value = not self.value
        Part.mqtt.publish(self.topic, self.value, retain=True)

    def _on_change(self, expression, value):
        pass
