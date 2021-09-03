#!/usr/bin/python

import numpy as np
import matplotlib.pyplot as plot
from scipy.fftpack import fft, ifft

# number of sample points:
n=0
# sample spacing:
T = 1.


fname= 'pi_10k.txt'
#fname = 'pi_100k.txt'
ptimespect = []
tfile = open(fname, 'r')
tag = fname
tag= tag.replace('.txt', '').replace('pi_', '')
for line in tfile.readlines():
    for char in line[:-1]:
        if char == '' or char == ' ':
            continue
        #print '"%s"' % (char,)
        val = int(char)
        #print '%s == %i' % (char,val,)
        ptimespect.append(1.*val)
        n = n+1

#print ptimespect 
# x axis of the time domain:
xtime = np.linspace(0.0, n*T, n)
timespect = np.array(ptimespect)
freqspect = fft(ptimespect)

print timespect
print freqspect

# x axis of the frequency domain:
xf = np.linspace(0.0, 1.0/(2.0*T), n//2)

plot.subplot(2, 1, 1)
plot.plot(xtime, timespect)
plot.ylim([0, 11])
plot.grid()

plot.subplot(2, 1, 2)
plot.plot(xf, 2.0/n * np.abs(freqspect[0:n//2]))
plot.ylim([0, 0.2])
plot.grid()

plot.show()

