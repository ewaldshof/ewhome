import yaml
from components import Component, Signal


yaml_string  = """
proportional:
    first_prop:
        sensor: sensor_input
        midpoint: 20
        spread: 2
    second_prop:
        sensor: first_prop
        midpoint: 20
        spread: 2
       
"""
print(yaml_string)
config = yaml.safe_load(yaml_string)

p = config["proportional"]
print(type(p["first_prop"]))

Component.netlist_from_config(config)
Component.print_netlist()
Signal.set_by_name("sensor_input", 20.5)
Component.print_netlist()
