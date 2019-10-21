from board.bohei import Board
from config import Config
from display import Display
from ewh_net import Network
from heartbeat import Heartbeat
from name import Name
from mqtt import MQTT
from task import Scheduler

__version__ = "0.2.0"

board = Board()
board.init()

heartbeat = Heartbeat(board.display)

network = Network()
if board.display:
    board.display.set_network(network)

mqtt = MQTT(network)
if board.display:
    board.display.set_mqtt(mqtt)
board.temperature.mqtt = mqtt

config = Config(network, mqtt)

name = Name(config, board.display)

scheduler = Scheduler()
if board.display:
    scheduler.register(board.display)
scheduler.register(board.temperature)
scheduler.register(heartbeat)
scheduler.register(network)
scheduler.register(mqtt)

scheduler.start(100)
