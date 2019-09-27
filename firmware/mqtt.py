from task import Task
from umqtt.simple import MQTTClient

class MQTT(Task):

    SERVER = "mqtt.ewh"

    def __init__(self, network):
        super().__init__()
        self.connected = False
        self.client = MQTTClient(network.mac, MQTT.SERVER)
        self.client.set_callback(self.callback)

    def callback(self, topic, msg):
        print(topic, msg)

    def set_connected(self, connected):
        if self.connected != connected:
            self.connected = connected
            if self.connected:
                self.on_connect()
            else:
                self.on_disconnect()

    def on_connect(self):
        print("MQTT connected")
        self.subscribe("ewh/config")

    def on_disconnect(self):
        print("MQTT disconnected")

    def subscribe(self, topic):
        try:
            self.client.subscribe(topic)
        except:
            self.set_connected(False)

    def update(self, scheduler):
        if not self.connected:
            try:
                self.client.connect()
                self.set_connected(True)
            except:
                pass
        else:
            try:
                self.client.check_msg()
            except:
                self.set_connected(False)
