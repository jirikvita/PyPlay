#!/usr/bin/python

from ROOT import *
from math import *

Funs = []
Pars = [200, 100, 50, 25, 10]

canname = 'HatFunction'
can = TCanvas(canname, canname, 0, 0, 1000, 800)
can.cd()

opt=''
fun = TF1('hat', 'exp(-1/(1-x^2))', -1., 1.)
fun.SetNpx(1000)
fun.Draw()
gPad.RedrawAxis()


gPad.Print(canname + '.pdf')

gApplication.Run()

