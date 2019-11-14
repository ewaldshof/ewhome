class Part:

    def __init__(self, config, services):
        self.config = config
        self.services = services
        self.board = services.board
        self.mqtt = services.mqtt
        self.scheduler = services.scheduler

    def boot(self):
        pass


class Services:

    def __init__(self, board, mqtt, scheduler):
        self.board = board
        self.mqtt = mqtt
        self.scheduler = scheduler
