from parts import Part
from task import Task

#slow_pwm: # control signal  duty cycle 
# Example configuration:
#
#   A1.1/slow_pwm:
#     period: 60     #pwm perdiod is 60 seconds
#     ration: 0.6    #60% of the period the signal is high

class SlowPwm(Part):

    def boot(self):
        self.handlers = {}
        for topic, config in self.config.items():
            self.handlers[topic] = SlowPwmHandler(self.mqtt, topic, **config)
            self.scheduler.register(self.handlers[topic])

class SlowPwmHandler(Task):

    def __init__(self, mqtt, topic, period=60, ratio=0):
        self.mqtt = mqtt
        self.topic = topic
        self.value = True
        self.period = mqtt.subscribe_expression(period, self._noop)
        self.ratio = mqtt.subscribe_expression(ratio, self._noop)
        self.update()

    def eval_period(self):
        try:
            self.current_period = self.period.evaluate()
            self.current_ratio = self.ratio.evaluate()
        except:
            print("exception in SlowPwm.eval_period {}".format(e))
            self.current_period = 60
            self.current_ratio = 0

    def update(self, scheduler=None):
        if self.value:
            self.eval_period()
            self.countdown = self.interval = 1000 * self.current_period * (1-self.current_ratio)
        else:
            self.countdown = self.interval = 1000 * self.current_period * self.current_ratio
        self.value = not self.value
        self.mqtt.publish(self.topic, self.value, retain=True)

    def _noop(self, expression, value):
        pass
