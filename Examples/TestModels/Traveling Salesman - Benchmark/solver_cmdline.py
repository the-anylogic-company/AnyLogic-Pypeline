import argparse
import json
from solver import FacilityOrderSolver


parser = argparse.ArgumentParser(description="Solve the traveling salesman problem")
parser.add_argument("-m", "--matrix", type=str, help="Full 2D distance matrix; no whitespace permitted")
parser.add_argument("-o", "--origin", type=int, help="Index of origin facility")
parser.add_argument("-v", "--visit", type=str, help="Number or list of facilities to visit in circuit; pass num to generate, list (w/no whitespace) to solve")
parser.add_argument("-x", "--nowrite", action="store_true", help="Don't overwrite previously saved data")
args = parser.parse_args()


# read from saved data if one or both of (matrix, origin) args is None
# (assumption is that value should be taken from saved data)
do_write = True
updated = False
if args.matrix is None or args.origin is None:
    with open("distanceData.json") as f:
        data = json.load(f)
    matrix = args.matrix or data['matrix']
    # make sure matrix is evaluated as a list
    if isinstance(matrix, str):
        matrix = eval(matrix)
    origin = args.origin or data['origin']
    # won't need to write if both are None (implying to take both from file)
    if args.matrix is None and args.origin is None:
        do_write = False
else: # both are not None, don't need to read
    matrix = eval(args.matrix)
    origin = args.origin
if do_write and not args.nowrite:
    updated = True
    data = {'matrix': matrix, 'origin': origin}
    with open("distanceData.json", "w") as f:
        json.dump(data, f, indent=4)

# either generate list or solve list, depending on what's passed
# (if anything at all)
if args.visit is not None:
    if args.visit.isnumeric():
        n_facilities = int(args.visit)
        order_solver = FacilityOrderSolver(matrix, origin)
        to_visit = order_solver.build_random_order(n_facilities)
        print(to_visit)
    else:
        to_visit = eval(args.visit)
        order_solver = FacilityOrderSolver(matrix, origin)
        solution = order_solver.solve(to_visit)
        print(solution['order'])
else:
    print(updated)
