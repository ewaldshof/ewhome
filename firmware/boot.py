from board.bohei import Board
from display import Display
from ewh_net import Network
from task import Scheduler

board = Board()
board.init()

network = Network()
board.display.set_mac(network.mac)

scheduler = Scheduler()
scheduler.register(board.display)
scheduler.loop_forever(0.1)
