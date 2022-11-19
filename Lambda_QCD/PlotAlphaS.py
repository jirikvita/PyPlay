#!/usr/bin/python

# jk 18.11.2022

from math import log10, log, pow, sqrt, exp, pi

import ROOT

# running coupling of QCD:

TR = 1./2.
CA = 3.
CF = 4./3.

nf = 3

# [1] https://arxiv.org/abs/1207.2389
b0 = (11*CA - 4*TR*nf) / (12*pi)
#b1 = (17*CA*CA - 10*TR*CA*nf - 6*TR*CF*nf) / (24*pi*pi)

# [2] https://arxiv.org/pdf/1604.08082.pdf
#b0 = 1./(4*pi)*(11. - 2./3.*nf)
b1 = 1./pow(4*pi,2)*(102. - 38./3.*nf)
b2 = 1./pow(4*pi,3)*( 2857./2. - 5033/18.*nf + 325./54.*nf*nf)

print(b0, b1, b2)

# in GeV
MZ = 92.3
logq2a = 0 # -0.5 #log(0.400)
logq2b = 2. # log(1e3)
lnMZ = log(MZ)

alphaSMZ = 0.120 # roughly, to match [1]

Lambda0 = exp(log(MZ) - 1./(2*b0*alphaSMZ))
log10Lamda0 = log10(Lambda0)

print('Lambda={:3.1f} MeV, pole at log10(Lambda)={:1.4f}'.format(1e3*Lambda0, log10Lamda0))


# note: in next:
# 2*(x*[3] - [2]) = ln(Q^2/MZ^2)

fname = 'alphaS_run_LO'
funLO = ROOT.TF1(fname, '[0] / (1. + 2*[1]*[0]*(x*[3] - [2]))', logq2a, logq2b)
# need also a conversion constant from ln(Q) to log10(Q)=x in plotting
funLO.SetParameters(alphaSMZ, b0, lnMZ, log(10.)) #, b1)
#funLO.SetLineColor(ROOT.kBlack)
#funLO.SetLineStyle(3)

# wrong:
fname = 'alphaS_run_NLO'
funNLO = ROOT.TF1(fname, '[0] / (1. + 2*(x*[3] - [2]) * ([1]*[0]) + [4]*[0]^2  )', logq2a, logq2b)
# need also a conversion constant from ln(Q) to log10(Q)=x in plotting
funNLO.SetParameters(alphaSMZ, b0, lnMZ, log(10.), b1)
funNLO.SetLineColor(ROOT.kBlue)
funNLO.SetLineStyle(2)

# wrong:
fname = 'alphaS_run_NNLO'
funNNLO = ROOT.TF1(fname, '[0] / (1. + 2*(x*[3] - [2]) * ([1]*[0]) + [4]*[0]^2 + [5]*[0]^3 )', logq2a, logq2b)
# need also a conversion constant from ln(Q) to log10(Q)=x in plotting
funNNLO.SetParameters(alphaSMZ, b0, lnMZ, log(10.), b1, b2)
funNNLO.SetLineColor(ROOT.kRed)
funNNLO.SetLineStyle(1)

ROOT.gStyle.SetOptTitle(0)
#funNNLO.Draw('')
#funNLO.Draw('same')
#funLO.Draw('same')

funLO.Draw('')


ROOT.gPad.SetGridy(1)
ROOT.gPad.SetGridx(1)

ROOT.gPad.Update()

ROOT.gApplication.Run()
