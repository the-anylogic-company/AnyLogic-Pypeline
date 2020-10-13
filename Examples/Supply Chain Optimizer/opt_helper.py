import json
import numpy as np
from math import ceil
from operator import itemgetter
from optimizer import SupplyChainOptimization

def parse_input(raw_model_data):
    """ Take JSON input and output the proper lists for solving """
    model_data = json.loads(raw_model_data)

    # get each population and sort by provided index key
    factory_data = sorted(model_data.get("factories", []), key=lambda x: x['_index'])
    warehouse_data = sorted(model_data.get("warehouses", []), key=lambda x: x['_index'])
    customer_data = sorted(model_data.get("customers", []), key=lambda x: x['_index'])

    # get item quantities (e.g., input/demand, output, storage/capacity) for each population
    factory_outputs = [x['output'] for x in factory_data]
    warehouse_capacities = [x['capacity'] for x in warehouse_data]
    customer_demands = [x['demand'] for x in customer_data]

    # build shipping costs array:
    #   factory -> warehouse (f2w), warehouse -> customer (w2c), factory -> customer (f2c)
    costs_f2w, costs_w2c, costs_f2c = [], [], []
    
    for factory in factory_data:
        # sort each pairs by key name before appending costs to respective lists
        pairs_2w = sorted(factory['warehouseCostMap'].items(), key=itemgetter(0))
        costs_f2w += [x[1] for x in pairs_2w]
        
        pairs_2c = sorted(factory['customerCostMap'].items(), key=itemgetter(0))
        costs_f2c += [x[1] for x in pairs_2c]
        
    for warehouse in warehouse_data:
        # sort pairs by key name before appending costs to respective list
        pairs_2c = sorted(warehouse['customerCostMap'].items(), key=itemgetter(0))
        costs_w2c += [x[1] for x in pairs_2c]

    costs = costs_f2w + costs_w2c + costs_f2c

    return factory_outputs, warehouse_capacities, customer_demands, costs


def _build_order(source_type, source_index, dest_type, dest_index, amount):
    order = dict()
    order['source_type'] = source_type
    order['source_index'] = source_index
    order['destination_type'] = dest_type
    order['destination_index'] = dest_index
    order['amount'] = ceil(amount*10)/10
    return order


def interpret_output(optimized_result, num_factories, num_warehouses, num_customers):
    info_data = dict()
    info_data['cost'] = round(optimized_result.fun, 2)
    info_data['is_successful'] = optimized_result.success.item() # convert np.bool_ to python bool for json dumping
    info_data['message'] = optimized_result.message
    
    var_array = optimized_result.x
    # The first `num_factories` rows ship from factories at the row to each warehouse.
    # The next `num_warehouses` rows ship from warehouses at the row to each customer.
    # The last `num_factories` rows ship from factories at the row to each customer.
    # Split the array accordingly:
    amounts_f2w, amounts_w2c, amounts_f2c = \
                 np.split(var_array,
                          [num_factories*num_warehouses, var_array.size-num_factories*num_customers])

    # Reshape each 1D amounts list so it can be indexed by individual facility (i.e., into 2D lists)
    # (for json dumping, round and convert numpy list -> python list)
    # Sample output: ```amounts_f2w = [[3.0, 20.0, 0.0, 15.0], [0.0, 0.0, 13.33333, 0.0]]
    #                   => factory[0] sends 3 product to warehouse[0], 20 to warehouse[1], ...```
    amounts_f2w = amounts_f2w.reshape((num_factories, -1)).round(3).tolist()
    amounts_w2c = amounts_w2c.reshape((num_warehouses, -1)).round(3).tolist()
    amounts_f2c = amounts_f2c.reshape((num_factories, -1)).round(3).tolist()

    # Look into each amounts list and convert to orders agent dictionary
    # (ignoring any with order size of 0)
    orders_data = []
    for factory_index in range(num_factories):
        # add orders going from factories -> warehouses
        for warehouse_index, amount in enumerate(amounts_f2w[factory_index]):
            if amount > 0:
                orders_data.append(_build_order('f', factory_index, 'w', warehouse_index, amount))
        # add orders going from factories -> customers
        for customer_index, amount in enumerate(amounts_f2c[factory_index]):
            if amount > 0:
                orders_data.append(_build_order('f', factory_index, 'c', customer_index, amount))

    for warehouse_index in range(num_warehouses):
        # add orders going from warehouses -> customers
        for customer_index, amount in enumerate(amounts_w2c[warehouse_index]):
            if amount > 0:
                orders_data.append(_build_order('w', warehouse_index, 'c', customer_index, amount))

    return info_data, orders_data    
    
    
def find_solution(raw_model_data):
    # convert the provided JSON to a series of lists the solver can use
    input_lists = parse_input(raw_model_data)
    # create an instance of the `Solver` class
    solver = SupplyChainOptimization(*input_lists)
    # tell it to find the optimal solution
    optimized_solution = solver.solve()
    # convert the object (a class from SciPy) to a format that can be JSON-ified in AL
    json_data = dict(zip(
        ['info', 'orders'],
        [json.dumps(data) for data in interpret_output(optimized_solution, solver.num_fty, solver.num_wh, solver.num_cus)]))
    return optimized_solution, json_data


def generate_dot(solution, only_body=False, one_line=False):
    if type(solution) != np.ndarray:
        array = solution.x
    else:
        array = solution

    amounts_f2w, amounts_w2c, amounts_f2c = np.split(array, [8, 28])
    amounts_f2w = amounts_f2w.reshape((2, -1)).round(5).tolist()
    amounts_w2c = amounts_w2c.reshape((4, -1)).round(5).tolist()
    amounts_f2c = amounts_f2c.reshape((2, -1)).round(5).tolist()

    with open("temp.txt","w") as f:
        f.write("F2W -> " + str(amounts_f2w))
        f.write("W2C -> " + str(amounts_w2c))
        f.write("F2C -> " + str(amounts_f2c))

    source = "\toverlap=false\n\tsubgraph {\n\t\trank1 [style=invisible];\n"
    if not only_body:
        source = "digraph {\n" + source
    
    for i in range(len(amounts_f2w)):
        a_2c = amounts_f2c[i]
        for j,a in enumerate(a_2c):
            if a > 0:
                source += f"\t\tF{i+1} -> C{j+1} [label={a}]\n"
            
        a_2w = amounts_f2w[i]
        for j,a in enumerate(a_2w):
            if a > 0:
                source += f"\t\tF{i+1} -> W{j+1} [label={a}]\n"

    for i in range(len(amounts_w2c)):
        a_2c = amounts_w2c[i]
        for j,a in enumerate(a_2c):
            if a > 0:
                source += f"\t\tW{i+1} -> C{j+1} [label={a}]\n"

    # if more than 1 factories is used, make invisible line so that F1 is first
    if len(amounts_f2w) > 1:
        source += "\t\trank1 " + " ".join(f"-> F{i+1}" for i in range(len(amounts_f2w))) + "[style=invis];\n"
    # add rank text
    _rank_f = "\t\t{rank = same; " + " ".join(f"F{i+1};" for i in range(2)) + "}\n"
    _rank_c = "\t\t{rank = same; " + " ".join(f"C{i+1};" for i in range(5)) + "}\n"
    source += _rank_f + _rank_c + "\t}"
    if not only_body:
        source += "\n}"
    if one_line:
        source = source.replace("\t", " ").replace("\n", " ")
    return source
