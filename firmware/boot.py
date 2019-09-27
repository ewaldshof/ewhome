from board.bohei import Board
from config import Config
from display import Display
from ewh_net import Network
from heartbeat import Heartbeat
from mqtt import MQTT
from task import Scheduler

board = Board()
board.init()

heartbeat = Heartbeat(board.display)

network = Network()
board.display.set_network(network)

mqtt = MQTT(network)
board.display.set_mqtt(mqtt)

config = Config(network, mqtt)
def config_update(config):
    print(config.get_mine())
config.on_update(config_update)

scheduler = Scheduler()
scheduler.register(board.display)
scheduler.register(heartbeat)
scheduler.register(network)
scheduler.register(mqtt)

scheduler.loop_forever(0.02)
