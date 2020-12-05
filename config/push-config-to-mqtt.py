from json import dumps
import paho.mqtt.client as paho
import time
import io

from yaml import load
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader, Dumper


config_file = "ewhome.yaml"
broker_address = "10.0.0.88"
topic_conf_complete = "ewhome/config"
topic_base = "ewhome/board/"
all_published = False


def read_yaml_file(filename):
    with io.open(filename, mode="r", encoding="utf-8") as file:
        config = load(file, Loader=Loader)
    return config

def to_json(config):
    return dumps(config)

def on_connect(client, userdata, flags, rc):
    #client.publish(topic_conf_complete, data, qos=1, retain=True)
    print(yaml_config["esps"].keys())
    for key, value in yaml_config["esps"].items():
        print(key, value)
        client.publish(
            topic_base + key + "/config", 
            to_json(value), 
            qos=1, 
            retain=True)
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
