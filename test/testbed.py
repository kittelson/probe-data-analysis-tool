import matplotlib.pyplot as plt

fig = plt.figure()
plot = fig.add_subplot(111)
annotation = plot.annotate('local max',xy=(3, 1.5), bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.5))
annotation
# create some curves
for i in range(4):
    plot.plot(
        [i*1,i*2,i*3,i*4],
        gid=i)

def on_plot_hover(event):
    annotated = False
    for curve in plot.get_lines():
        if curve.contains(event)[0]:
            print("over %s" % curve.get_gid())
            annotation.set_text(str(curve.get_gid()))
            print(event.xdata)
            print(event.ydata)
            annotation.set_x(event.xdata)
            annotation.set_y(event.ydata)
            annotation.set_visible(True)
            event.canvas.draw()
            annotated = True
    if not annotated:
        annotation.set_visible(False)
        event.canvas.draw()

fig.canvas.mpl_connect('motion_notify_event', on_plot_hover)
plt.show()

"""
==================================
Modifying the coordinate formatter
==================================

Show how to modify the coordinate formatter to report the image "z"
value of the nearest pixel given x and y
"""
import numpy as np
import matplotlib.pyplot as plt
from mpldatacursor import datacursor



X = 10*np.random.rand(5, 3)

fig, ax = plt.subplots()
px = ax.imshow(X, interpolation='nearest')
ann = ax.annotate('local max', xy=(2, 1), xytext=(3, 1.5))
ann.set_visible(True)

def on_plot_hover(event):
    if event.xdata is not None and event.ydata is not None:
        print(str(int(event.xdata)) + ',' + str(int(event.ydata)))
        ann.set_x(int(event.xdata))
        ann.set_y(int(event.ydata))
        ann.set_text(X[min(int(event.ydata), 4)][min(int(event.xdata), 2)])
        event.canvas.draw()
    else:
        ann.set_visible(False)

datacursor(px)

fig.canvas.mpl_connect('motion_notify_event', on_plot_hover)

plt.show()