#!/usr/bin/python
# jk 10.5.2018

from cplx import Complex
print('----------------')
# zero test:
z = Complex()
z.PrintPretty()
z.Divide(z)
print('----------------')
z0 = Complex(0., 1.)
z0.PrintReIm()
z0.PrintPolar()
print('----------------')
z1 = Complex(-1.5, 1.)
z1.PrintReIm()
z1.PrintPolar()
print('--- addition ---')
(z0+z1).PrintReIm()
(z0+z1).PrintPolar()
print('--- subtraction ---')
(z0-z1).PrintReIm()
(z0-z1).PrintPolar()
print('----------------')
z1 = Complex(1.5, 1.5)
z1.PrintReIm()
z1.PrintPretty()
print('----------------')
z1 = Complex(-1.5, 1.5)
z1.PrintReIm()
z1.PrintPretty()
print('----------------')
z5 = Complex(-1.5, -1.5)
z5.PrintReIm()
z5.PrintPretty()
print('----------------')
z6 = Complex(1.5, -1.5)
z6.PrintReIm()
z6.PrintPretty()
print('---- Multiply ----')
(z0*z1).PrintPolar()
(z0*z1).PrintReIm()
#zz = Complex(z0)
#zz.Multi(z1)
#zz.PrintReIm()
zz = Complex(z0)
zz.AltMulti(z1)
zz.PrintReIm()
print('---- Divide ----')
(z0/z1).PrintPolar()
(z0/z1).PrintReIm()
zz = Complex(z0)
zz.AltDivide(z1)
zz.PrintReIm()
print('----------------')
print('---- Square ----')
z0.PrintReIm()
z3 = Complex(z0)
#z3.Set(z0)
z3.Pow(2.)
z3.PrintReIm()
print('--- Conjuate ---')
z4 = z0.GetConjugate()
z0.Print()
z4.Print()
#z4.Print('reim')
z4.Print('polar')
z4.Print('pretty')
print('----------------')



