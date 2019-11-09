from parts import Part

class ConfigDumper(Part):

    def boot(self):
        print("ConfigDumper booting, my config is:", self.config)
