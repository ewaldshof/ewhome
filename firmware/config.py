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
    @staticmethod
    def print_exception(e, msg="Exception in Config:"):
        print( "{0}: {1}: {2}".format(msg, type(e).__name__, str(e)))


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
        Part.setup_services(self.board, self.mqtt, self.scheduler)
        for partname, partconfig in self.mine["parts"].items():
            modname = "parts." + partname
            classname = "".join(word[0].upper() + word[1:] for word in partname.split("_"))
            #output heading for each part type in blue
            print("\033[94mInitializing part: {0} (import {1} from {2})\x1b[0m".format(partname, classname, modname))
            instance = None
            try:
                imported = __import__("parts." + partname, globals(), locals(), [classname])
            except Exception as e:
                Config.print_exception("Import failed", e)
                continue

            try:
                cls = getattr(imported, classname)
            except Exception as e:
                Config.print_exception("getattr failed:", e)
                continue

            try:
                cls.boot(partconfig)
            except Exception as e:
                Config.print_exception("Class boot failed:", e)
                continue
 
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
