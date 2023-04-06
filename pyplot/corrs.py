#!/usr/bin/python

import numpy as np
import matplotlib.pyplot as plt

# generate two random datasets
#x = np.random.rand()
#y = np.random.rand()

# jk
# https://numpy.org/doc/stable/reference/random/generated/numpy.random.normal.html

# https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.hist.html
# https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.scatter.html

Ngen = 500
off = 25.

x = np.random.normal(0, 10, Ngen)
d = np.random.normal(0, 2, Ngen) + off
y = x + d

xmean = x.mean()
xstd = x.std()
ymean = y.mean()
ystd = y.std()


xmin = min(x)
ymin = min(y)
xymin = min(xmin, ymin)

xmax = max(x)
ymax = max(y)
xymax = max(xmax, ymax)


# calculate the correlation coefficient
corr = np.corrcoef(x, y)[0][1]

# plot the data
plt.scatter(x, x+d, color = 'red', alpha = 0.3)
plt.title(f"Correlation: {corr:.2f}")
plt.xlabel("X")
plt.ylabel("Y")


nbins = 20
halpha = 0.40

# Create histograms
plt.figure()
plt.hist(x, range = (xymin, xymax), bins=nbins, 
         edgecolor='black', color = 'blue', alpha = halpha)
plt.xlabel('values')
plt.ylabel('Events')
#plt.title(f'Histogram of Data, mean {xmean:1.2f} stdd: {xstd:1.2f}')


# Create histograms
#plt.figure()
plt.hist(y, range = (xymin, xymax), bins=nbins,
         edgecolor='black', color = 'darkgreen', alpha = halpha)
plt.xlabel('values')
plt.ylabel('Events')
#plt.title(f'Histogram of Data, mean {ymean:1.2f} stdd: {ystd:1.2f}')
plt.title(f'meanX {xmean:1.2f} stdX: {xstd:1.2f} meanY {ymean:1.2f} stdY: {ystd:1.2f} ')


# show all plots:
plt.show()




# OTHER:
#https://stackoverflow.com/questions/33328774/box-plot-with-min-max-average-and-standard-deviation

