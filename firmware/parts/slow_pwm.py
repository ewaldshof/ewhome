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
        self.value = False
        self.schedule_period_from_dict(content)
        self.current_ratio = 0.5
        self.ratio = Part.subscribe_expression(content.get("ratio", "0.5"), self._on_change)
        self.update()
        Part.scheduler.register(self)


    def eval(self):
        try:
            self.current_ratio = self.ratio.evaluate()
        except Exception as e:
            ct.print_debug(self.ratio)
            ct.print_debug(self.period)
            ct.format_exception(e, "Exception in SlowPwm.eval_period for instance {}".format(self.topic))
            self.current_ratio = 0.5

    def update(self, scheduler=None):
        old_ratio = self.current_ratio
        self.eval()
        # in extreme cases we set the output to a constant value
        if self.current_ratio < 0.0001 or self.current_ratio > 0.9999:
            self.value = self.current_ratio > 0.5
            phase_ratio = 1.0
        else: #otherwise toggle
            self.value = not self.value
            phase_ratio = self.current_ratio if self.value else 1-old_ratio
        self.countdown = self.interval = 1000 * self.period * phase_ratio
        Part.publish(self.topic, self.value, retain=True)

    def _on_change(self, expression, value):
        pass
