#!/usr/bin/python

# jk 26.4.2022

# https://www.geeksforgeeks.org/operator-overloading-in-python/
# https://www.delftstack.com/howto/python/print-object-python/

from math import pow, sqrt, atan, sin, cos


class cplx:
    def __init__(self, re, im):
        self.re = re
        self.im = im

    def __add__(self, right):
        return cplx(self.re + right.re, self.im + right.im)
    def __neg__(self):
        return cplx(-self.re, -self.im)
    def __sub__(self, right):
        return self + (-right)
    def __repr__(self):
        return '{:+f}{:+f}i'.format(self.re, self.im)
    def __mul__(self, right):
        return cplx(self.re*right.re - self.im*right.im, self.re*right.im + self.im*right.re)

    def mag(self):
        val = pow(self.im,2) + pow(self.re,2)
        if val > 0.:
            return sqrt(val)
        return 0.
    def __div__(self, right):
        val = right.mag()
        if val > 0.:
            return cplx( (self.re*right.re + self.im*right.im) / val, (-self.re*right.im + self.im*right.re) / val)
        return cplx(0.,0.)

    def phi(self):
        return atan(re,im)
    def r(self):
        return self.mag()
    def conjug(self):
        self.im = -self.im
    def getconjug(self):
        return cplx(self.re, -self.im)


c1 = cplx(1., 2.)
c2 = cplx(-3., 1.)
print(c1,c2)
print(c1+c2)
print(c1-c2)
print(c1*c2)
print(c1/c2)
cc1 = c1.getconjug()
cc2 = c2.getconjug()
print(c1,c2)
print(c1*cc1)
print(c2*cc2)

