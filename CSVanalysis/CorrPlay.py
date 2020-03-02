#!/usr/bin/python3
import csv, os, sys

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from math import log10

from collections import OrderedDict

#########################################
def GetIndex(key, keys, nUniq):
    s = 0
    for key2 in keys:
        if key == key2:
            break
        s += nUniq[key2]
    return s

#########################################
def MakeLabels(uniqs, numeric = True):
    labels = []
    ikey = 0
    for key in uniqs:
        ikey += 1
        for val in uniqs[key]:
            if numeric:
                labels.append('{}: {}'.format(ikey,val))
            else:
                labels.append('{}: {}'.format(key, val))
    return labels
#########################################

#some model data;-)
Data = [ { 'A' : 'aa', 'B' : 'bd' },
         { 'A' : 'ab', 'B' : 'bc' },
         { 'A' : 'aa', 'B' : 'bc' },
         { 'A' : 'aa', 'B' : 'bd' },
         { 'A' : 'aa', 'B' : 'be' },
         { 'A' : 'ab', 'B' : 'bd' },
         { 'A' : 'ab', 'B' : 'bd' },
         { 'A' : 'aa', 'B' : 'bc' },
         { 'A' : 'aa', 'B' : 'bd' },
         { 'A' : 'ab', 'B' : 'bc' },
         { 'A' : 'ab', 'B' : 'be' },
         ]

#########################################

def DataCorr(Data, dirname, pdfdirname):

    keys = []
    for data in Data:
        for key in data:
            keys.append(key)
        break

    uniqueAnsws = {}
    for data in Data:
        ikey = 0
        for key in data:
            if not key in keys:
                keys.append(key)
            ikey += 1
            try:
                test = uniqueAnsws[key]
            except:
                uniqueAnsws[key] = []
            answ = data[key]
            if not answ in uniqueAnsws[key]:
                uniqueAnsws[key].append(answ)

    print('Unique answers are')
    print(uniqueAnsws)

    nUniq = {}
    for key in uniqueAnsws:
        nUniq[key] = len(uniqueAnsws[key])
    nKeys = len(keys)


    print('Key counts are')
    print(nUniq)

    x = []
    y = []
    N = 0
    idata = -1
    for data1 in Data:
        idata = idata + 1
        for key1 in data1:
            if idata == 0:
                N = N + nUniq[key1]
            for data2 in Data:
                for key2 in data2:
                    if key1 != key2:
                        #print(uniqueAnsws[key1].index(data1[key1]), uniqueAnsws[key2].index(data2[key2]) )
                        i1 = GetIndex(key1, keys, nUniq) + uniqueAnsws[key1].index(data1[key1])
                        i2 = GetIndex(key2, keys, nUniq) + uniqueAnsws[key2].index(data2[key2])
                        #print(key1, data1[key1], key2, data2[key2], i1, i2)
                        x.append(i1)
                        y.append(i2)

    print('N of total bins: {}'.format(N))
    print('Number of data rows: {}'.format(len(Data)))

    print(len(x), len(y))
    for xx,yy in zip(x,y):
        print(xx,yy)

    fig, ax = plt.subplots()
    ax.hist2d(x, y, bins = (range(0,N+1),range(0,N+1)), cmap=plt.cm.jet)

    bins = [  i + 0.5 for i in range(0,N) ]
    ax.set_xticks(bins)
    ax.set_yticks(bins)

    labels = MakeLabels(uniqueAnsws)
    ax.set_xticklabels(labels)
    ax.set_yticklabels(labels)


    plt.savefig('{}Corrs2d.png'.format(dirname))
    if not '00' in dirname:
        plt.savefig('{}Corrs2d.pdf'.format(pdfdirname))
    # plt.show()
        
    return fig

DataCorr(Data, '', '')
