#!/usr/bin/python3
# jiri kvita 2020

from math import log10

# distance scaling:
gkm = 1.


cans = []
stuff = []

#########################################
def CountPeople(families):
    n = 0
    for fam in families:
        n = n + len(fam.GetMembers())
    return n

#########################################
def MakeDigitStr(i, digits = 4):
    tag = str(i)
    n = digits
    try: 
        n = int(log10(i))
    except ValueError:
        pass
    if i is 0:
        n = 0
    for i in range(0, digits - n):
        tag = '0' + tag
    return tag


