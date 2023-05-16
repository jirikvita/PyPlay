#!/usr/bin/python
# jk 16.5.2023

# https://en.wikipedia.org/wiki/Mandelbrot_set
# https://mathworld.wolfram.com/MandelbrotSet.html
# https://en.wikipedia.org/wiki/Julia_set

from math import pow, sqrt, pi, sin, cos
import ROOT

kMin = 1.e-3
kMandel = 'Mandel'
kJulia = 'Julia'

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
    def __truediv__(self,other):
        result = MyComplex( (self.re*other.re +  self.im*other.im)/ other.mag(),  (self.im*other.re + self.re*other.im) / other.mag())
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
    
def getNext(z, c, maintag):
    # Mandelbrot:
    znew = c
    if maintag == kMandel:
        znew = z*z + c
    elif maintag == kJulia:
        # some Julia:
        alpha = pi*2./4.
        xi = 0.7885
        znew = z*z + MyComplex(xi*cos(alpha), xi*sin(alpha))
        
        #two = MyComplex(2.,0.)
        #three = MyComplex(3.,0.)
        #znew = (z*z + MyComplex(cos(alpha), sin(alpha))) / (two*z)
        #znew = (z*z*z + MyComplex(cos(alpha), sin(alpha))) / (three*z*z)
        
    #znew.print()
    return znew

##################################################

def iterate(c, maintag, Nmax = 200, bound = 100.):
    n = 0
    c1 = MyComplex(1.,0.)
    z = c*c1
    bounded = True
    while n < Nmax:
        znew = getNext(z, c, maintag)
        if znew.mag() > bound:
            bounded = False
            break
        n = n + 1
        z = znew*c1
    return z,bounded, n

##################################################

def Plot(nbx, x1, x2, nby, y1, y2, results, maintag, addtag):
    ROOT.gStyle.SetPadTopMargin(0.)
    ROOT.gStyle.SetPadBottomMargin(0.)
    ROOT.gStyle.SetPadRightMargin(0.)
    ROOT.gStyle.SetPadLeftMargin(0.)

    name = maintag
    title = name
    h2 = ROOT.TH2D(name, title, nbx, x1, x2, nby, y1, y2)
    bwx = (x2 - x1) / nbx
    bwy = (y2 - y1) / nby
    for i in range(0, len(results)):
        for j in range(0, len(results[i])):
            h2.SetBinContent(i+1, j+1, results[i][j])
    h2.Scale(1.)
    h2.GetXaxis().SetTickSize(0.)
    h2.GetYaxis().SetTickSize(0.)
    canname = name
    can = ROOT.TCanvas(canname, canname, 0, 0, 1200,1200)
    h2.SetStats(0)
    ROOT.gStyle.SetOptTitle(0)
    h2.Draw('col')
    can.SetLogz(1)
    can.Update()

    palettes = {
        'Standard' : 1,
        'Avocado'  : ROOT.kAvocado,
        'Rust'     : ROOT.kRust,
        'Viridis'  : ROOT.kViridis,
        'Cherry'   : ROOT.kCherry,
        'DeepSea'  : ROOT.kDeepSea,
    }
    for key,palette in palettes.items():
        ROOT.gStyle.SetPalette(palette)
        ROOT.gPad.SetLogz(0)
        can.Print(can.GetName() + f'_{key}{addtag}_liny.png')
        ROOT.gPad.SetLogz(1)
        can.Print(can.GetName() + f'_{key}{addtag}_logy.png')

    
    return can,h2

##################################################
##################################################
##################################################


# DEFAULT:
ym = 1.1
x1, x2 = -1.55, 0.55
y1, y2 = -ym,ym
maintag = kMandel
addtag = ''

# ZOOM:
#ym = 1.1 / 3.
#x1, x2 = -1.45, -0.65
#y1, y2 = -ym,ym
#addtag = '_zoom1'

# Julia
ym = 1.5
x1, x2 = -ym,ym
y1, y2 = -ym,ym
maintag = kJulia
addtag = ''


nn = 2000
nbx = nn
nby = nn
bwx = (x2 - x1) / nbx
bwy = (y2 - y1) / nby

results = []

verb = 2000
verbose = False

# bin centers bcx, bcy
for i in range(0, nbx):
    if i % verb == 0:
        print(f' x loop progress {i}/{nbx}')
    results.append([])
    bcx = x1 + bwx* (i + 1/2.)
    for j in range(0, nby):
        #if j % verb == 0:
        #    print(f'   y loop progress {j}/{nby}')

        bcy = y1 + bwy* (j + 1/2.)
        c = MyComplex(bcx, bcy)
        if verbose:
            print('Iterating...')
        zn,bounded,n = iterate(c, maintag)
        if bounded:
            results[-1].append(kMin)
        else:
            results[-1].append(n)
        if verbose:
            print('  ...result: mag={:1.3f} n={}'.format(zn.mag(), n))

#print(results)
can, h2 = Plot(nbx, x1, x2, nby, y1, y2, results, maintag, addtag)
stuff.append([can,h2])


ROOT.gApplication.Run()

