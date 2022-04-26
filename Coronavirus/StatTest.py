#!/usr/bin/python

import ROOT

import random

print('Usage: time ./StatTest.py')

r3 = ROOT.TRandom3()
N = 10000000

# steering!
testROOT = False

if testROOT:
    print('Testing ROOT rand speed...')
else:
    print('Testing python rand speed...')
    
for i in range(0,N):
    if testROOT:
        y = r3.Uniform(0,1)
    else:
        y = random.uniform(0,1)
        
