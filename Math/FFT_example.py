#!/usr/bin/python

import numpy as np
import matplotlib.pyplot as plot
from scipy.fftpack import fft, ifft

# number of sample points:
n=264
# sample spacing:
T = 1.0 / 800.0

#https://docs.scipy.org/doc/scipy/reference/tutorial/fftpack.html
# https://docs.scipy.org/doc/scipy/reference/tutorial/fftpack-1.py
# https://docs.scipy.org/doc/numpy/reference/routines.fft.html
# A[1:n/2] contains the positive-frequency terms, and A[n/2+1:] contains the negative-frequency terms
#spect = fft(a[, n, axis, norm])

# x axis of the time domain:
xtime = np.linspace(0.0, n*T, n)
timespect = 2*np.sin(20.0 * 2.0*np.pi*xtime) + 0.5*np.sin(50.0 * 2.0*np.pi*xtime) + 1.5*np.sin(80.0 * 2.0*np.pi*xtime)

freqspect = fft(np.array(timespect))

print timespect
print freqspect

# x axis of the frequency domain:
xf = np.linspace(0.0, 1.0/(2.0*T), n//2)

plot.subplot(2, 1, 1)
plot.plot(xtime, 2.0/n * np.abs(timespect))
plot.grid()

plot.subplot(2, 1, 2)
plot.plot(xf, 2.0/n * np.abs(freqspect[0:n//2]))
plot.grid()

plot.show()
