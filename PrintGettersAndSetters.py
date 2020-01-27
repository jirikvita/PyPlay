#!/usr/bin/python

from __future__ import print_function

cname = 'cparams'
members = ['spreadFrequency', 'spreadRadius', 'dieProb', 'getWellTime', 'incubationTime', 'superSpreadFraction', 'initialSickFraction']

#cname = 'cattractor'
#members = ['x', 'y', 'radius', 'strength']

#cname = 'cperson'
#members = ['id', 'age', 'x', 'y', 'attractors', 'status']

#cname = 'cworld'
#members = ['can', 'day', 'step', 'xmin', 'xmax', 'ymin', 'ymax', 'nPeople', 'rand', 'randSpeedX', 'randSpeedY', 'cols', 'marks']

print('class {:}:'.format(cname))
print('  # code generated by PrintGettersAndSetters.py')
inits = ''
for mem in members:
    inits = inits + mem
    if members.index(mem) < len(members) - 1:
        inits = inits + ', '
print('  def __init__(self, {:}):'.format(inits))
for mem in members:
    umem = mem[0].upper() + mem[1:]
    print('    self._{:} = {:}'.format(mem, mem) ) 

print()
for mem in members:
    umem = mem[0].upper() + mem[1:]
    print('  def Get{:}(self): return self._{:}'.format(umem, mem) )
print()
for mem in members:
    umem = mem[0].upper() + mem[1:]
    print('  def Set{:}(self, {:}): self._{:} = {:}'.format(umem, mem, mem, mem) ) 
print()
