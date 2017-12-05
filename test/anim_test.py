import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation


# fig = plt.figure()
fig, ax = plt.subplots(subplot_kw=dict(polar=True))

position = np.arange(6) + .5 

plt.tick_params(axis = 'x', colors = '#072b57')
plt.tick_params(axis = 'y', colors = '#072b57')

speeds = [np.random.rand() for el in range(6)]
heights = [0, 0, 0, 0, 0, 0]
rects = plt.bar(position, heights, align = 'center', color = '#b8ff5c') 
plt.xticks(position, ('A', 'B', 'C', 'D', 'E', 'F'))

plt.xlabel('X Axis', color = '#072b57')
plt.ylabel('Y Axis', color = '#072b57')
plt.title('My Chart', color = '#072b57')

plt.ylim((0,1))
plt.xlim((0,6))

plt.grid(True)

rs = [r for r in rects]

def init():
    return rs

def animate(i):
    global rs, heights
    if all(map(lambda x: x == 25, heights)):
        heights = [0, 0, 0, 0, 0, 0]
    else:
        # heights = [h + s / 25 for h, s in zip(heights, speeds)]
        heights = [s * i / 25 for h, s in zip(heights, speeds)]
    for h,r in zip(heights,rs):
        r.set_height(h)
    return rs

# anim = animation.FuncAnimation(fig, animate, init_func=init, frames=25, interval=1, repeat=False, blit=True)

def onclick(event):
    global speeds
    speeds = [np.random.rand() for el in range(6)]
    anim = animation.FuncAnimation(fig, animate, init_func=init, frames=25, interval=1, repeat=False, blit=True)
    plt.show()

fig.canvas.mpl_connect('button_press_event', onclick)

anim = animation.FuncAnimation(fig, animate, frames=25, interval=1, repeat=False, blit=True)

plt.show()