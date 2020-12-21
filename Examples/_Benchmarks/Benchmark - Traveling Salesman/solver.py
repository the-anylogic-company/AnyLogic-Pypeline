# A traveling salesman problem solver - designed for AnyLogic

import numpy as np
import random
random.seed(1)
from typing import List, Dict, Any
from ortools.constraint_solver import routing_enums_pb2, pywrapcp
from ortools.constraint_solver.pywrapcp import RoutingIndexManager, RoutingModel, Assignment

class FacilityOrderSolver:
    def __init__(self, full_distance_matrix: List[List[float]], home_index: int):
        """Create a new solver object based on the supplied route information.

        Parameters
        ----------
        full_distance_matrix : List[List[float]]
            A 2D square matrix representing the distance between all facilities.
            The data is expected to be mirrored over the
            main diagonal (which itself is expected to be 0s).
            The number of facilities is implied to be the length of the matrix.
        home_index : int
            The index of the facility designated as the "home" or origin point.
        """
        # matrix needs to be ints, so scale up before converting
        self.matrix = (np.array(full_distance_matrix)*100).astype(np.int32)
        self.home_index = home_index


    def _create_data_model(self, indices_to_visit: List[int] = None) -> Dict[str, Any]:
        """Stores the data for the problem

        Parameters
        ----------
        indices_to_visit : List[int]
            The list of indices corresponding to the desired facilities to visit.

        Note
        ----
        In this context, the index of the home facility is made relative to the list
        of facilities to visit (as opposed to the list of all facilties).
        This is needed to comply with how the solver works based on the example by Google.

        Returns
        -------
        Dict[str, Any]
            With keys:
            - 'distance_matrix', set to original or rearranged distance matrix
            - 'num_vehicles', set to 1
            - 'home', set to the relative index of the home facility

        """
        # slice the master matrix so that only the desired indices are included
        # (or don't slice if all are desired)
        if indices_to_visit is None:
            relative_home_index = self.home_index
            matrix = self.matrix
        else:
            relative_home_index = indices_to_visit.index(self.home_index)
            matrix = np.rot90(np.rot90(self.matrix[ indices_to_visit ], k=-1)[ indices_to_visit ], k=1)
        data = {'distance_matrix': matrix,
            'num_vehicles': 1,
            'home': relative_home_index}
        return data


    def _extract_solution(self, manager: RoutingIndexManager, routing: RoutingModel, assignment: Assignment, indices_to_visit: List[int]) -> Dict[str, Any]:
        """Transform results to a usable format

        Parameters
        ----------
        manager : RoutingIndexManager
            OR-tools' object to manage conversion between NodeIndex and variable index
        routing : RoutingModel
            OR-tools' object for route solving
        assignment : Assignment
            OR-tools' object for mapping from variable to domains
        indices_to_visit : List[int]
            The list of indices corresponding to the desired facilities to visit        

        Returns
        -------
        Dict[str, Any]
            With keys:
            - 'objective', set to objective value (minified distance)
            - 'order', instructions for the order of facilities to visit

        """
        sln = {"objective": assignment.ObjectiveValue()}
    
        stop_indices = []
        index = routing.Start(0)
        while not routing.IsEnd(index):
            relative_index = manager.IndexToNode(index)
            stop_indices.append(indices_to_visit[relative_index])
            previous_index = index
            index = assignment.Value(routing.NextVar(index))
        relative_index = manager.IndexToNode(index)
        stop_indices.append(indices_to_visit[relative_index])
        sln["order"] = stop_indices
        return sln

    def build_random_order(self, n_facilities: int) -> List[int]:
        """Randomly samples a given number of facilities from the total number."""
        n_total = len(self.matrix)
        return sorted(random.sample( set(range(n_total)) - set([self.home_index]), n_facilities) + [self.home_index])

    def solve(self, indices_to_visit: List[int] = None) -> Dict[str, Any]:
        """Finds the optimal order of facilities to minimize distance.

        Parameters
        ----------
        indices_to_visit : List[int]
            The list of indices corresponding to the desired facilities to visit

        Returns
        -------
        Dict[str, Any]
            Soltution dictionary with keys:
            - 'objective', set to objective value (minified distance)
            - 'order', instructions for the order of facilities to visit
        """
        if indices_to_visit is None:
            indices_to_visit = list(range(len(self.matrix)))
            
        # make sure home location is in the listed, and that the list is sorted
        if self.home_index not in indices_to_visit:
            indices_to_visit.append(self.home_index)
        indices_to_visit.sort()
        
        data = self._create_data_model(indices_to_visit)

        # create routing index manager
        manager = RoutingIndexManager(len(data['distance_matrix']),
                                           data['num_vehicles'], data['home'])

        # create routing model
        routing = RoutingModel(manager)

        def distance_callback(from_index, to_index):
            # returns distance between two nodes
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            dist = data['distance_matrix'][from_node][to_node]

            return dist

        transit_callback_index = routing.RegisterTransitCallback(distance_callback)

        # define cost of each arc
        routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

        # set first solution heuristic
        search_params = pywrapcp.DefaultRoutingSearchParameters()
        search_params.first_solution_strategy = (routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)

        # solve problem
        assignment = routing.SolveWithParameters(search_params)

        return self._extract_solution(manager, routing, assignment, indices_to_visit)



def test(indices_to_visit = None):
    """ Demonstrates a sample solution """
    ##0 Chicago
    ##1 New York City
    ##2 Los Angeles
    ##3 Minneapolis
    ##4 Denver
    ##5 Dallas
    ##6 Seattle
    ##7 Boston
    ##8 San Francisco
    ##9 St. Louis
    ##10 Houston
    ##11 Phoenix
    ##12 Salt Lake City
    ##13 Miami
    ##14 Atlanta
    ##15 Kansas City
    home_index = 15 # Kansas city
    # 15x15 matrix with main diagonal consisting of 0s and to which data is mirrored along
    # (values are derived from external resource and multiplied by 1000 for higher accuracy)
    matrix = np.array([[0.0, 1148413.3550047704, 2813453.6297408855, 572861.4368351421, 1483440.7452179305, 1296355.2188721865, 2801269.1215845253, 1370943.3069385102, 2996683.256068982, 422589.4697157836, 1515737.0196676727, 2343639.7107855356, 2031500.319603397, 1913900.3015914203, 946854.1020487415, 665894.0336505901],
               [1148413.3550047704, 0.0, 3949451.153672887, 1642119.4792808082, 2628946.6435325537, 2212019.1209020815, 3882177.952930788, 306997.0343229422, 4144977.810718553, 1408454.3261387087, 2286054.8575902223, 3455343.3108375454, 3179102.5335818897, 1754834.3710577146, 1202616.154562711, 1766599.1336905772],
               [2813453.6297408855, 3949451.153672887, 0.0, 2455296.3791196346, 1339227.410707824, 1998182.1420783552, 1545364.434045008, 4184394.186016967, 559978.4273194656, 2560790.9591738936, 2212581.51715849, 575975.8749662543, 933602.6426595236, 3767490.41517038, 3120118.850020503, 2186473.1552241463],
               [572861.4368351421, 1642119.4792808082, 2455296.3791196346, 0.0, 1127312.7583590776, 1390159.7734006236, 2249169.1308160927, 1811513.5290266906, 2554165.8167895717, 750916.7305340832, 1701189.1538312144, 2062079.2399570548, 1590460.9488364782, 2434801.332310659, 1462408.5353501518, 662752.1291133759],
               [1483440.7452179305, 2628946.6435325537, 1339227.410707824, 1127312.7583590776, 0.0, 1067257.7993323756, 1646308.7967673023, 2852307.4164419994, 1530510.2790658756, 1283707.511393525, 1414308.8805983758, 943721.1931707633, 598728.757362067, 2779561.192116527, 1952618.0544916363, 899656.1020173575],
               [1296355.2188721865, 2212019.1209020815, 1998182.1420783552, 1390159.7734006236, 1067257.7993323756, 0.0, 2709804.112590561, 2500314.4507069485, 2390841.4329337194, 882457.80942383, 361482.7025425731, 1427995.4150203674, 1610768.421819668, 1788903.6065106322, 1161480.3557326929, 730446.8613086065],
               [2801269.1215845253, 3882177.952930788, 1545364.434045008, 2249169.1308160927, 1646308.7967673023, 2709804.112590561, 0.0, 4018059.834330202, 1093104.7332788548, 2778905.575804111, 3046648.362755992, 1794989.6453295103, 1129464.5539648102, 4404737.747850686, 3516794.375197078, 2427457.036285458],
               [1370943.3069385102, 306997.0343229422, 4184394.186016967, 1811513.5290266906, 2852307.4164419994, 2500314.4507069485, 4018059.834330202, 0.0, 4350710.853063807, 1673216.4080939887, 2586942.3262796295, 3706392.097841614, 3382851.415271485, 2022974.6418062754, 1509585.60107986, 2015770.1390589625],
               [2996683.256068982, 4144977.810718553, 559978.4273194656, 2554165.8167895717, 1530510.2790658756, 2390841.4329337194, 1093104.7332788548, 4350710.853063807, 0.0, 2812916.3098878833, 2650547.941880299, 1053620.7288649315, 967859.8344376946, 4179636.203479384, 3448359.745690545, 2428862.4239271535],
               [422589.4697157836, 1408454.3261387087, 2560790.9591738936, 750916.7305340832, 1283707.511393525, 882457.80942383, 2778905.575804111, 1673216.4080939887, 2812916.3098878833, 0.0, 1093601.4408876144, 2050115.5214378452, 1872971.1741522516, 1708236.6189296674, 752855.8488125347, 384122.2000072272],
               [1515737.0196676727, 2286054.8575902223, 2212581.51715849, 1701189.1538312144, 1414308.8805983758, 361482.7025425731, 3046648.362755992, 2586942.3262796295, 2650547.941880299, 1093601.4408876144, 0.0, 1636770.4499809493, 1932616.2801687205, 1559260.024532222, 1130480.278513877, 1039856.4844335921],
               [2343639.7107855356, 3455343.3108375454, 575975.8749662543, 2062079.2399570548, 943721.1931707633, 1427995.4150203674, 1794989.6453295103, 3706392.097841614, 1053620.7288649315, 2050115.5214378452, 1636770.4499809493, 0.0, 812548.5062332726, 3191662.5092484164, 2564665.4531581327, 1690942.142157212],
               [2031500.319603397, 3179102.5335818897, 933602.6426595236, 1590460.9488364782, 598728.757362067, 1610768.421819668, 1129464.5539648102, 3382851.415271485, 967859.8344376946, 1872971.1741522516, 1932616.2801687205, 812548.5062332726, 0.0, 3364908.7076308434, 2551338.215149899, 1490589.7393085626],
               [1913900.3015914203, 1754834.3710577146, 3767490.41517038, 2434801.332310659, 2779561.192116527, 1788903.6065106322, 4404737.747850686, 2022974.6418062754, 4179636.203479384, 1708236.6189296674, 1559260.024532222, 3191662.5092484164, 3364908.7076308434, 0.0, 973244.7750437199, 2000112.4162614697],
               [946854.1020487415, 1202616.154562711, 3120118.850020503, 1462408.5353501518, 1952618.0544916363, 1161480.3557326929, 3516794.375197078, 1509585.60107986, 3448359.745690545, 752855.8488125347, 1130480.278513877, 2564665.4531581327, 2551338.215149899, 973244.7750437199, 0.0, 1089830.6426635552],
               [665894.0336505901, 1766599.1336905772, 2186473.1552241463, 662752.1291133759, 899656.1020173575, 730446.8613086065, 2427457.036285458, 2015770.1390589625, 2428862.4239271535, 384122.2000072272, 1039856.4844335921, 1690942.142157212, 1490589.7393085626, 2000112.4162614697, 1089830.6426635552, 0.0]])

    solver = FacilityOrderSolver(matrix, home_index)
    
    return solver.solve(indices_to_visit)

# won't execute unless this file is directly run
# (importing this file wont trigger)
if __name__ == "__main__":
    from pprint import pprint
    from random import sample
    from time import time
    
    print("Visiting all :")
    _start = time()
    pprint(test())
    _elapsed = time() - _start
    print(f"= {_elapsed:5.3f} seconds\n")

    rand_cities = sample(range(15),5)
    print("Visiting", rand_cities, ":")
    _start = time()
    pprint(test(rand_cities))
    _elapsed = time() - _start
    print(f"= {_elapsed:5.3f} seconds\n")
