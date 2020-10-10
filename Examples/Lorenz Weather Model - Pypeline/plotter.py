import matplotlib
from matplotlib import use
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from collections import deque

# Provides better graph drawing (e.g., moving chart w/o locking thread)
# But requires PyQt5 to be installed
#use('Qt5Agg')

# creation of figure
fig = plt.figure()
fig.canvas.set_window_title("Lorenz Weather Model - Stock plotting")

# limit size to the same as default size of datasets in AL model
xs = deque(maxlen=500)
ys = deque(maxlen=500)
zs = deque(maxlen=500)

# create 3d plot
ax = fig.add_subplot(111, projection="3d")
ax.set(xlim=[-25, 25], ylim=[-30, 30], zlim=[0, 50])
ax.set_xlabel("X", color="goldenrod", weight="bold")
ax.set_ylabel("Y", color="orangered", weight="bold")
ax.set_zlabel("Z", color="dodgerblue", weight="bold")

# initial drawing and showing
fig.canvas.draw()
bg = fig.canvas.copy_from_bbox(ax.bbox)
plt.show(block=False)

line_color = 'g'
line_style = '-'

line3d, = ax.plot(xs, ys, zs, line_color + line_style)

#### Functions called from AL:

def set_inputs(S: float, R: float, B: float) -> None:
    """ Update the plot's title based on the inputs of the AL model """
    ax.set_title(f"S={S:.2f}", loc='left', color="goldenrod")
    ax.set_title(f"R={R:.2f}", loc='center', color="orangered")
    ax.set_title(f"B={B:.2f}", loc='right', color="dodgerblue")
    plt.tight_layout()

def move_figure(x, y):
    """ Move figure's upper left corner to pixel (x, y) """
    backend = matplotlib.get_backend()
    if backend == 'TkAgg':
        fig.canvas.manager.window.wm_geometry("+%d+%d" % (x, y))
    elif backend == 'WXAgg':
        fig.canvas.manager.window.SetPosition((x, y))
    else:
        # This works for QT and GTK
        # You can also use window.setGeometry
        fig.canvas.manager.window.move(x, y)
    
def append(x: float, y: float, z: float) -> None:
    """ Append the provided point to the datasets and redraw the plot """
    xs.append(x)
    ys.append(y)
    zs.append(z)

    line3d.set_data_3d(xs, ys, zs)
    fig.canvas.draw()
    fig.canvas.flush_events()






