# build netlits of components that can be simulated
# inspired by this paper:
# https://www1.icsi.berkeley.edu/~nweaver/papers/1998-generators.pdf

# This implementation currently only allows for one gloabel netlist that is stored as a class variable.

from color_text import ColorText as ct
import re as ure
import time as utime
#import ure
#import utime

import math 
import random

class Component():
    # this provide a dictionalry of all components by name 
    by_name = {}

    # each class configuers the valid input signal names with this dictionary.
    # the entries are tuples (default, min, max)
    # if min or max is None it will not be checked
    # if default is none the input is consiered to be a mandatory input
    # single line components must use "in" as input name
    inputs = {}

   # same for parameters, these can't be changed after initialisation
    params = {}

    #outputs don't need defaults, initialize them all to (None, None, None) 
    outputs = {}

    # init is called during netlist creation
    # when the netlist is complete, first_eval() is called on all components
    def __init__(self, key, config):
        ct.print_info("New {} named {} initialised with {}".format(type(self).__name__, key, config))
        self.name = key

        # init name of the component
        # default implementation creates an output out connected to a signal with the configured name, driven by this component
        self.init_name(key, config)
 
        if isinstance(config, str):
            #initialize single line component from str
            self.init_single_line(config)
        else:
            assert type(config) == dict, "config of a component must either be str or dict"
            #initialize multi line components from config dictionary
            # create signals or constants for inputs, adds self to fanout
            ct.print_debug("Initializing Inputs")
            self.init_ports_from_dict(config, type(self).inputs, Signal.create_by_input_string)
            # create constants for parameter, adds self to fantout
            ct.print_debug("Initializing Params")
            self.init_ports_from_dict(config, type(self).params, Signal.constant)
            #create additional outputs, sets self as source
            ct.print_debug("Initializing Outputs")
            self.init_ports_from_dict(config, type(self).outputs, Signal.get_by_name)

            # when done there should be no connections left in configuration
            assert len(config) == 0, "unmatched connections".format(config)

    #default implementation assumes name of component specifies an output signal, can be overwritten
    def init_name(self, name, config):
        ct.print_debug("Default implementation creates output {} for {}".format(name, type(self)))
        config["out"] = name
        #self.out = Signal.get_by_name(name, self)

    #default implementation assumes signal, can be overwritten for params
    def init_single_line(self, config):
        ct.print_debug("Default implementation creates input {} from single line for {}".format(config, type(self)))
        self.init_ports_from_dict({"in": config}, type(self).inputs, Signal.create_by_input_string)

    def init_ports_from_dict(self, config, names_and_constraints, signal_creation_method):
        for name  in names_and_constraints:
            (default, minimum, maximum) = names_and_constraints[name]
            ct.print_debug("{} {} {} {}".format(name, default, minimum, maximum))
            line_config = config.pop(name, None)
            if line_config is None:
                assert default is not None, "mandatory port {} missing".format(name)
                sig = Signal.constant(default, self)
            else:
                sig = signal_creation_method(line_config, self)
            setattr(self, name, sig) 
    

    @classmethod
    def init_class(cls, config):
        ct.print_debug("Unmodified init_class() does nothing for {}".format(cls.__name__))
        pass

    @classmethod
    def boot(cls, config):
        cls.init_class(config)
        for key, content in config.items():
            Component.by_name[key] = cls(key, content)

    # create a netlist of components ant signals from a config dict 
    @classmethod
    def netlist_from_config(cls, config):
        for compname, compconfig in config.items():
            modname = "components." + compname
            classname = "".join(word[0].upper() + word[1:] for word in compname.split("_"))
            #output heading for each part type in blue
            ct.print_heading("Initializing part: {} (import {} from {})".format(compname, classname, modname))
            try:
                imported = __import__("components." + compname, globals(), locals(), [classname])
            except Exception as e:
                ct.format_exception(e, "Import failed")
                continue

            try:
                cls = getattr(imported, classname)
            except Exception as e:
                ct.format_exception(e, "getattr failed:")
                continue

            try:
                cls.boot(compconfig)
            except Exception as e:
                ct.format_exception(e, "Class boot failed:")
                raise e
                continue

    #call first_eval on all components in arbitraray order. A partial ordering would be nice instead
    #
    @classmethod
    def first_eval_all(cls):
        for comp in Component.by_name.items():
            comp.first_eval()

    #first eval must ensure that no outputs have value none
    #the default implementation relies on __init__ to set all outputs to 0
    def first_eval(self):
        self.eval()

    # this is called when more than one input changed or we don't know whether an input changed and want to reevaluate anyway
    # components must override this any can additionally override on_input_change to increase peformance
    def eval(self):
        pass

    # this is called when a single input changed
    # this must only be called after netlist is built completely
    # default implementation ignores the information on input and calls eval
    def on_input_change(self, signal):
        self.eval()

        
    @classmethod
    def print_netlist(cls):
        for name, comp in Component.by_name.items():
            ct.print_heading("component {} of type {}".format(name, type(comp)))
            ct.print_info(str(comp))

    def __str__(self):
        s = ""
        for key, value in self.__dict__.items():
            s += "{:>15} : {}\n".format(key, str(value))
        return s 

# a sginal passes a value change initiated by its source to all of its fanout components
class Signal():

    def __str__(self):
        return "{:>5} = signal {}".format(self.value, self.name)

    by_name = {}

    name_re = ure.compile(r'[A-Za-z_][A-Za-z0-9_]*')

    @classmethod
    def constant(cls, value, used_by=None):
        sig = cls.get_by_name("const_"+str(value))
        sig.__value = value
        sig.add_fanout(used_by)
        return sig

    @classmethod
    def get_by_name(cls, name, source=None):
        if name in Signal.by_name:
            return Signal.by_name[name]
        else:
            #create a new signals if none with the name exists
            return cls(name, source)

    #analyze an input string to decide what type of signal to use
    #this is intended for the right hand side strings of the instantiation
    @classmethod
    def create_by_input_string(cls, name, component):
        ct.print_debug("analyzing signal assignment {} of type {}".format(name, type(name)))
        if not isinstance(name, str):
            ct.print_debug("creating constant")
            return cls.constant(name, component)

        match = cls.name_re.match(name)

        # a simple case is a direct assignment of a signal
        if match.end() == len(name):
            ct.print_debug("direct assignment")
            sig = cls.get_by_name(name)
            sig.add_fanout(component)
            return sig

        #otherwise we create an Expression component

    @classmethod
    def set_by_name(cls, name, value):
        Signal.get_by_name(name).value = value

    def __init__(self, name, source = None):
        self.name = name
        self.set_source(source)
        assert name not in Signal.by_name, "signal {} allready exists".format(name)
        Signal.by_name[name] = self
        self.last_value = self.__value = 0
        self.fanouts = set()

    def has_changed(self):
        return self.last_value != self.value
    
    def rising_edge(self, threshold = 0.5):
        return self.has_changed and self.value > threshold 

    def falling_edge(self, threshold = 0.5):
        return self.has_changed and self.value <= threshold 

    def __setValue(self, val):
        # no change, no None
        if self.last_value == val:
            return 

        self.last_value = self.__value
        self.__value = val

        for component in self.fanouts:
            component.on_input_change(self)

    def __getValue(self):
        return self.__value
    
    value = property(__getValue, __setValue)

    def set_source(self, component):
        self.source = component

    def add_fanout(self, component):
        self.fanouts.add(component)

    

class Expression(Component):
     expr_globals = {
            "dew"  : None, #self._dewpoint,
            "min"  : min,
            "max"  : max,
            "sqrt" : math.sqrt,
            "exp"  : math.exp,
            "abs"  : math.fabs,
            "floor": math.floor,
            "ceil" : math.ceil,
            "fmod" : math.fmod,
            "log"  : math.log,
            "log10": math.log10,
            "pow"  : math.pow,
            "acos" : math.acos,
            "asin" : math.asin,
            "atan" : math.atan,
            "atan2": math.atan2,
            "cos"  : math.cos,
            "sin"  : math.sin,
            "tan"  : math.tan,
            "trunc": math.trunc,
            "degrees" : math.degrees,
            "radians" : math.radians,
            "randint" : random.randint,
            "uniform" : random.uniform,
            "time"    : utime.time,  #only available in micropython
            "mqtt_get_value": None #MQTT.get_cached_or_raise,
        }