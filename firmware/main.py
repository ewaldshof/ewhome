from board.bohei import Board
from config import Config
from display import Display
from ewh_net import Network
from heartbeat import Heartbeat
from name import Name
from mqtt import MQTT
from task import Scheduler
import ntptime

network = Network()
MQTT.init(network)

board = Board(network)
board.init()


heartbeat = Heartbeat(board.display)


scheduler = Scheduler()

config = Config(board, network, scheduler)

name = Name(config, board.display) 
scheduler.register(board.display)
scheduler.register(heartbeat)
scheduler.register(network)
scheduler.register(MQTT.task)

print("Starting scheduler of version {0}".format(config.version))

scheduler.start(100)

