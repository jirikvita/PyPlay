#!/usr/bin/python

# 6.11.2021
# jk according to https://stackoverflow.com/questions/36816537/spherical-coordinates-plot-in-matplotlib

import numpy as np
import matplotlib.pyplot as plt
import mpl_toolkits.mplot3d.axes3d as axes3d

npt, npp = 64, 64
theta, phi = np.linspace(0, 2*np.pi, npt), np.linspace(0, np.pi, npp)
THETA, PHI = np.meshgrid(theta, phi)

# https://en.wikipedia.org/wiki/Table_of_spherical_harmonics#%E2%84%93_=_3
# palettes:
# https://matplotlib.org/stable/tutorials/colors/colormaps.html


Rs = [1.,
      #np.power(np.cos(PHI), 2),
      #np.power(np.sin(PHI)*np.cos(PHI), 2),
      np.power(3.*np.power(np.cos(PHI),2) - 1, 2),
      #np.power(np.cos(PHI), 4),
      #np.power(5.*np.power(np.cos(PHI),3) - 3*np.cos(PHI), 2),
      #np.power(5.*np.power(np.cos(PHI),2) - 1, 2),
]

i=-1

for R in Rs:

    i = i+1
    X = R * np.sin(PHI) * np.cos(THETA)
    Y = R * np.sin(PHI) * np.sin(THETA)
    Z = R * np.cos(PHI)
    
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1, projection='3d')
    plot = ax.plot_surface(
        # viridis, hot, hsv, jet, gist_rainbow
        X, Y, Z,
        rstride=1, cstride=1,
        cmap=plt.get_cmap('gist_rainbow'),
        linewidth=0, antialiased=False, alpha=0.5)

    plt.savefig('harmSq_{}.png'.format(i))
    plt.show()

