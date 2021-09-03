#!/usr/bin/python

from ROOT import *

col = [kRed, kBlue]

Funs = []
V0 = 5e-6 # in MeV, 5 eV
mc2 = 0.511e6 # electron
a = 1.e3 # in fm, sould be 1pm
hc = 197 # MeV fm

Pars = [ V0, mc2, a, hc ]

Forms = [ '1/( 1. + [0]^2 / (4*x*(x+[0])) * (sin( 2*[2]/[3]*sqrt( 2*[1]*(x+[0])  )  ))^2  )',
          '1/( 1. + [0]^2 / (4*x*([0]-x)) * (sinh( 2*[2]/[3]*sqrt( 2*[1]*([0]-x)  )  ))^2  )'
         ]
X1 = [0., 0.]
X2 = [5*V0, V0]

opt=''
Cans = []

tag = ['FiniteWell', 'FiniteStep']

i = -1
for x1,x2,form in zip(X1,X2,Forms):
    i = i+1
    can = TCanvas('Transmissions_%s' % (tag[i] ))
    Cans.append(can)
    can.cd()
    fun = TF1('Trans_%s' % (tag[i],), form, x1, x2)
    fun.SetNpx(20000)
    ipar = -1
    for par in Pars:
        ipar = ipar+1
        fun.SetParameter(ipar, 1.*par)
    fun.SetLineColor(col[i])
    fun.Draw(opt)
    #opt='same'
    Funs.append(fun)
    can.Print(can.GetName() + '.png')
    can.Print(can.GetName() + '.pdf')
  
    


gApplication.Run()
