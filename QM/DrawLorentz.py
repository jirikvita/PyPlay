#!/usr/bin/python

from ROOT import *

Funs = []
Pars = [
    1e-1,
    2e-1,
    #1e-2,
    #9e-1,
    #8e-1,
    #4e-1,
    #5e-2,

]

form = ["1/(x^2+[0]^2)^(3/2)",
        "x^2/(x^2+[0]^2)^(5/2)",
        "(-2*x^2+[0]^2)/(x^2+[0]^2)^(5/2)"
         ]
nn = len(form)
x1 = -1
x2 = 1

opt=''
for par in Pars:

    print len(Funs)/nn
    fun = TF1('delta1%i' % (int(par),), form[0], x1, x2)
    fun.SetParameter(0, 1.*par)
    fun.SetNpx(2000)
    #fun.SetLineColor(kBlue)
    fun.SetLineColor(kBlue+len(Funs)/nn)
    #fun.Draw(opt)
    #opt='same'
    Funs.append(fun)

    print len(Funs)/nn
    fun = TF1('delta2%i' % (int(par),), form[1], x1, x2)
    fun.SetParameter(0, 1.*par)
    fun.SetNpx(2000)
    #fun.SetLineColor(kGreen)
    fun.SetLineColor(kGreen+len(Funs)/nn)
    #fun.Draw(opt)
    Funs.append(fun)
    #opt='same'
    
    print len(Funs)/nn
    fun = TF1('delta2%i' % (int(par),), form[2], x1, x2)
    fun.SetParameter(0, 1.*par)
    fun.SetNpx(10000)
    #fun.SetLineColor(kRed)
    fun.SetLineColor(kRed+len(Funs)/nn)
    fun.Draw(opt)
    Funs.append(fun)
    opt='same'
    
#gPad.SetLogy()
gPad.RedrawAxis()
gPad.Print('Lorentz.png')
gPad.Print('Lorentz.pdf')

gApplication.Run()
