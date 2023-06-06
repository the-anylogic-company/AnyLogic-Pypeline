# This script has functions to get inputs for the parameters variation experiment,
#   and to process the outputs.

from typing import Optional
try:
    import os
    import numpy as np
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.ticker as plticker
    from  matplotlib.colors import LinearSegmentedColormap
    from mpl_toolkits.mplot3d import Axes3D
    IMPORT_SUCCESS = True
except ModuleNotFoundError:
    IMPORT_SUCCESS = False
    

def get_num_workers(iteration_index: int) -> int:
    """ Starts at 4 and increases by 1 every three iterations. """
    return (iteration_index // 3) + 4

def get_arrival_rate(iteration_index: int) -> float:
    """ Starts at 1.5 and increases by 0.5 for every three iterations. """
    return (iteration_index % 3)/2 + 1.5

def reset():
    """
        Clears the log file and the removes the generated image.
        Called at the start of each experiment run.
    """
    with open("model_outputs_log.csv", "w") as _:
        pass
    
    try:
        os.remove("model_outputs_3d.png")
    except FileNotFoundError:
        pass

def log_outputs(num_workers: int, arrival_rate: float, queue_time: float):
    """
        Write the given input/output data to a local log file.
        Called at the end of each run
    """
    with open("model_outputs_log.csv", "a") as outfile:
        outfile.write(f"{num_workers},{arrival_rate},{queue_time}\n")

def save_results() -> Optional[bool]:
    """
        Reads the local log file to generate and save a 3D plot.
        The filename is returned (or None if the libraries could not be imported).
    """
    if not IMPORT_SUCCESS:
        return None

    fig = plt.figure()
    fig.set_tight_layout(True)

    ax = fig.add_subplot(projection='3d')
    ax.set_title("Experiment run results")
    ax.set_xlabel("# Workers")
    ax.set_ylabel("Arrival Rate (per sec)") 
    ax.set_zlabel("Queue time (sec)")
    
    array = np.loadtxt("model_outputs_log.csv", delimiter=",", ndmin=2)
    if array.size > 0:  # at least one data point
        x = array[:,0]
        y = array[:,1]
        z = array[:,2]
        
        # set color based on z values
        cmap = LinearSegmentedColormap.from_list('gr',["green", "yellow", "red"], N=256)
        colors = cmap( (z-z.min())/(z.max()-z.min()) )

        # make bars somewhat smaller (e.g., 90%) than distance between points
        width, depth = 1*0.5, 0.5*0.5
        
        ax.bar3d(x, y, np.zeros_like(z), width, depth, z, shade=True, color=colors)

        # update tick interval based on predetermined step sizes
        ax.xaxis.set_major_locator(plticker.MultipleLocator(base=1.0))
        ax.yaxis.set_major_locator(plticker.MultipleLocator(base=0.5))
        
    filename = "model_outputs_3d.png"
    fig.savefig(filename)
    return filename
    
    
