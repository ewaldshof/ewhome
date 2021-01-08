import errno
import machine
import ujson
from components import Component
from uos import mkdir
from color_text import ColorText as ct
from mqtt import MQTT

try: # Some boards have a sync() call for filesystem sync, others don't.
    from uos import sync
except:
    def sync():
        pass

cachedir = "/cache"
cachefile = cachedir + "/config.json"
config_topic_base = "board/"

class Config:


    def __init__(self, board, network, scheduler):
        self.board = board
        self.scheduler = scheduler
        self.parts_initialized = False
        self.mac = network.mac
        self.data = {}
        self.mine = None
        self.version = "0.8.0"
        self.listeners = []
        self.read_cache()
#        if (type(self.mine) is dict and "parts" in self.mine):
#            ct.print_heading("initializing from cache")
#            Part.init_parts(board, scheduler, self.mine["parts"])

        Component.setup_services(board, scheduler)
        if (type(self.mine) is dict and "components" in self.mine):
            ct.print_heading("initializing from cache")
            Component.netlist_from_config(self.mine["components"])
            Component.print_netlist()
        MQTT.subscribe(config_topic_base + self.mac + "/config", self.on_mqtt)

 
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
        self.mine = data
        for listener in self.listeners:
            listener(self)

    def on_mqtt(self, topic, data):
        mine_before = self.mine
        self.set_data(data)
        self.write_cache(data)

        #comparing jsons is not reliable because the ordering of elements can change.
        #Therefore we just compare the date the config was published
        if (mine_before is None) or (self.mine is None): 
            same_date = False
        else:
            same_date = (mine_before["published"] == self.mine["published"])

        if not same_date:
            ct.print_warning("Config changed, rebooting")  
            # My config has changed. Reboot.
            sync()
            machine.reset()
        ct.print_info("Received config with identical date {}".format(self.mine["published"]))

    def on_update(self, listener):
        self.listeners.append(listener)
