import ujson

class Config:

    def __init__(self, network, mqtt):
        self.mac = network.mac
        self.data = {}
        self.mine = None
        self.listeners = []
        mqtt.subscribe("ewh/config", self.on_mqtt)

    def on_mqtt(self, topic, msg):
        try:
            self.data = ujson.loads(msg)
        except:
            print("JSON config decode error: " + msg)
        self.mine = self.data.get("esps", {}).get(self.mac, None)
        for listener in self.listeners:
            listener(self)

    def on_update(self, listener):
        self.listeners.append(listener)
