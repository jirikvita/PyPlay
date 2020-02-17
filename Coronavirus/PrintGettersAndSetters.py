#!/usr/bin/python
# jiri kvita 2020

from __future__ import print_function

#cname = 'cparams'
#members = ['spreadFrequency', 'spreadRadius', 'deathProb', 'healProb', 'getWellTime', 'incubationTime', 'superSpreadFraction', 'initialSickFraction', 'maxDaysSick', 'ageDeathFact', 'maxAge']

#cname = 'cattractor'
#members = ['x', 'y', 'rmin', 'rmax', 'strength']

#cname = 'cperson'
#members = ['id', 'age', 'x', 'y', 'attractors', 'status', 'sickDays', 'healed', 'nDaysInStatus']

cname = 'cworld'
members = ['can', 'histos', 'day', 'step', 'xmin', 'xmax', 'ymin', 'ymax', 'nPeople', 'rand', 'randSpeedX', 'randSpeedY', 'cols', 'marks', 'attractorIndex']

#cname = 'cfamily'
#members = ['members', 'x0', 'y0']

print('')
print('')
print('#########################################')
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
print('')