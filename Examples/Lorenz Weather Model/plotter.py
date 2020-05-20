from matplotlib import use
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from collections import deque


xs = deque(maxlen=500)
ys = deque(maxlen=500)
zs = deque(maxlen=500)

# Provides better graph drawing (e.g., moving chart w/o locking thread)
# But requires PyQt5 to be installed
#use('Qt5Agg')

fig = plt.figure()
fig.canvas.set_window_title("Lorenz Weather Model - Stock plotting")

ax = fig.add_subplot(111, projection="3d")
ax.set(xlim=[-25, 25], ylim=[-30, 30], zlim=[0, 50])
ax.set_xlabel("X", color="goldenrod", weight="bold")
ax.set_ylabel("Y", color="orangered", weight="bold")
ax.set_zlabel("Z", color="dodgerblue", weight="bold")
plt.tight_layout()

fig.canvas.draw()
bg = fig.canvas.copy_from_bbox(ax.bbox)
plt.show(block=False)

line_color = 'g'
line_style = '-'

line3d, = ax.plot(xs, ys, zs, line_color + line_style)

#### Function called from AL:

def append(x, y, z):
    xs.append(x)
    ys.append(y)
    zs.append(z)

    line3d.set_data_3d(xs, ys, zs)
    fig.canvas.draw()
    fig.canvas.flush_events()






