#!/usr/bin/python
# Thu 17 Oct 09:24:40 CEST 2019

from __future__ import print_function

import ROOT
from math import sqrt, pow, log, exp, pi
import os, sys, getopt

cans = []
stuff = []

##########################################
def MakeAndDraw2DFun(name, X, N, npx = 150, npy = 150):
    xmin = X[0][0]
    xmax = X[0][1]
    ymin = X[1][0]
    ymax = X[1][1]
    fun2d = ROOT.TF2(name, "[0]*(sin([1]*x)*sin([2]*y))^2", xmin, xmax, ymin, ymax)
    # arb. normalization:
    fun2d.SetParameter(0, 1.)
    i = 0
    for n in N:
        fun2d.SetParameter(i+1, n*pi / (X[i][1] - X[i][0]))
        i = i+1
    fun2d.SetNpx(npx)
    fun2d.SetNpy(npy)
    fun2d.Draw("colz")    
    stuff.append(fun2d)
    return fun2d
##########################################

def MakeAndDraw3DHist(name, X, N, Ngen =  50000, nx = 80):
    xmin = X[0][0]
    xmax = X[0][1]
    ymin = X[1][0]
    ymax = X[1][1]
    zmin = X[2][0]
    zmax = X[2][1]
    ny = nx
    nz = nx
    fun3d = ROOT.TF3('fun' + name, "[0]*(sin([1]*x)*sin([2]*y)*sin([3]*z))^2", xmin, xmax, ymin, ymax, zmin, zmax)
    stuff.append(fun3d)
    # arb. normalization:
    fun3d.SetParameter(0, 1.)
    i = 0
    for n in N:
        fun3d.SetParameter(i+1, n*pi / (X[i][1] - X[i][0]))
        i = i+1
    h3 = ROOT.TH3D("h3"+name, "h3"+name, nx, xmin, xmax, ny, ymin, ymax, nz, zmin, zmax)
    stuff.append(h3)
    h3.FillRandom("fun3d", Ngen)
    h3.SetStats(0)
    return h3


##########################################
# https://www.tutorialspoint.com/python/python_command_line_arguments.htm
def main(argv):
    #if len(sys.argv) > 1:
    #  foo = sys.argv[1]

    ### https://www.tutorialspoint.com/python/python_command_line_arguments.htm
    ### https://pymotw.com/2/getopt/
    ### https://docs.python.org/3.1/library/getopt.html


    ROOT.gStyle.SetOptTitle(0)

    gBatch = False
    gTag=''
    print(argv[1:])
    try:
        # options that require an argument should be followed by a colon (:).
        opts, args = getopt.getopt(argv[2:], 'hbt:', ['help','batch','tag='])

        print('Got options:')
        print(opts)
        print(args)
    except getopt.GetoptError:
        print('Parsing...')
        print ('Command line argument error!')
        print('{:} [ -h -b --batch -tTag --tag="MyCoolTag"]]'.format(argv[0]))
        sys.exit(2)
    for opt,arg in opts:
        print('Processing command line option {} {}'.format(opt,arg))
        if opt == '-h':
            print('{:} [ -h -b --batch -tTag --tag="MyCoolTag"]'.format(argv[0]))
            sys.exit()
        elif opt in ("-b", "--batch"):
            gBatch = True
        elif opt in ("-t", "--tag"):
            gTag = arg
            print('OK, using user-defined histograms tag for output pngs {:}'.format(gTag,) )

    if gBatch:
        ROOT.gROOT.SetBatch(1)

    print('*** Settings:')
    print('tag={:}, batch={:}'.format(gTag, gBatch))

    canname = 'InfWell2D'
    ww = 800
    can = ROOT.TCanvas(canname, canname, 0, 0, ww, ww)
    cans.append(can)
    #filename = 'foo.root'
    #rfile = ROOT.TFile(filename, 'read')
    #hname = 'histo_h'
    #h1 = rfile.Get('hname')

    # 2D function
    X = [ [0., 1.], [0., 1.]]
    Ns = [ [1, 1], [2, 1], [3, 1],
           [4, 2], [2, 2], [3, 2],
           [4, 3], [5, 4], [3, 3],
    ]
    j = 0
    can.Divide(3,3)
    for N in Ns:
        can.cd(j+1)
        fun2d = MakeAndDraw2DFun('fun2d_{:}'.format(j), X, N)
        j = j+1
    
    # 3D histo
    X = [ [0., 1.], [0., 1.], [0., 1.]]
    
    canname = 'InfWell3D'
    can = ROOT.TCanvas(canname, canname, 100, 100, ww, ww)
    cans.append(can)

    can.Divide(3,3)
    Ns = []
    j = 0
    Ns = [  [1, 1, 1], [2, 1, 1], [3, 2, 1],
            [3, 4, 1], [2, 2, 2], [3, 2, 2],
            [4, 3, 2], [3, 5, 4], [3, 3, 3],
    ]
    for N in Ns:
        can.cd(j+1)
        ROOT.gPad.SetPhi(42.)
        ROOT.gPad.SetTheta(40.)
        h3 = MakeAndDraw3DHist('3d', X, N)
        h3.SetMarkerColor(ROOT.kBlue+2)
        j = j+1
        h3.Draw()
    for can in cans:
        can.Print(can.GetName() + '.png')
        can.Print(can.GetName() + '.pdf')
 

    
    ROOT.gApplication.Run()
    return

###################################
###################################
###################################

if __name__ == "__main__":
    # execute only if run as a script"
    main(sys.argv)
    
###################################
###################################
###################################

