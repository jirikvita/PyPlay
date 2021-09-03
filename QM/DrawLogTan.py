#!/usr/bin/python

from ROOT import *
from math import *

Funs = []
Pars = [1, ]

opt=''
for par in Pars:
    fun = TF1('logtan%i' % (int(par),), 'log(tan(x/2))', 0, pi)
    fun.SetParameter(0, 1.*par)
    fun.SetNpx(2000)
    fun.SetLineColor(kBlue+len(Funs))
    fun.Draw(opt)
    Funs.append(fun)
    opt='same'
for par in Pars:
    fun = TF1('logtan%i' % (int(par),), '[0]*sin(x)*(log(tan(x/2)))^2', 0, pi)
    fun.SetParameter(0, 1.*par)
    fun.SetNpx(2000)
    fun.SetLineColor(kBlue+len(Funs))
    fun.Draw(opt)
    Funs.append(fun)
    opt='same'

gPad.RedrawAxis()
gPad.Print('LogTan.png')
gPad.Print('LogTan.eps')

gApplication.Run()
