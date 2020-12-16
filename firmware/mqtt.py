import math
import random
from task import Task
import ujson
from umqtt.simple import MQTTClient
import ure
import utime

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

    def __init__(self, network):
        super().__init__()
        self.connected = False
        self.callback_called = False
        self.subscriptions = []
        self.topics = []
        self.cache = {}
        self.client = MQTTClient(network.mac, MQTT.SERVER)
        self.client.set_callback(self.callback)

    def callback(self, topic, msg, unjson=True):
        self.callback_called = True
        topic = topic.decode("utf-8")
        if unjson:
            try:
                msg = ujson.loads(msg)
            except:
                # Don't pass non-JSON payloads around.
                print("<!- MQTT {0} non-JSON payload rejected: {1}".format(topic, msg))
                return
        if not topic.endswith('/config'):
            # Config is too large for the memory.
            print("<-- MQTT {0}: {1}".format(topic, msg))
        self.cache[topic] = msg
        for subscription in self.subscriptions:
            if subscription["re"].match(topic):
                try:
                    subscription["callback"](topic, msg)
                except Exception as e:
                    print("Callback {0} failed: {1}".format(subscription["topic"], str(e)))

    def set_connected(self, connected):
        if self.connected != connected:
            self.connected = connected
            if self.connected:
                self.on_connect()
            else:
                self.on_disconnect()

    def on_connect(self):
        print("o-o MQTT connected")
        for topic in self.topics:
            print("~~~ MQTT subscribe on {0}".format(topic))
            try:
                self.client.subscribe(topic)
            except:
                self.set_connected(False)

    def on_disconnect(self):
        print("-x- MQTT disconnected")

    def subscribe(self, topic, callback, use_prefix=True):
        if use_prefix:
            topic = "{0}/{1}".format(MQTT.PREFIX, topic)
        # Build a regex that converts MQTT wildcards to regexes for subscription filtering.
        regex = topic
        for (from_re, to) in MQTT.MQTT_TO_REGEX.items():
            regex = ure.sub(from_re, to, regex)
        if regex[0] != "^":
            regex = "^" + regex
        if regex[-1] != "$":
            regex = regex + "$"
        regex_obj = ure.compile(regex)
        new_subscription = {
            "topic": topic,
            "re": regex_obj,
            "callback": callback,
        }
        for subscription in self.subscriptions:
            identical = new_subscription['topic'] == subscription['topic'] \
                and new_subscription['callback'] == subscription['callback']
            if identical:
                print("Duplicate subscription on {0} for same callback, returning old id {1}".format(
                    subscription["topic"], subscription["id"]
                ))
                return subscription["id"]
        self.subscriptions.append(new_subscription)
        new_topic = new_subscription['topic'] not in self.topics
        if new_topic:
            self.topics.append(new_subscription['topic'])
        sub_id = len(self.subscriptions) - 1
        new_subscription["id"] = sub_id
        print("Added subscription {0} for {1}, regex {2}".format(sub_id, topic, regex))
        if self.connected and new_topic:
            try:
                print("~~~ MQTT subscribe on {0}".format(topic))
                self.client.subscribe(topic)
            except:
                self.set_connected(False)
        return sub_id

    def subscribe_expression(self, expression, callback):
        expr = Expression(self, expression)
        expr.subscribe(callback)
        return expr

    def publish(self, topic, data, retain=False, use_prefix=True):
        if use_prefix:
            topic = "{0}/{1}".format(MQTT.PREFIX, topic)
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
        self.callback(topic, data, unjson=False) # no need to convert JSON back and forth

    def get_cached(self, topic, default=None, use_prefix=True):
        if use_prefix:
            topic = "{0}/{1}".format(MQTT.PREFIX, topic)
        return self.cache[topic] if topic in self.cache else default

    def get_cached_or_raise(self, topic, use_prefix=True):
        if use_prefix:
            topic = "{0}/{1}".format(MQTT.PREFIX, topic)
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
