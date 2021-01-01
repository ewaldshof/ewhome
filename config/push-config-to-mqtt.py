from json import dumps
import paho.mqtt.client as paho
import time
import io
from datetime import datetime
import sys 

from yaml import load
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader, Dumper


config_file = "ewhome.yaml" if len(sys.argv) < 2 else sys.argv[1]

broker_address = "10.0.0.88"
topic_conf_complete = "ewhome/config"
topic_base = "ewhome/"
all_published = False


def read_yaml_file(filename):
    with io.open(filename, mode="r", encoding="utf-8") as file:
        config = load(file, Loader=Loader)
    return config

def add_date(config):
    config["published"]= datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return config

def to_json(config):
    return dumps(config)


def publish_as_json(client, sub_topic, data, with_date = True):
        client.publish(
            topic_base + sub_topic, 
            to_json(add_date(data) if with_date else data), 
            qos=1, 
            retain=True)

def on_connect(client, userdata, flags, rc):
    # publish the old school config topic for all boards that are not updated yet
    #client.publish(topic_conf_complete, data, qos=1, retain=True)

    # and also create one topic per board 
    # this should be the norm for the future
    print(yaml_config["esps"].keys())
    for key, value in yaml_config["esps"].items():
        print(key, value)
        publish_as_json(client, "board/"+key+"/config", value)

    # and also publish room data
    if "raeume" in yaml_config:
        publish_as_json(client, "app/rooms", yaml_config["raeume"], False)

    global all_published
    all_published = True

def on_publish(client, userdata, result):
    if all_published:
        client.disconnect()

def on_log(mqttc, obj, level, string):
    print(string)

def connect_and_push():
    mqtt = paho.Client()
    mqtt.on_connect = on_connect
    mqtt.on_publish = on_publish
    mqtt.on_log = on_log
    mqtt.connect(broker_address)
    mqtt.loop_start()


if __name__ == "__main__":
    yaml_config = read_yaml_file(config_file)
    data = to_json(yaml_config)
    connect_and_push()
    while not all_published:
        time.sleep(0.1)
