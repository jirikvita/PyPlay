#!/usr/bin/python


from math import *
from ROOT import *


formula = ''
N=50
sign = '+'
nextsign='-'
for i in range(1,N):
    if i % 2 == 0:
        continue
    formula = formula + sign + ' 1/sqrt([0])*1/TMath::Pi()/(1-%i*%i/4.)*sin(%i*TMath::Pi()/(2*[0])*x)' % (i,i,i)
    sign,nextsign = nextsign,sign
    
    
x2=1.
print formula
name='Fourier'
fun = TF1(name, formula, 0, 2*x2)
fun.SetParameter(0, x2)
fun.SetNpx(10000)
fun.Draw()
gPad.Print('Fourier.png')
gPad.Print('Fourier.eps')


gApplication.Run()
