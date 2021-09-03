#!/usr/bin/python

from ROOT import *
from math import *

Funs = []
Pars = [200, 100, 50, 25, 10]

can = TCanvas("Deltas", "Deltas", 0, 0, 1000, 800)
can.cd()

opt=''
for par in Pars:
    fun = TF1('delta%i' % (int(par),), 'sin([0]*x)/x', -1/2., 1/2.)
    fun.SetParameter(0, 1.*par)
    fun.SetNpx(2000)
    fun.SetLineColor(kBlue+len(Funs))
    fun.Draw(opt)
    Funs.append(fun)
    opt='same'
    print 'Integral under central peak: I = %f' % (fun.Integral(-pi/(1.*par),pi/(1.*par)),)
gPad.RedrawAxis()
gPad.Print('Deltas.png')
gPad.Print('Deltas.eps')
gPad.Print('Deltas.pdf')

gApplication.Run()
