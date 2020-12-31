from parts import FixedPeriodPart, Part
from task import Task
from color_text import ColorText as ct 

#slow_pwm: # control signal  duty cycle 
# Example configuration:
#
#   A1.1/slow_pwm:
#     period: 60     #pwm perdiod is 60 seconds
#     ration: 0.6    #60% of the period the signal is high

class SlowPwm(FixedPeriodPart):

    def __init__(self, key, content):
        self.topic = key
        self.value = True
        self.schedule_period_from_dict(content)
        self.ratio = Part.subscribe_expression(content.get("ratio", "0.5"), self._on_change)
        self.update()


    def eval_period(self):
        try:
            self.current_ratio = self.ratio.evaluate()
        except Exception as e:
            ct.print_debug(self.ratio)
            ct.print_debug(self.period)
            ct.format_exception(e, "Exception in SlowPwm.eval_period for instance {}".format(self.topic))
            self.current_ratio = 0.5

    def update(self, scheduler=None):
        if self.value:
            self.eval_period()
            self.countdown = self.interval = 1000 * self.period * (1-self.current_ratio)
        else:
            self.countdown = self.interval = 1000 * self.period * self.current_ratio
        self.value = not self.value
        Part.publish(self.topic, self.value, retain=True)

    def _on_change(self, expression, value):
        pass
