#!/usr/bin/python

import os, sys

import ROOT
from ROOT import gPad, gApplication, TF1, TH1D, TH2D, TCanvas, TLine
from ROOT import kRed, kBlue, kGreen, kBlack

from math import sqrt, pow, pi, exp, log
import random

def GetEqualPoints(f1, f2):
    x1 = f1.GetXaxis().GetXmin()
    x2 = f1.GetXaxis().GetXmax()
    step = 1e-3
    signe = 0
    oldsigne = 0
    zns = []
    for i in range(1, int((x2 - x1)/step) ):
        x = x1 + i*step
        #print(f1.Eval(x),f2.Eval(x))
        if f1.Eval(x) < 0 or f2.Eval(x) < 0:
            oldsigne = 0
            continue
        df = f1.Eval(x) - f2.Eval(x)
        if abs(df) > 0:
            signe = df/abs(df)
        else:
            signe = 0
        if abs(oldsigne) < 1e-4:
            oldsigne = 1.* signe
            continue
        if signe*oldsigne < 0:
            zns.append(1.*x)
            oldsigne = 0.
        oldsigne = 1.* signe
            
    return zns
                   
    
Funs = []

stuff = []

pngdir = 'png/'
pdfdir = 'pdf/'
os.system(f'mkdir {pngdir}')
os.system(f'mkdir {pdfdir}')

hc=197 # MeV fm
# alpha particle:
a=1 # fm
m = 3700 # MeV
V0 = 500 # MeV

# electron
#a=1.e6 # fm
#m = 0.511 # MeV
#V0 = 1e-4 # MeV

print('---------------------------------------------------')
print('Solutions for the finite square well:')
print(f'm  = {m} MeV')
print(f'V0 = {V0} MeV')
print(f'a  = {a} fm')

z0 = sqrt(2*m*V0)/(hc)*a
print(f'z0 = {z0:1.3f}')

zero=0

# pars to define tan and -cotan ;-)
Pars = [ [1, 1, z0], [-1, -1, z0] ]
fun1expr = '[1]*tan(x)^([0])'
# the sqrt function
fun2expr = 'sqrt(([0]/x)^2-1)'

ymax = 20.
nx = 100
ny = 1000
h2 = TH2D('Finite square well energy solutions', 'Finite square well energy solutions;z;', nx, zero, z0, ny, 0, ymax)
#h2.SetOptTitle(0)
h2.SetStats(0)

canE = ROOT.TCanvas('FiniteWellEnergySolutions', '', 0, 0, 1200, 800)
h2.Draw()

pilines = []
col = [kBlue, kGreen+3]

opt='same'
j=-1
for pars in Pars:
    j=j+1
    fun1 = TF1('well_1_%i' % (j,), fun1expr, zero, z0)
    fun1.SetParameter(0, 1.*pars[0])
    fun1.SetParameter(1, 1.*pars[1])
    fun1.SetNpx(5000)
    fun1.SetLineColor(col[j])
    fun1.Draw(opt)
    Funs.append(fun1)
    
    
fun2 = TF1('well_2_%i' % (j,), fun2expr, zero, z0)
i=0
#for par in pars[2:]:
fun2.SetParameter(0, pars[2])
i=i+1

fun2.SetNpx(5000)
fun2.SetLineColor(kRed)
fun2.Draw(opt)
Funs.append(fun2)

for i in range(0,1+2*int(z0/pi)):
    line = TLine(i*pi/2, 0, i*pi/2, ymax)
    line.SetLineStyle(2)
    line.SetLineColor(kBlack)
    line.Draw()
    pilines.append(line)

gPad.RedrawAxis()
ROOT.gPad.SetGridx(1)
ROOT.gPad.SetGridy(1)
ROOT.gPad.Update()

tag='_%i_%i_%i' % (int(a),int(1.e3*m),int(1e6*V0))
#gPad.Print('png/Well%s.png' % (tag,))
#gPad.Print('png/Well%s.pdf' %(tag,))
stuff.append([h2, Funs, canE])


zns_even = GetEqualPoints(fun2, Funs[0])
print(f'OK, found {len(zns_even)} even solutions')
zns_odd = GetEqualPoints(fun2, Funs[1])
print(f'OK, found {len(zns_odd)} odd solutions')
Zns = { 1: zns_even, -1: zns_odd}

Es = []
# a triplet of functions left, in and right of the finite well
Funs = []
FunsSq = []

sf = 1.75
x1 = -sf*a
x2 = -1.*x1

for parity in Zns:
    zns = Zns[parity]
    for iz, zn in enumerate(zns):
        E = pow(zn*hc, 2) / (2*m*a*a) - V0
        print(f'zn={zn:1.3f} E={E}')
        kappa = sqrt(-2*m*E) / hc
        k = sqrt(2*m*(V0 + E)) / hc
        Es.append(E)

        
        # amplitude inside:
        D = 1.
        fform = '[0]*cos([1]*x)'
        if parity < 0:
            fform = '[0]*sin([1]*x)'
            
        funIn = TF1(f'fun_in_{iz}', fform, -a, a)
        funIn.SetParameters(D, k)#, a)

        # amplitude outside:
        F = D*funIn.Eval(a) * exp(kappa*a)
        funLeft = TF1(f'fun_left_{iz}', '[0]*exp([1]*x)', x1, -a)
        funLeft.SetParameters(parity*F, kappa)
        funRight = TF1(f'fun_right_{iz}', '[0]*exp(-[1]*x)', a, x2)
        funRight.SetParameters(F, kappa)
        Funs.append([funLeft, funIn, funRight])

        # probability densities: (squared functions)
        funInSq = TF1(f'funsq_in_{iz}', '(' + fform + ')^2', -a, a)
        funInSq.SetParameters(D, k)#, a)
        funLeftSq = TF1(f'funsq_left_{iz}', '([0]*exp([1]*x))^2', x1, -a)
        funLeftSq.SetParameters(parity*F, kappa)
        funRightSq = TF1(f'funsq_right_{iz}', '([0]*exp(-[1]*x))^2', a, x2)
        funRightSq.SetParameters(F, kappa)
        FunsSq.append([funLeftSq, funInSq, funRightSq])

################################################
canEs = ROOT.TCanvas('FiniteWellEnergies', '', 0, 0, 1200, 800)
canEs.cd()
potential = ROOT.TF1('fpot', ' 0. - (x>-[0])*(x<[0])*[1]', x1, x2)
potential.SetLineColor(ROOT.kBlue)
potential.SetParameters(a, V0)
potential.SetNpx(5000)
potential.SetLineWidth(3)
hpot = ROOT.TH2D('hpot', ';x [fm];V(x) [MeV];', 100, x1, x2, 100, -1.2*V0, 0.2*V0)
hpot.SetStats(0)
hpot.Draw()
potential.Draw('same')
elines = []
for E in Es:
    line = ROOT.TLine(-a, E, a, E)
    line.SetLineWidth(2)
    line.SetLineColor(ROOT.kRed)
    line.SetLineStyle(1)
    line.Draw()
    elines.append(line)
stuff.append([elines, hpot, potential])
ROOT.gPad.SetGridx(1)
ROOT.gPad.SetGridy(1)
ROOT.gPad.Update()



################################################
canf = ROOT.TCanvas('FiniteWellFunctions', '', 0, 0, 1600, 800)
canf.cd()
y1, y2 = -2, 2
h2 = ROOT.TH2D('tmp', ';x [fm];#psi(x);', 1000, x1, x2, 1000, y1, y2)
h2.SetStats(0)
h2.Draw()
leg = ROOT.TLegend(0.7, 0.7, 0.88, 0.88)
cols = [ROOT.kRed, ROOT.kBlue, ROOT.kGreen+2, ROOT.kCyan,
        ROOT.kMagenta, ROOT.kTeal+10, ROOT.kOrange-3,
        ROOT.kViolet, ROOT.kOrange, ROOT.kPink+10]
alpha = 0.15
for i,funs in enumerate(Funs):
    #col = max(1, int(10*random.random()) )
    col = -1
    if i < len(cols):
        col = cols[i]
    else:
        col = max(1, int(10*random.random()) )
    lsty = max(1, int(10*random.random()) )
    for fun in funs:
        fun.SetNpx(5000)
        #fun.SetLineColorAlpha(col, alpha)
        fun.SetFillColorAlpha(col, alpha)
        fun.SetFillStyle(1111)
        fun.SetLineColor(col)
        #fun.SetLineStyle(lsty)
        fun.Draw('same')
    leg.AddEntry(funs[1], funs[1].GetName(), 'PL')
#leg.Draw()
lines = [ ROOT.TLine(-a, y1, -a, y2), ROOT.TLine(a, y1, a, y2)]
for line in lines:
    line.SetLineStyle(2)
    line.SetLineColor(ROOT.kBlack)
    line.Draw()
ROOT.gPad.SetGridx(1)
ROOT.gPad.SetGridy(1)
ROOT.gPad.Update()

################################################
canSq = ROOT.TCanvas('FiniteWellDensities', '', 0, 0, 1600, 800)
canSq.cd()
y1, y2 = -0.2, 1.2
h2Sq = ROOT.TH2D('tmpSq', ';x [fm];|#psi(x)|^{2};', 1000, x1, x2, 1000, y1, y2)
h2Sq.SetStats(0)
h2Sq.Draw()
legSq = ROOT.TLegend(0.7, 0.7, 0.88, 0.88)
for i,funs in enumerate(FunsSq):
    for fun in funs:
        fun.SetNpx(5000)
        col = Funs[i][0].GetLineColor()
        #fun.SetLineColorAlpha(col, alpha)
        fun.SetLineColor(col)
        fun.SetFillColorAlpha(col, alpha)
        fun.SetFillStyle(1111)
        fun.Draw('same')
    legSq.AddEntry(funs[1], funs[1].GetName(), 'PL')
#legSq.Draw()
linesSq = [ ROOT.TLine(-a, y1, -a, y2), ROOT.TLine(a, y1, a, y2)]
for line in linesSq:
    line.SetLineStyle(2)
    line.SetLineColor(ROOT.kBlack)
    line.Draw()
ROOT.gPad.SetGridx(1)
ROOT.gPad.SetGridy(1)
ROOT.gPad.Update()   


stuff.append([h2, h2Sq])
cans = [canE, canEs, canf, canSq]
NEs = len(Es)
for can in cans:
    can.Print(pngdir + can.GetName() + f'_V0_{V0}MeV_{NEs}_solutions.png')
    can.Print(pdfdir + can.GetName() + f'_V0_{V0}MeV_{NEs}_solutions.pdf')

print('DONE!')
gApplication.Run()
