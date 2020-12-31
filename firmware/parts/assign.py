from parts import Part

# Example configuration:
# assign:
#   A1.1/gated_heating: A1.1/windows and (A1.1/heating > 0.5)
#   BE.1/fan: (BE.1/dew[0] < outside/dew[0]) and (BE.1/dht[0] > 55.0)

class Assign(Part):


    # content is a single line containing the expression to be evaluated
    def __init__(self, key, content):
        self.topic = key 
        self.expression = Part.subscribe_expression(content, self._on_change)
        #do one initial evaluation
        #self.expression._on_mqtt(self.topic, "")
        try:
            Part.publish(self.topic, self.expression.evaluate())
        except:
            pass
            
    def _on_change(self, expression, value):
        Part.publish(self.topic, value)

