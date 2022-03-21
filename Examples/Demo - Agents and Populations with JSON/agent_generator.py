import json
from string import ascii_uppercase
from random import randint, uniform

factory_calls = 0
order_counter = 0

def new_factories_json(count: int) -> str:
    """
    Construct a list of Factory agents as a JSON string.
    """
    global factory_calls
    factories = []
    for index in range(count):
        factory = {"factoryID": f"Fty-{ascii_uppercase[factory_calls]}{index:02d}",
                   "numWorkers": randint(5, 10),
                   "dailyProduction": uniform(10, 30)*100.0,
                   "latitude": uniform(34, 46),
                   "longitude": uniform(-89.5, -118)}
        factories.append(factory)
        
    factory_calls = (factory_calls + 1) % len(ascii_uppercase)
    return json.dumps(factories)

def new_order_json() -> str:
    """
    Construct a new Order agent as a JSON string.
    """
    global order_counter
    order = {"orderID": f"PyOrder{order_counter:03d}",
             "size": randint(100, 500)*10}
    
    order_counter += 1
    return json.dumps(order)

