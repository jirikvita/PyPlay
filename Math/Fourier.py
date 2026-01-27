#!/usr/bin/python
# jk 11.2.2017

from math import *
from ROOT import *

#############################################

class FitForm:
    def __init__(self, term, x1, x2, nKs, s1, s2, name):
        self._term = term
        self._x1 = x1
        self._x2 = x2
        self._nKs = nKs
        self._s1 = s1
        self._s2 = s2
        self._name = name
    def GetTerm(self):
        return self._term
    def GetnKs(self):
        return self._nKs
    def GetS1(self):
        return self._s1
    def GetS2(self):
        return self._s2
    def GetX1(self):
        return self._x1
    def GetX2(self):
        return self._x2
    def GetName(self):
        return self._name

    def  GetFormula(self, n1, N):
        formula = ''	
        sign = self._s1
        nextsign = self._s2
        for i in range(n1,N+1):
            Sign = sign
            #if i == n1: Sign = ''
            veci = tuple( [i*n/n for n in range(1,self._nKs+1)] ) # makes a tuple (i,i,i,i,i...)
            formula = formula + Sign + (self._term % (veci))
            sign,nextsign = nextsign,sign
        return formula
    

#############################################


#############################################
#############################################
#############################################

gStyle.SetOptTitle(0)



Forms = []
Forms.append( FitForm(' 4/TMath::Pi()*1/(2*%i-1)*sin((4*%i-2)*x) ', -pi/2, pi/2, 2, '+', '+', 'Const') )
Forms.append( FitForm(' 2*sin(%i*x)/%i', -2*pi, 2*pi, 2, '+', '-', 'Saw') )
Forms.append( FitForm( '  4/TMath::Pi()*cos((2*%i-1)*x)/(2*%i-1)^2 + (%i == 1)*TMath::Pi()/2', -2*pi, 2*pi, 3, '-', '-', 'Abs') )
Forms.append( FitForm(' sin((2*%i-1)*x)*4./(TMath::Pi()*(2*%i-1)^2)', -2*pi, 2*pi, 2, '+', '-', 'Pyramides') )

N = [25, 1, 2, 4, 12, ]
col = [kRed, kBlue, kGreen+3, kMagenta, kYellow+3, kOrange, kPink]
lstyle = [1, 5, 4, 3, 2, 1, 1, 1, 1, 1, 1, 1]
#x1=0
#x2=pi/2.

canname = 'Fourier'
can = TCanvas(canname, canname, 0, 0, 1000, 1000)
can.Divide(2,2)
funs = []

for form in Forms:
    print( '--- Processing ' )
    print( form )
    x1=form.GetX1()
    x2=form.GetX2()
    j = Forms.index(form)
    can.cd(j+1)
    opt=''
    tag=form.GetName()    
    for n in N:
        formula = form.GetFormula(1,n)
        print( formula )
        name='Fourier_%s_%i' % (tag,n,)
        fun = TF1(name, formula, x1, x2)
        fun.SetNpx(2000)
        iterm = N.index(n)
        fun.SetLineColor(col[iterm])
        fun.SetLineStyle(lstyle[iterm])
        fun.Draw(opt)
        opt='same'
        funs.append(fun)

    can.cd(j+1)
    gPad.Print('Fourier_%s.png' % (tag,))
    gPad.Print('Fourier_%s.pdf' % (tag,))


gApplication.Run()
