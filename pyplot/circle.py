#!/usr/bin/python


import matplotlib.pyplot as plt
from matplotlib.patches import Circle

# create a figure and axis
fig, ax = plt.subplots()

# create a circle
circle = Circle((0, 0), radius=1, fill=False)

# add the circle to the axis
ax.add_patch(circle)

# set the axis limits
ax.set_xlim(-1.5, 1.5)
ax.set_ylim(-1.5, 1.5)

# show the plot
plt.show()

