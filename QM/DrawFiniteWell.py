#!/usr/bin/python

from ROOT import *
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
#V0 = 1e-4 # MeV

z0 = sqrt(2*m*V0)/(hc)*a
print z0

zero=0

Pars = [ [1, 1, z0], [-1, -1, z0] ]
fun1expr = '[1]*tan(x)^([0])'
fun2expr = 'sqrt(([0]/x)^2-1)'

ymax = 20.
nx=100
ny=1000
h2=TH2D('Finite square well energy solutions', 'Finite square well energy solutions', nx, zero, z0, ny, 0, ymax)
#h2.SetOptTitle(0)
h2.SetStats(0)
h2.Draw()

lines = []
col = [kBlue, kGreen+3]

opt='same'
j=-1
for pars in Pars:
    j=j+1
    fun1 = TF1('well_1_%i' % (j,), fun1expr, zero, z0)
    fun1.SetParameter(0, 1.*pars[0])
    fun1.SetParameter(1, 1.*pars[1])
    

    fun1.SetNpx(2000)
    fun1.SetLineColor(col[j])
    fun1.Draw(opt)
    Funs.append(fun1)
    
    
fun2 = TF1('well_2_%i' % (j,), fun2expr, zero, z0)
i=0
#for par in pars[2:]:
fun2.SetParameter(0, pars[2])
i=i+1

fun2.SetNpx(2000)
fun2.SetLineColor(kRed)
fun2.Draw(opt)
Funs.append(fun2)

for i in range(0,1+2*int(z0/pi)):
    line = TLine(i*pi/2, 0, i*pi/2, ymax)
    line.SetLineStyle(2)
    line.SetLineColor(kBlack)
    line.Draw()
    lines.append(line)

gPad.RedrawAxis()
tag='_%i_%i_%i' % (int(a),int(1.e3*m),int(1e6*V0))
gPad.Print('Well%s.png' % (tag,))
gPad.Print('Well%s.pdf' %(tag,))

gApplication.Run()
