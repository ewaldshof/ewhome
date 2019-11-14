from parts import Part
from task import Task

# Example configuration:
# proportional: # outputs value in range [0.0:1.0]
#   A1.1/heating:
#     sensor: A1.1/luft
#     midpoint: 21 #in °C
#     spread: 2
#     interval: 60

class Proportional(Part):

    def boot(self):
        self.handlers = {}
        for topic, config in self.config.items():
            self.handlers[topic] = ProportionalHandler(self.mqtt, topic, **config)

class ProportionalHandler(Task):

    def __init__(self, mqtt, topic, sensor, midpoint, spread, interval=60):
        self.mqtt = mqtt
        self.topic = topic
        self.sensor = mqtt.subscribe_expression(sensor, self._noop)
        self.midpoint = mqtt.subscribe_expression(midpoint, self._noop)
        self.spread = mqtt.subscribe_expression(spread, self._noop)
        self.timeout = self.interval = 1000 * interval

    def update(self, scheduler):
        result = 0.0  # Default if anything goes wrong.
        try:
            current = self.sensor.evaluate()
            midpoint = self.midpoint.evaluate()
            spread = self.spread.evaluate()
            diff = midpoint - current
            result = 0.5 + (diff / spread)
            result = min(1.0, max(0.0, result))
        except:
            pass
        self.mqtt.publish(self.topic, result, retain=True)

    def _noop(self, expression, value):
        pass
