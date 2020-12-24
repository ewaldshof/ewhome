from parts import Part

class ConfigDumper(Part):

    @classmethod
    def boot(cls, config):
        print("ConfigDumper booting, my config is:", config)
