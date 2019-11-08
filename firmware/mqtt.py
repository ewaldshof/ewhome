from task import Task
from umqtt.simple import MQTTClient
import ure

class MQTT(Task):

    SERVER = "mqtt.ewh"

    MQTT_TO_REGEX = {
        "^\\+/": "[^/]+/",
        "/\\+$": "/[^/]+",
        "/\\+/": "/[^/]+/",
        "^#$": ".*",
        "/#$": "/.+",
    }

    def __init__(self, network):
        super().__init__()
        self.connected = False
        self.subscriptions = []
        self.client = MQTTClient(network.mac, MQTT.SERVER)
        self.client.set_callback(self.callback)

    def callback(self, topic, msg):
        for subscription in self.subscriptions:
            if subscription["re"].match(topic):
                try:
                    subscription["callback"](topic, msg)
                except Exception as e:
                    print("Callback {0} failed: {1}".format(subscription["topic"], str(e)))

    def set_connected(self, connected):
        if self.connected != connected:
            self.connected = connected
            if self.connected:
                self.on_connect()
            else:
                self.on_disconnect()

    def on_connect(self):
        print("MQTT connected")
        for subscription in self.subscriptions:
            try:
                self.client.subscribe(subscription["topic"])
            except:
                self.set_connected(False)

    def on_disconnect(self):
        print("MQTT disconnected")

    def subscribe(self, topic, callback):
        # Build a regex that converts MQTT wildcards to regexes for subscription filtering.
        regex = topic
        for (from_re, to) in MQTT.MQTT_TO_REGEX.items():
            regex = ure.sub(from_re, to, regex)
        if regex[0] != "^":
            regex = "^" + regex
        if regex[-1] != "$":
            regex = regex + "$"
        regex_obj = ure.compile(regex)
        new_subscription = {
            "topic": topic,
            "re": regex_obj,
            "callback": callback,
        }
        for subscription in self.subscriptions:
            for k in ("topic", "callback"):
                if new_subscription[k] != subscription[k]:
                    break
                print("Duplicate subscription on {0} for same callback, returning old id {1}".format(
                    subscription["topic"], subscription["id"]
                ))
                return subscription["id"]
        self.subscriptions.append(new_subscription)
        sub_id = len(self.subscriptions) - 1
        new_subscription["id"] = sub_id
        print("Added subscription {0} for {1}, regex {2}".format(sub_id, topic, regex))
        try:
            self.client.subscribe(topic)
        except:
            self.set_connected(False)
        return sub_id

    def publish(self, topic, message, retain=False):
        # TODO: error handling if not connected
        self.client.publish(topic, message, retain)

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
