import numpy as np
from scipy import optimize
from typing import List, Dict

VERBOSE = False

class SupplyChainOptimization:
    def __init__(self, factory_outputs, warehouse_capacities,
                 customer_demands, shipping_costs):
##        # validate totals
##        assert sum(factory_outputs) >= sum(customer_demands), "Customers demand more than can be produced...open a new factory?"
        
        self.factory_outputs = factory_outputs
        self.num_fty = len(factory_outputs)

        self.warehouse_capacities = warehouse_capacities
        self.num_wh = len(warehouse_capacities)

        self.customer_demands = customer_demands
        self.num_cus = len(customer_demands)

        self.shipping_costs = shipping_costs

    
    def factory_produce_constr(self, x, fty_idx): # ineq
        # check factory `fty_idx` isn't producing more than it can
        # (total from factory <= factory producible)
        
        # add producing amount sent to all warehouses
        _start_index = fty_idx * self.num_wh
        num_producing = sum(x[_start_index : _start_index + self.num_wh])

        if VERBOSE: print(f"Factory {fty_idx} produces {num_producing} to wh, ", end="")
        
        # add producing amount sent to all customers
        _start_index = self.num_fty*self.num_wh + self.num_wh*self.num_cus + self.num_cus*fty_idx
        num_producing += sum(x[_start_index : _start_index + self.num_cus])
        
        if VERBOSE: print(f"{num_producing} with customers")
        
        return self.factory_outputs[fty_idx] - num_producing


    def warehouse_cap_constr(self, x, wh_idx): # ineq
        # check warehouse `wh_idx` isn't holding more than it can
        # (total to warehouse <= warehouse capacity)
        
        num_holding = 0
        for fty_idx in range(self.num_fty):
            # add holding amount from factory `fty_idx`
            num_holding += x[wh_idx + fty_idx*self.num_wh]
            
        if VERBOSE: print(f"Warehouse {wh_idx} holding {num_holding}")
        
        return self.warehouse_capacities[wh_idx] - num_holding


    def warehouse_io_constr(self, x, wh_idx): # eq
        # checkhouse warehouse `wh_idx` is sending as much as it receives
        # (total to warehouse == total from warehouse)

        num_holding = 0
        for fty_idx in range(self.num_fty):
            # add holding amount from factory `fty_idx`
            num_holding += x[wh_idx + fty_idx*self.num_wh]

        offset_index = self.num_fty*self.num_wh # start of warehouse/customer section of list
        _start_index = offset_index + self.num_cus * wh_idx
        num_sending = sum(x[_start_index : _start_index + self.num_cus])

        if VERBOSE: print(f"Warehouse {wh_idx} holding {num_holding}, sending {num_sending}")

        return num_holding - num_sending

        
    def customer_receive_constr(self, x, cus_idx): # ineq
        # check customer `cus_idx` is receiving all that it demands
        # (total to customer >= demand)
        
        num_receiving = 0
        offset_index = self.num_fty * self.num_wh # start of warehouse/customer section
        for wh_idx in range(self.num_wh):
            # add receiving amount from warehouse `wh_idx`
            num_receiving += x[offset_index + wh_idx*self.num_cus + cus_idx]

        if VERBOSE: print(f"Customer {cus_idx} receiving {num_receiving} from wh, ", end="")

        offset_index = self.num_fty*self.num_wh + self.num_wh*self.num_cus # start of factory/customer section
        for fty_idx in range(self.num_fty):
            # add receiving amount from factory `fty_idx`
            num_receiving += x[offset_index + fty_idx*self.num_cus + cus_idx]

        if VERBOSE: print(f"{num_receiving} with factory")
            
        return num_receiving - self.customer_demands[cus_idx]


    def make_constraints(self):
        cons = []
        for i in range(self.num_fty):
            dct1 = {'type': 'ineq', 'fun': self.factory_produce_constr, 'args': (i,)}
            cons.append(dct1)
        for i in range(self.num_wh):
            dct2 = {'type': 'ineq', 'fun': self.warehouse_cap_constr, 'args': (i,)}
            cons.append(dct2)
            
            dct3 = {'type': 'eq', 'fun': self.warehouse_io_constr, 'args': (i,)}
            cons.append(dct3)
        for i in range(self.num_cus):
            dct4 = {'type': 'ineq', 'fun': self.customer_receive_constr, 'args': (i,)}
            cons.append(dct4)
        return cons


    def make_input_vars(self):
        return np.zeros((self.num_fty*self.num_wh + self.num_wh*self.num_cus + self.num_fty*self.num_cus,))


    def make_bounds(self):
        return [(0, None) for _ in range(self.num_fty*self.num_wh + self.num_wh*self.num_cus + self.num_fty*self.num_cus)]


    def objective(self, x):
        return (self.shipping_costs * x).sum()


    def solve(self):
        constraints = self.make_constraints()
        bounds = self.make_bounds()
        x0 = self.make_input_vars()

        sln = optimize.minimize(self.objective, x0,
                                bounds=bounds,
                                constraints=constraints)
        return sln   
        
    

    
    
