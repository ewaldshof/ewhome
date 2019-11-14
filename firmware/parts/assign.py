from parts import Part

# Example configuration:
# assign:
#   A1.1/gated_heating: A1.1/windows and (A1.1/heating > 0.5)
#   BE.1/fan: (BE.1/dew[0] < outside/dew[0]) and (BE.1/dht[0] > 55.0)

class Assign(Part):

    def boot(self):
        self.handlers = {}
        for topic, expression in self.config.items():
            self.handlers[topic] = AssignHandler(self.mqtt, topic, expression)

class AssignHandler:

    def __init__(self, mqtt, topic, expression):
        self.topic = topic
        self.mqtt = mqtt
        self.expression = mqtt.subscribe_expression(expression, self._on_change)

    def _on_change(self, expression, value):
        self.mqtt.publish(self.topic, value)
