class Name:

    def __init__(self, config, display):
        self.display = display
        config.on_update(self.on_update)
        self.on_update(config)

    def on_update(self, config):
        name = "(not configured)"
        mine = config.mine
        if mine is not None and "name" in mine:
            name = mine["name"]
        self.display.text(name, 0)