import math
import random
from task import Task
import ujson
from umqtt.simple import MQTTClient
import ure
import utime
from color_text import ColorText as ct

class MQTT(Task):

    SERVER = "mqtt.ewh"

    PREFIX = "ewhome"

    MQTT_TO_REGEX = {
        "^\\+/": "[^/]+/",
        "/\\+$": "/[^/]+",
        "/\\+/": "/[^/]+/",
        "^#$": ".*",
        "/#$": "/.+",
    }

    @classmethod 
    def prefix(cld, topic, use_prefix = True):
        return "/".join([MQTT.PREFIX, topic]) if use_prefix else topic

    def __init__(self, network):
        super().__init__()
        self.connected = False
        self.callback_called = False
        self.subscriptions = {}
        self.cache = {}
        self.client = MQTTClient(network.mac, MQTT.SERVER)
        self.client.set_callback(self.callback)

    def callback(self, topic, msg, unjson=True):
        self.callback_called = True
        topic = topic.decode("utf-8")
        if unjson:
            try:
                msg = ujson.loads(msg)
            except Exception as e:
                # Don't pass non-JSON payloads around.
                ct.format_exception(e, "<!- MQTT {0} non-JSON payload rejected: {1}".format(topic, msg))
                return

        ct.print_debug("Received MQTT message for {}".format(topic))
        if topic.endswith('/config'):
            # Config is too large for the memory.
            ct.print_debug("<-- MQTT {0}: config".format(topic))
        else:
            ct.print_debug("<-- MQTT {0}: {1}".format(topic, msg))

        self.cache[topic] = msg
        subscription = self.subscriptions[topic]
        for callback in subscription["callbacks"]:
            try:
                ct.print_debug("callback")
                callback(topic, msg)
            except Exception as e:
                ct.format_exception(e, "Callback {0} failed: {1}".format(subscription))

    def set_connected(self, connected):
        if self.connected != connected:
            self.connected = connected
            if self.connected:
                self.on_connect()
            else:
                self.on_disconnect()

    def on_connect(self):
        print("o-o MQTT connected")
        for topic in self.subscriptions:
            ct.print_info("~~~ MQTT subscribe on {0}".format(topic))
            try:
                self.client.subscribe(topic)
            except:
                self.set_connected(False)

    def on_disconnect(self):
        print("-x- MQTT disconnected")

    def subscribe(self, topic, callback, use_prefix=True):
        topic = MQTT.prefix(topic, use_prefix)
        

        ct.print_debug("subscribing topic {}".format(topic))

        subscription =  self.subscriptions.get(topic, None)

        # if we allready are subscribed to this, just add another callback
        if subscription is not None:
            callbacks = subscription["callbacks"]
            if callback in callbacks:
                ct.print_warning("Callback allready exists for this topic, doing nothing")
            else:
                ct.print_debug("adding callback to existing subscription {}".format(topic))
                subscription["callbacks"].append(callback)
            return subscription

        self.subscriptions[topic] = {"topic": topic, "callbacks": [callback]}

        ct.print_info("Added subscription for {}".format(topic))
        if self.connected:
            try:
                print("~~~ MQTT subscribe on {0}".format(topic))
                self.client.subscribe(topic)
            except Exception as e:
                ct.format_exception(e, "subscription failed")
                self.set_connected(False)
        return subscription

    def subscribe_expression(self, expression, callback):
        expr = Expression(self, expression)
        expr.subscribe(callback)
        return expr

#    def update_variable(self, topic, ratain=False, use_prefix=True, publish=True):


    def publish(self, topic, data, retain=False, use_prefix=True):
        topic = MQTT.prefix(topic, use_prefix)
        message = ujson.dumps(data)
        print("-{0}> MQTT {1}{2}: {3}".format(
            "-" if self.connected else " ", topic, " (retain)" if retain else "", message
        ))
        if retain:
            self.cache[topic] = data
        if self.connected:
            try:
                self.client.publish(topic, message, retain)
                return
            except:
                self.set_connected(False)
        # At this point, the message was not sent and we are probably disconnected. Deliver locally.
        self.callback(topic.encode("utf-8"), data, unjson=False) # no need to convert JSON back and forth

    def get_cached(self, topic, default=None, use_prefix=True):
        topic = MQTT.prefix(topic, use_prefix)
        return self.cache[topic] if topic in self.cache else default

    def get_cached_or_raise(self, topic, use_prefix=True):
        topic = MQTT.prefix(topic, use_prefix)
        if topic not in self.cache:
            raise KeyError(topic)
        return self.cache[topic]

    def update(self, scheduler):
        if not self.connected:
            try:
                self.client.connect()
                self.set_connected(True)
            except:
                pass
        else:
            self.callback_called = False
            try:
                while True:
                    self.client.check_msg()
                    if not self.callback_called:
                        break
                    self.callback_called = False
                self.callback_called = False
            except:
                self.set_connected(False)


class Expression:

    def __init__(self, mqtt, expression):
        self.mqtt = mqtt
        self.topics = []
        expression = str(expression)
        self.expression = expression
        self.python = expression
        self.expr_globals = {
            "dew"  : self._dewpoint,
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
            "mqtt_get_value": mqtt.get_cached_or_raise,
        }
        self._analyze(expression)
        self.topics = list(set(self.topics))  # remove duplicates
        print("Expression `{0}` becomes `{1}`, has topics: {2}".format(expression, self.python, self.topics))

    def __str__(self):
        return self.expression

    def _analyze(self, expression):
        # MicroPython doesn't support \w in character classes, hence we write them out.
        topic_re = ure.compile(r'[A-Za-z0-9_][A-Za-z0-9_./-]+/[A-Za-z0-9_.-]*[A-Za-z0-9_]')
        # There's also no find_all, and on the ESP32 no match.end(), therefore we use sub() to collect topics.
        self.python = topic_re.sub(self._replace_in_expr, expression)

    def _dewpoint(self, rel_humidity, temperature):
        humidity /= 100.0
        v = math.log10(humidity)+ 7.5*temperature/(237.3+temperature)
        tk = temperature + 273.15
        dd = humidity * 6.1078 * pow(10,7.5*temperature/(237.3+temperature))
        Rstar = 8314.3 #J/(kmol*K)
        m_w = 1801600.0 # kg/(10e5 kmol)
        return {
            "dewpoint": 237.3*v/(7.5-v),
            "abs_humidity": (m_w/Rstar)*dd/tk,
        }

    def _on_mqtt(self, topic, value):
        # Try evaluating the expression. If there are errors, don't notify our observer.
        try:
            value = self.evaluate()
            try:
                self.callback(self, value)
            except Exception as e:
                print("Callback for `{0}` failed: {1}: {2}".format(
                    self.expression, type(e).__name__, str(e)
                ))
        except Exception as e:
            print("Evaluating `{0}` failed: {1}: {2}".format(
                self.expression, type(e).__name__, str(e)
            ))

    def _replace_in_expr(self, match):
        topic = match.group(0)
        self.topics.append(topic)
        return 'mqtt_get_value("{0}")'.format(topic)

    def evaluate(self):
        return eval(self.python, self.expr_globals)

    def subscribe(self, callback):
        self.callback = callback
        for topic in self.topics:
            self.mqtt.subscribe(topic, self._on_mqtt)
