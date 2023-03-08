# Gets the model inputs for the parameters variation experiment

def get_num_workers(iteration_index: int) -> int:
    """ Starts at 1 and increases by 1 every three iterations. """
    return (iteration_index // 3) + 1

def get_arrival_rate(iteration_index: int) -> float:
    """ Cycles between [1,2,3] """
    return (iteration_index % 3) + 1.0

def get_mean_delay_time(iteration_index: int) -> float:
    """ Always returns 1 """
    return 1.0
