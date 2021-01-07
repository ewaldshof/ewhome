# build netlits of components that can be simulated
# inspired by this paper:
# https://www1.icsi.berkeley.edu/~nweaver/papers/1998-generators.pdf

# This implementation currently only allows for one gloabel netlist that is stored as a class variable.

from color_text import ColorText as ct
import ure as ure
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
    # single line components must use "input" as input name
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
 
        if not isinstance(config, dict):
            #initialize single line component from str by converting it into a multi line component
            ct.print_debug("Converting from single line to multi line Component")
            config = {"input": config}

        # init name of the component
        # default implementation creates "output" connected to a signal with the configured name, driven by this component
        self.init_name(config)
 

        #initialize multi line components from config dictionary
        # create signals or constants for inputs, adds self to fanout
        ct.print_debug("Initializing Inputs")
        self.init_ports_from_dict(config, type(self).inputs, Signal.create_by_input_string)
        # create constants for parameter, adds self to fantout
        ct.print_debug("Initializing Params")
        self.init_ports_from_dict(config, type(self).params, type(self).init_param)
        #create additional outputs, sets self as source
        ct.print_debug("Initializing Outputs")
        self.init_ports_from_dict(config, type(self).outputs, Signal.get_by_name)

        # when done there should be no connections left in configuration
        assert len(config) == 0, "unmatched connections".format(config)
        self.post_init()

    # this is call during netlist creation directly after __init__
    def post_init(self):
        pass

    #default behhaviour for params is to make them a constant signal
    # maybe we can reorder the paarmeters of the singnal_creation_methode to make this a mamber function
    @classmethod
    def init_param(cls, value, component, param_name):
        Signal.constant(value, self2, name)

    @classmethod
    def constant(cls, value, used_by=None, port=None):
        sig = cls.get_by_name("const_"+str(value))
        sig.__value = value
        sig.add_fanout(used_by)
        return sig


    #default implementation assumes name of component specifies an output signal, can be overwritten
    def init_name(self, config):
        ct.print_debug("Default implementation creates output {} for {}".format(self.name, type(self)))
        config["output"] = self.name
        #self.out = Signal.get_by_name(name, self)


    def init_ports_from_dict(self, config, names_and_constraints, signal_creation_method):
        for name  in names_and_constraints:
            (default, minimum, maximum) = names_and_constraints[name]
            ct.print_debug("{} {} {} {}".format(name, default, minimum, maximum))
            line_config = config.pop(name, None)
            if line_config is None:
                assert default is not None, "mandatory port {} missing".format(name)
                sig = Signal.constant(default, self)
            else:
                sig = signal_creation_method(line_config, self, name)
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
            ct.print_heading("Initializing component: {} (import {} from {})".format(compname, classname, modname))
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
                ct.print_info("booting {}".format(cls.__name__))
            except Exception as e:
                ct.format_exception(e, "Class boot failed:")
                raise e
                continue
        cls.first_eval_all()

    @staticmethod
    def setup_services(board, scheduler):
        Component.board = board
        Component.scheduler = scheduler

    #call first_eval on all components in arbitraray order. A partial ordering would be nice instead
    #
    @classmethod
    def first_eval_all(cls):
        for comp in Component.by_name.values():
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
        cls.print_components()
        Signal.print_signals()
    
    @classmethod
    def print_components(cls):
        for name, comp in Component.by_name.items():
            ct.print_heading("component {} of type {}".format(name, type(comp)))
            ct.print_info(str(comp))

    def __str__(self):
        s = ""
        for key, value in self.__dict__.items():
            if key != "expr_locals": #special case for Expression subclass
                s += "{:>15} : {}\n".format(key, str(value))
        return s 

# a sginal passes a value change initiated by its source to all of its fanout components
class Signal():
    @classmethod
    def print_signals(cls):
        for sig in Signal.by_name.values():
            ct.print_heading(str(sig))
            for fanout in sig.fanouts:
                ct.print_info(fanout.name)

    def __str__(self):
        return "{:>5} = signal {}".format(self.value, self.name)

    by_name = {}


    @classmethod
    def constant(cls, value, used_by=None, port=None):
        sig = cls.get_by_name("const_"+str(value))
        sig.__value = value
        sig.add_fanout(used_by)
        return sig

    @classmethod
    def get_by_name(cls, name, source=None, port=None):
        if name in Signal.by_name:
            return Signal.by_name[name]
        else:
            #create a new signals if none with the name exists
            return cls(name, source)

    #analyze an input string to decide what type of signal to use
    #this is intended for the right hand side strings of the instantiation
    @classmethod
    def create_by_input_string(cls, input_string, component, port):
        ct.print_debug("analyzing signal assignment {} of type {}".format(input_string, type(input_string)))
        if not isinstance(input_string, str):
            ct.print_debug("creating constant")
            return cls.constant(input_string, component)

        
        match = Expression.name_re.match(input_string)


            
        # a simple case is a direct assignment of a signal
        if len(match.group(0)) == len(input_string):
            ct.print_debug("direct assignment")
            sig = cls.get_by_name(input_string)
            sig.add_fanout(component)
            return sig

        #otherwise we create an Expression component
        signal_name = ("_".join((component.name, port)))
        expr = Expression(signal_name, input_string)
        Component.by_name[signal_name] = expr
        expr.output.add_fanout(component)
        return expr.output

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
        ct.print_debug("setting {} from {} to {}".format(self.name, self.last_value, val))
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

    name_re = ure.compile(r'[A-Za-z_][A-Za-z0-9_]*')

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

    reserved_names = {"name", "expr_locals", "python", "output"}


    def __init__(self, result_name, expression_string):
        self.name = result_name 
        matches = Expression.name_re.match(expression_string)
        self.expr_locals = {}
        self.python = Expression.name_re.sub(self._replace_in_expr, expression_string)
        ct.print_info("Expression = {}".format(self.python))
        out = Signal.get_by_name(result_name, self)
        setattr(self, "output", out)

    def eval(self):
        val = eval(self.python, self.expr_globals, self.expr_locals)
        ct.print_debug("evaluating {} to {}".format(self.name, self.output.value))
        self.output.value = val


    def _replace_in_expr(self, match):        
        name = match.group(0)
        ct.print_debug("processing match {}".format(name))
        if  name in Expression.expr_globals:
            ct.print_debug("ignoring global function name: {}".format(name))
            return name
        assert name not in Expression.reserved_names, "reserved names can't be used in expressions: {}".format(name)

        sig = Signal.get_by_name(name, None)
        sig.add_fanout(self)
        setattr(self, name, sig)
        self.expr_locals[name] =  sig
        return '{}.value'.format(name)

    def format_expr_locals(self):
        s = ""
        for key, value in self.expr_locals.items():
            s += "{:>20} : {}\n".format(key, str(value.name))
        return s 

    @classmethod
    def is_simple_asssignment(string):
        pass
    