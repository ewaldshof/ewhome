class Name:

    def __init__(self, config, display):
        if display:
            self.display = display
            config.on_update(self.on_update)
            self.on_update(config)

    def on_update(self, config):
        name = "(not configured)"
        mine = config.mine
        version = config.version
        if mine is not None and "name" in mine:
            name = mine["name"]
        self.display.text(name, 0)
        self.display.text(version, 1)
        
