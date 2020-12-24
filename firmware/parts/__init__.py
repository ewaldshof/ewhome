class Part:

    #services are identical over all parts
    @staticmethod   
    def setup_services(board, mqtt, scheduler):
        Part.board = board
        Part.mqtt = mqtt
        Part.scheduler = scheduler



    @classmethod
    def boot(cls, config):
        cls.instances = {}
        for key, content in config.items():
            cls.instances[key] = cls(key, content)

    @staticmethod
    def print_exception(e, msg="Exception in Config:"):
        print( "\033[91m{0}: {1}: {2}\x1b[0m".format(msg, type(e).__name__, str(e)))

    initialized = False

    @classmethod
    def init_parts(cls, board, mqtt, scheduler, part_config):
        if Part.initialized:
            return
        Part.initialized = True
        Part.board = board
        Part.mqtt = mqtt
        Part.scheduler = scheduler

        for partname, partconfig in part_config.items():
            modname = "parts." + partname
            classname = "".join(word[0].upper() + word[1:] for word in partname.split("_"))
            #output heading for each part type in blue
            print("\033[94mInitializing part: {0} (import {1} from {2})\x1b[0m".format(partname, classname, modname))
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