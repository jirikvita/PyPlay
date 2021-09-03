#!/usr/bin/python

from ROOT import *

Funs = []
Pars = [200, 100, 50, 25, 10]

opt=''
for par in Pars:
    fun = TF1('delta%i' % (int(par),), 'sin([0]*x)/x', -1/2., 1/2.)
    fun.SetParameter(0, 1.*par)
    fun.SetNpx(2000)
    fun.SetLineColor(kBlue+len(Funs))
    fun.Draw(opt)
    Funs.append(fun)
    opt='same'
gPad.RedrawAxis()
gPad.Print('Deltas.png')
gPad.Print('Deltas.pdf')

gApplication.Run()
