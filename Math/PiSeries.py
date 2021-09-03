#!/usr/bin/python


sum = 0.
sgn = 1
for i in range(0,10000):
    sum = sum + 4.*sgn/(2.*i+1)
    sgn = -sgn

print sum
