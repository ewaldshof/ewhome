class Part:

    #services are identical over all parts
    @staticmethod   
    def setup_services(board, mqtt, scheduler):
        Part.board = board
        Part.mqtt = mqtt
        Part.scheduler = scheduler



    @classmethod
    def boot(cls, config):
        cls.instances = {}
        for key, content in config.items():
            cls.instances[key] = cls(key, content)

    
