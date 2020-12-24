import errno
import machine
import ujson
from parts import Part
from uos import mkdir

try: # Some boards have a sync() call for filesystem sync, others don't.
    from uos import sync
except:
    def sync():
        pass

cachedir = "/cache"
cachefile = cachedir + "/config.json"

class Config:


    def __init__(self, board, network, mqtt, scheduler):
        self.mqtt = mqtt
        self.board = board
        self.scheduler = scheduler
        self.parts_initialized = False
        self.mac = network.mac
        self.data = {}
        self.mine = None
        self.version = "0.7.0"
        self.listeners = [self.board.temperature._on_config_update] # TODO: Hack until Temperature becomes a Part.
        self.read_cache()
        if (type(self.mine) is dict and "parts" in self.mine):
            Part.init_parts(board, mqtt, scheduler, self.mine["parts"])
        mqtt.subscribe("config", self.on_mqtt)

 
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
        mine_before = self.mine
        self.set_data(data)
        self.write_cache(data)
        if self.mine != mine_before:
            # My config has changed. Reboot.
            sync()
            machine.reset()

    def on_update(self, listener):
        self.listeners.append(listener)
