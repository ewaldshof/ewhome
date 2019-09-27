from board.bohei import Board
from display import Display
from ewh_net import Network
from mqtt import MQTT
from task import Scheduler

board = Board()
board.init()

network = Network()
board.display.set_network(network)

mqtt = MQTT(network)

scheduler = Scheduler()
scheduler.register(board.display)
scheduler.register(network)
scheduler.register(mqtt)

scheduler.loop_forever(0.02)
