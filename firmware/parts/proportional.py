from parts import FixedPeriodPart, Part

# proportional: # outputs value in range [0.0:1.0]
# creates a linear ramp with width "spread" centered around "midpoint"
# 0.0 if sensor <= (midpoint - spread/2)
# 1.0 if sensor >= (midpoint + spread/2)
# useful for pid controllers
# Example configuration:
#
#   A1.1/heating:
#     sensor: A1.1/luft
#     midpoint: 21 #in °C
#     spread: 2
#     interval: 60

class Proportional(FixedPeriodPart):

    def __init__(self, key, content):
        self.topic = key
        print("key: ", key)
        print("content: ", content)

        assert {"sensor"}.issubset(content), "parameter missing from proportional {}".format(key)
        self.sensor = Part.mqtt.subscribe_expression(content["sensor"], self._on_change)
        self.midpoint = Part.mqtt.subscribe_expression(content.get("midpoint", "20"), self._on_change)
        self.spread = Part.mqtt.subscribe_expression(content.get("spread", "2"), self._on_change)
        self.schedule_period_from_dict(content)
 
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
        Part.mqtt.publish(self.topic, result, retain=True)

    def _on_change(self, expression, value):
        pass


