#!/usr/bin/python

import ROOT
from ROOT import gPad, gApplication, TF1, TH1D, TH2D, TCanvas, TLine
from ROOT import kRed, kBlue, kGreen, kBlack

from math import *

Funs = []

hc=197 # MeV fm
# alfa castice:
a=1 # fm
m = 3700 # MeV
V0 = 1000 # MeV

# elektron
#a=1.e6 # fm
#m = 0.511 # MeV
#V0 = 1e-4

z0 = sqrt(2*m*V0)/(hc)*a
print(z0)

zero=0

Pars = [ [1,1, z0], [-1,1, z0], [1,-1, z0], [-1,-1, z0] ]
fun1expr = 'tan(x)^[0]'
fun2expr = '[0]*sqrt(([1]/x)^2-1)'

opt='same'
ymax = 20.
nx=100
ny=1000
h2=TH2D('Infinite squere well energy solutions', 'Infinite squere well energy solutions', nx, zero, z0, ny, -ymax, ymax)
#h2.SetOptTitle(0)
h2.SetStats(0)
h2.Draw()

j=-1
for pars in Pars:
    j=j+1
    fun1 = TF1('infwell_1_%i' % (j,), fun1expr, zero, z0)
    fun1.SetParameter(0, 1.*pars[0])

    fun2 = TF1('infwell_2_%i' % (j,), fun2expr, zero, z0)
    i=0
    for par in pars[1:]:
        fun2.SetParameter(i, 1.*par)
        i=i+1

    fun1.SetNpx(2000)
    fun1.SetLineColor(kBlue+j)
    fun1.Draw(opt)
    Funs.append(fun1)
    
    fun2.SetNpx(2000)
    fun2.SetLineColor(kRed)
    fun2.Draw(opt)
    Funs.append(fun2)



gPad.RedrawAxis()
tag='_%i_%i_%i' % (int(a),int(1.e3*m),int(1e6*V0))
gPad.Print('InfWell%s.png' % (tag,))
gPad.Print('InfWell%s.pdf' %(tag,))

gApplication.Run()
