import errno
import machine
from parts import Services
import ujson
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
        self.init_parts()
        mqtt.subscribe("config", self.on_mqtt)

    def init_parts(self):
        if self.parts_initialized:
            return
        self.parts_initialized = True
        if not (type(self.mine) is dict and "parts" in self.mine):
            return
        services = Services(self.board, self.mqtt, self.scheduler)
        for partname, partconfig in self.mine["parts"].items():
            modname = "parts." + partname
            classname = "".join(word[0].upper() + word[1:] for word in partname.split("_"))
            print("Initializing part: {0} (import {1} from {2})".format(partname, classname, modname))
            instance = None
            try:
                imported = __import__("parts." + partname, globals(), locals(), [classname])
                try:
                    instance = getattr(imported, classname)(partconfig, services)
                    try:
                        instance.boot()
                    except Exception as e:
                        print("Instance boot failed: {0}: {1}".format(type(e).__name__, str(e)))
                except Exception as e:
                    print("Instantiation failed: {0}: {1}".format(type(e).__name__, str(e)))
            except Exception as e:
                print("Import failed: {0}: {1}".format(type(e).__name__, str(e)))

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
