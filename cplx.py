#!/usr/bin/python


# jk 10.5.2018
# http://blog.teamtreehouse.com/operator-overloading-python


from __future__ import print_function

from math import sqrt, pow, tan, atan, sin, cos, pi, fabs

gEpsilon = 1e-10


class Complex:
    #def __init__(self, re = 0., im = 0.):
    #    self._re = re
    #    self._im = im
    #    self._r = 0.
    #    self._phi = 0.
    #    self.ComputePolar()
    def __init__(self, *args):
        if len(args) == 1:
            # expect initiation by an instance of Complex
            self.Set(args[0])
        elif len(args) == 2:
            self._re = args[0]
            self._im = args[1]
            #self._r = 0.
            #self._phi = 0.
            self.ComputePolar()
        else:
            self._re = 0.
            self._im = 0.
            self._r = 0.
            self._phi = 0.
            
    def Set(self, z):
        self._re = z.Re()
        self._im = z.Im()
        self.ComputePolar()
    def Re(self):
        return self._re
    def Im(self):
        return self._im
    def R(self):
        return self._r
    def Phi(self):
        return self._phi

    def SetRe(self, re):
        self._re = re
        self.ComputePolar()
    def SetIm(self, im):
        self._im = im
        self.ComputePolar()
    def SetR(self, r):
        self._r = r
        self.ComputeReIm()
    def SetPhi(self, phi):
        self._phi = phi
        self.ComputeReIm()

        
    def GetConjugate(self):
        z = Complex(self.Re(), -self.Im())
        return z
    def Conjugate(self):
        self.im = -1.*self._im
        self.ComputePolar()

    def ComputePolar(self):
        self._r = sqrt (pow(self._re, 2) + pow(self._im, 2) )
        self._phi = self.MakePhi()
    def MakePhi(self):
        # to keep phi in (0, pi)
        phi = 0.
        if fabs(self._re) > gEpsilon:
            phi = atan(self._im / self._re)
        else:
            if self._im > 0.:
                phi = pi/2.
            else:
                phi = -pi/2.
        if (self.Re() < -gEpsilon and phi < 0.) or (self.Re() < -gEpsilon and phi > 0.):
            phi = phi + pi
        if phi < 0:
            phi = 2*pi + phi
        return phi

    def ComputeReIm(self):
        self._re = self._r*cos(self._phi)
        self._im = self._r*sin(self._phi)

    
    def Add(self, z, K = 1.):
        self._re = self._re + K*z.Re()
        self._im = self._im + K*z.Im()
        self.ComputePolar()
    def __add__(self, right):
        left = Complex(self._re, self._im)
        left.Add(right)
        return left
    def __sub__(self, right):
        left = Complex(self._re, self._im)
        left.Add(right, -1.)
        return left

    def __mul__(self, right):
        left = Complex(self._re, self._im)
        left.Multi(right)
        return left
    def __div__(self, right):
        left = Complex(self._re, self._im)
        left.Divide(right)
        return left

    
    def Multi(self, z):
        self._phi = self._phi + z.Phi()
        self._r = self._r*z.R()
        self.ComputeReIm()

    # alternative multiplication method:
    def AltMulti(self, z):
        a = self.Re()
        b = self.Im()
        c = z.Re()
        d = z.Im()
        # (a+ib)(c+id)
        self._re = a*c - b*d
        self._im = a*d + c*b
        self.ComputePolar()

    def Divide(self, z):
        self._phi = self._phi - z.Phi()
        if z.R() > 0.:
            self._r = self._r/z.R()
        else:
            print('Complex::Divide: error dividing by complex number! Zero modulus given!')
        self.ComputeReIm()

    # alternative division method:
    def AltDivide(self, z):
        a = self.Re()
        b = self.Im()
        c = z.Re()
        d = z.Im()
        denum = c*c+d*d
        # (a+ib)(c-id) / (cc+dd)
        self._re = a*c + b*d
        self._im = -a*d+c*b
        if fabs(denum) > gEpsilon:
            self._re = self._re / denum
            self._im = self._im / denum
        else:
            print('Complex::AltDivide: error dividing by complex number! Zero modulus given!')
        self.ComputePolar()

        
    def Pow(self, a):
        self._phi = self._phi * a
        self._r = pow(self._r, a)
        self.ComputeReIm()
        
    def PrintReIm(self):
        print('{:2.3f}{:+2.3f}i'.format(self.Re(), self.Im()))
    def PrintPolar(self):
        print('{:f}*exp({:f}i)'.format(self.R(), self.Phi()))
    def PrintPretty(self):
        print('{:1.2f}*exp({:1.2f}i*pi)'.format(self.R(), self.Phi() / pi))
    def Print(self, mode = 'REIM'):
        mode = mode.upper()
        if 'POLAR' in mode:
            self.PrintPolar()
        elif 'PRETTY' in mode:
            self.PrintPretty()
        else:
            self.PrintReIm()
            
