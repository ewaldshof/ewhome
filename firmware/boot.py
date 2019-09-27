from board.bohei import Board
from display import Display
from task import Scheduler

board = Board()
board.init()

scheduler = Scheduler()
scheduler.register(board.display)
scheduler.loop_forever(0.1)
