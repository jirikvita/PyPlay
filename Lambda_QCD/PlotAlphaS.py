#!/usr/bin/python

# jk 18.11.2022

from math import log10, log, pow, sqrt, exp, pi

import ROOT

# running coupling of QCD:

TR = 1/2.
CA = 3
CF = 4/3.

nf = 3
b0 = (11*CA - 4*TR*nf) / (12*pi)
b1 = (18*CA*CA - 10*TR*CA*nf - 6*TR*CF*nf) / (24*pi*pi)


# in GeV
MZ = 92.3
logq2a = -0.5 #log(0.400)
logq2b = 2. # log(1e3)
lnMZ = log(MZ)

alphaSMZ = 0.116

Lambda0 = exp(log(MZ) - 1./(2*b0*alphaSMZ))
log10Lamda0 = log10(Lambda0)

print('Lambda={:3.1f} MeV, pole at log10(Lambda)={:1.4f}'.format(1e3*Lambda0, log10Lamda0))


fname = 'alphaS_run'
fun = ROOT.TF1(fname, '[0] / (1. + 2*[1]*[0]*(x*[3] - [2]))', logq2a, logq2b)
# need also a conversion constant from ln(Q) to log10(Q)=x in plotting
fun.SetParameters(alphaSMZ, b0, lnMZ, log(10.)) #, b1)

fun.Draw()

ROOT.gApplication.Run()
