class Part:

    def __init__(self, config, services):
        self.config = config
        self.services = services
        self.board = services.board
        self.mqtt = services.mqtt
        self.scheduler = services.scheduler

    def _listify(self, value):
        return value if type(value) is list else [value]

    def _listify_types(self, value, *types):
        listified = self._listify(value)
        for value in listified:
            self._only_types(value, *types)
        return listified

    def _only_types(self, value, *types):
        if type(value) not in types:
            raise TypeError("value {0} is of type {1} but only {2} accepted".format(
                value, type(value), ", ".join(types)
            ))

    def boot(self):
        pass


class Services:

    def __init__(self, board, mqtt, scheduler):
        self.board = board
        self.mqtt = mqtt
        self.scheduler = scheduler
