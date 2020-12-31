# each part type is implemented in a file in this directory
# The folling naming convention must be followed:

# part type in yaml: loweer case separated by underscored. 
# filename identical to part type + ".py" 
# e.g. slow_pwm or assign

# Class: First word capitalized, not seperated
# e.g. SlowPwm or Assign

# Classes must inherit from Part (or possible its subclasses)

# Classes must implement __init__(self, key, content) that is called for each instance where
# - key is the identifier in the yaml for the instance 
# - content is the whole config assigned to the identifier. This might be a single string for some parts or a dictionary for others
from task import Task
from color_text import ColorText as ct 
from mqtt import MQTT

class Part:
    #services are identical over all parts
    @staticmethod   
    def setup_services(board, scheduler):
        Part.board = board
        Part.scheduler = scheduler


    @classmethod
    def publish(cls, topic, value, retain = True):
        MQTT.publish(topic, value, retain)

    @classmethod
    def subscribe_expression(cls, expression, callback):
        return MQTT.subscribe_expression(expression, callback)

    @classmethod
    def boot(cls, config):
        cls.instances = {}
        ct.print_debug(str(config))
        for key, content in config.items():
            cls.instances[key] = cls(key, content)


    initialized = False

    @classmethod
    def init_parts(cls, board, scheduler, part_config):
        if Part.initialized:
            return
        Part.initialized = True
        Part.board = board
        Part.scheduler = scheduler

        for partname, partconfig in part_config.items():
            modname = "parts." + partname
            classname = "".join(word[0].upper() + word[1:] for word in partname.split("_"))
            #output heading for each part type in blue
            ct.print_heading("Initializing part: {} (import {} from {})".format(partname, classname, modname))
            try:
                imported = __import__("parts." + partname, globals(), locals(), [classname])
            except Exception as e:
                ct.format_exception(e, "Import failed")
                continue

            try:
                cls = getattr(imported, classname)
            except Exception as e:
                ct.format_exception(e, "getattr failed:")
                continue

            try:
                cls.boot(partconfig)
            except Exception as e:
                ct.format_exception(e, "Class boot failed:")
                continue
        
        ct.print_debug("Leaving Init Parts")

# class for parts that are updated with a fixed period
# update is called with the set period in seconds
class FixedPeriodPart(Part, Task):

    # utility function for multi line componets
    # sets period member variable from dictionary entry "period" 
    def schedule_period_from_dict(self, config, default=60, minimum=2, maximum = 3600):
        self.period = config.get("period", default)  # this should evaluate an expression!
        self.period = max(self.period, minimum)
        self.period = min(self.period, maximum)
        self.countdown = self.interval = 1000 * self.period
        config.pop("period", None)  #after this the content dictionery should only contain sensor addresses
        Part.scheduler.register(self)
 