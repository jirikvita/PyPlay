#!/usr/bin/python
from math import pi
# jk 26.2.2021

import ROOT

stuff = []

forms = ['sin(x^2+y^2)/cosh(x*y)',
         'exp(-abs(x+y))*cos(x*y)',
         '-abs(x) + y^2',
         'exp(-sqrt(x^2+y^2))*cos(x*y)',
]

canname = 'FunFunctions2D'
can = ROOT.TCanvas(canname, canname, 0, 0, 1200,900)
can.Divide(2,2)
funs = []

x1 = -5
x2 = 5
y1 = x1
y2 = x2

ROOT.gStyle.SetPalette(1)

opt = 'surf'
#opt = 'surf3'

i = -1
cols = [ROOT.kBlue, ROOT.kMagenta, ROOT.kBlack, ROOT.kRed]
for form in forms:
    i = i+1
    name = 'fun{}'.format(i)
    fun = ROOT.TF2(name, form, x1, x2, y1, y2)
    can.cd(i+1)
    fun.SetNpx(100)
    fun.SetNpy(100)
    fun.SetLineWidth(1)
    fun.SetLineColor(cols[i])
    fun.Draw(opt) 
    funs.append(fun)


can.Print(can.GetName() + '.pdf')
can.Print(can.GetName() + '.png')

stuff.append([can, funs, forms])

ROOT.gApplication.Run()
