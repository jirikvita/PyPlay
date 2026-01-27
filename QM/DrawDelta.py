#!/usr/bin/python

import ROOT

Funs = []
Pars = [200, 100, 50, 25, 10]

opt=''
for par in Pars:
    fun = ROOT.TF1('delta%i' % (int(par),), 'sin([0]*x)/x', -1/2., 1/2.)
    fun.SetParameter(0, 1.*par)
    fun.SetNpx(2000)
    fun.SetLineColor(ROOT.kBlue+len(Funs))
    fun.Draw(opt)
    Funs.append(fun)
    opt='same'
ROOT.gPad.RedrawAxis()
ROOT.gPad.Print('Deltas.png')
ROOT.gPad.Print('Deltas.pdf')

ROOT.gApplication.Run()
