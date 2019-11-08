import errno
import ujson
from uos import mkdir

cachedir = "/cache"
cachefile = cachedir + "/config.json"

class Config:

    def __init__(self, network, mqtt):
        self.mac = network.mac
        self.data = {}
        self.mine = None
        self.version = "0.3.0"
        self.listeners = []
        self.read_cache()
        mqtt.subscribe(mqtt.PREFIX + "/config", self.on_mqtt)

    def read_cache(self):
        data = None
        try:
            with open(cachefile, "r") as infile:
                data = ujson.load(infile)
        except:
            print("Could not read from config cache.")
        if data is not None:
            self.set_data(data)

    def write_cache(self, data):
        try:
            mkdir(cachedir)
        except OSError as e:
            if e.args[0] != errno.EEXIST: # MicroPython OSError objects don't have .errno
                raise
        with open(cachefile, "w") as outfile:
            ujson.dump(data, outfile)
        print("Written config cache.")

    def set_data(self, data):
        self.data = data
        self.mine = data.get("esps", {}).get(self.mac, None)
        for listener in self.listeners:
            listener(self)

    def on_mqtt(self, topic, data):
        self.set_data(data)
        self.write_cache(data)

    def on_update(self, listener):
        self.listeners.append(listener)
