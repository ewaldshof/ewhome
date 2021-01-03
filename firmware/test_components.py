import yaml
from components import Component, Signal


yaml_string1  = """
assign:
    sumabs: in1 + abs(in2)    
"""
yaml_string2  = """
proportional:
    first_prop:
        sensor: sensor_intput
        midpoint: 20
        spread: 2
    second_prop:
        sensor: first_prop
        midpoint: 20
        spread: 2
       
"""
print(yaml_string1)
config = yaml.safe_load(yaml_string1)
Component.netlist_from_config(config)
Component.print_netlist()
print("update")
Signal.set_by_name("in1", 7.5)
Signal.set_by_name("in2", -3)
Component.print_netlist()
#Signal.set_by_name("trigger_input", 0.5)
#Component.print_netlist()
