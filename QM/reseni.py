#!/usr/bin/python

from myAll import *

from math import pi, sqrt, pow, sin, cos, exp


h = 6.62606957e-34  # Js
hb = h/pi           # Js
c = 299792458.      # m s-1
e = 1.602176565e-19 # C
k = 1.3806488e-23   # J/K
me = 511.e3*e/c/c  # kg
alpha = 1/137.0356
mu = 931.e6 * e / (c*c)

print "me:"
print me

def GetPc_eV(lbd):
    return h*c / lbd / e

def GetP(lbd):
    return h / lbd 


# light:
lbd = 500.e-9 #m

print 'Photon momentum in SI and eV for lambda=%f' % (lbd)
print GetP(lbd)
print GetPc_eV(lbd)


print "Roentgen:"
lbd=0.1e-9
# roentgen: 0.01 to 10 nanometers
print GetP(lbd)
print GetPc_eV(lbd)


# 4)
print "Photon wavelength from e+e- annihilation:"
print h/(me*c)

# 5)
print "Radio waves 30m, P=1 W"
print "Energy in eV:"
lbd = 30
print h*c/lbd/e
print "Photons per s:"
print 1*lbd/(h*c)

# 6)
print "Free electron gamma capture"
print sqrt(2*hb/(me*c))


# 12)
print "Molecule of oxygen wave length:"
T = 300
print h / sqrt(6*k*T*16*mu)
m = 1e-6 # kg
v = 330 # m/s
print h/(m*v)

#13)
print "Klassical Bohr electron energy in eV:"
r = hb/(alpha*me*c)
print 0.5*hb*c*alpha/r/e
print 0.5*pow(alpha*c,2)*me/e

#################################################
# plotting:


# lambdas in nm:
x1=  1e-6
x2 = 1e-7
T = 300

RJ = "[0]*[1]/x^4"
funRF = ROOT.TF1("Rayleight-Jeans", RJ,  x1, x2)
funRF.SetParameters(2*c*k, T)
funRF.SetLineColor(1)
funRF.SetNpx(10000)

Planck = "[0]/x^5 * 1/(exp([1]/(x*[2])) - 1)"
funPlanck = ROOT.TF1("Planck", RJ,  x1, x2)
funPlanck.SetParameters(2*h*c*c, h*c/k, T)
funPlanck.SetLineColor(2)
funPlanck.SetNpx(10000)

can = nextCan.nextCan()
funRF.Draw()
#funPlanck.Draw("same")
#funPlanck.Draw()
can.Print("can.eps")



ROOT.gApplication.Run()
