class Part:

    def __init__(self, config, services):
        self.config = config
        self.services = services
        self.board = services.board
        self.mqtt = services.mqtt

    def boot(self):
        pass


class Services:

    def __init__(self, board, mqtt):
        self.board = board
        self.mqtt = mqtt
