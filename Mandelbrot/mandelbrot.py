#!/usr/bin/python
# jk 16.5.2023

# https://en.wikipedia.org/wiki/Mandelbrot_set
# https://mathworld.wolfram.com/MandelbrotSet.html

from math import pow, sqrt
import ROOT

kMin = 1.e-3

stuff = []

# https://www.programiz.com/python-programming/operator-overloading

##################################################
##################################################
##################################################

class MyComplex:
    def __init__(self, re, im):
        self.re = re
        self.im = im
    def print(self):
        print('re={:1.3f} im={:1.3f} mag={:1.3f}'.format(self.re, self.im, self.mag()))
    def mag(self):
        mag2 = pow(self.re,2) + pow(self.im,2)
        if mag2 > 0:
            return sqrt(mag2)
        else:
            return 0.
    def __add__(self,other):
        result = MyComplex(self.re + other.re, self.im + other.im)
        return result
    def __mul__(self,other):
        result = MyComplex(self.re*other.re - self.im*other.im, self.re*other.im + self.im*other.re)
        return result
    #def __mul__(self,real):
    #    result = MyComplex(self.re*real, self.im*real)
    #    return result

##################################################
##################################################
##################################################
    
def getNext(z, c):
    znew = z*z + c
    #znew.print()
    return znew

##################################################

def iterate(c, Nmax = 200, bound = 100.):
    n = 0
    #z = c*1.
    #z = c
    c1 = MyComplex(1.,0.)
    z = c*c1
    bounded = True
    while n < Nmax:
        znew = getNext(z, c)
        if znew.mag() > bound:
            bounded = False
            break
        n = n + 1
        z = znew*c1
    if bounded:
        n = kMin
    return z,bounded, n

##################################################

def Plot(nbx, x1, x2, nby, y1, y2, results):
    name = 'Mandelbrot'
    title = name
    h2 = ROOT.TH2D(name, title, nbx, x1, x2, nby, y1, y2)
    bwx = (x2 - x1) / nbx
    bwy = (y2 - y1) / nby
    for i in range(0, len(results)):
        for j in range(0, len(results[i])):
            h2.SetBinContent(i+1, j+1, results[i][j])
    h2.Scale(1.)
    canname = name
    can = ROOT.TCanvas(canname, canname)
    h2.SetStats(0)
    ROOT.gStyle.SetPalette(ROOT.kAvocado)
    ROOT.gStyle.SetOptTitle(0)
    h2.Draw('col')
    can.SetLogz(1)
    can.Update()
    return can,h2

##################################################
##################################################
##################################################

x1, x2 = -1.45, 0.55
y1, y2 = -1.1,1.1
nbx = 2000
nby = 2000
bwx = (x2 - x1) / nbx
bwy = (y2 - y1) / nby


results = []

verb = 100
verbose = False

# bin centers bcx, bcy
for i in range(0, nbx):
    if i % verb == 0:
        print(f' xprocess {i}/{nbx}')
    results.append([])
    bcx = x1 + bwx* (i + 1/2.)
    for j in range(0, nby):
        #if j % verb == 0:
        #    print(f'   yprocess {j}/{nby}')

        bcy = y1 + bwy* (j + 1/2.)
        c = MyComplex(bcx, bcy)
        if verbose:
            print('Iterating...')
        zn,bounded,n = iterate(c)
        if bounded:
            results[-1].append(0.)
        else:
            results[-1].append(n)
        if verbose:
            print('  ...result: mag={:1.3f} n={}'.format(zn.mag(), n))

#print(results)
can, h2 = Plot(nbx, x1, x2, nby, y1, y2, results)
stuff.append([can,h2])

ROOT.gApplication.Run()

