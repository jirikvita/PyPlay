#!/usr/bin/python3
# St 18. května 2022, 14:37:57 CEST

#from __future__ import print_function

import ROOT
from math import sqrt, pow, log, exp
import os, sys, getopt
from numpy import random

cans = []
stuff = []

class cnode:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        return

class drawNNarch:
    
    def __init__(self,nNodes, cols = [], mk = 20, ms = 1.5, offx = 0.02, offy = 0.02, useMaxScale = True, nBaseDaughter = 2):
        self.nNodes = nNodes
        self.rnodes = []
        self.nodes = []
        self.slines = []
        # adjust dy spread based on the layer with maximal number of nodes
        self.useMaxScale = useMaxScale
        self.xmin = offx
        self.xmax = 1. - offx
        self.ymin = offy
        self.ymax = 1. - offy
        self.mk = mk
        self.ms = ms
        self.mc = []
        self.nBaseDaughter = nBaseDaughter # for binary or higher trees
        self.nDaughter = -1
        if len(cols) > 0:
            for col in cols:
                self.mc.append(col)
        while len(self.mc) < len(self.nNodes):
            self.mc.append(ROOT.kRed)
        if self.xmax < self.xmin:
            self.xmin,self.xmax = self.xmax,self.xmin
        if len(self.nNodes) < 1:
            print('Error, empty list of nodes counts provided!')
        else:
            self.dx = (self.xmax - self.xmin) / (len(self.nNodes)-1)
        iN = 0
        # for binary or higher trees
        for nnode in self.nNodes:
            if nnode == -1:
                self.nDaughter = self.nBaseDaughter
                self.useMaxScale = False
                self.nNodes[iN] = int(pow(self.nDaughter, iN))
            iN = iN + 1
        return
    
    def drawLayer(self, i, vertivally = False):
        x0 = self.xmin + i * self.dx
        nn0 = self.nNodes[i]
        nn = 1.*nn0
        if self.useMaxScale:
            nn = max(self.nNodes)
        dy = (self.ymax - self.ymin) / nn
        y0 = self.ymin + (nn - nn0 + 1) * dy/2
        lines = []
        rnodes = []
        nodes = []
        for j in range(0,self.nNodes[i]):
            x = 1.*x0
            y = y0 + j*dy
            # for trees, draw vertically;-)
            if self.nDaughter > 0:
                x,y = y,self.xmax - x + self.xmin
            rnode = ROOT.TMarker(x,y, self.mk)
            rnode.SetMarkerSize(self.ms)
            rnode.SetMarkerColor(self.mc[i])
            node = cnode(x,y)
            nodes.append(node)
            rnodes.append(rnode)
            if len(self.nodes) > 0:
                iold = -1
                for oldnode in self.nodes[-1]:
                    iold = iold + 1
                    if self.nDaughter > 0:
                        # we're building a tree
                        print('iold={} j={}, j/nD={} j//nD={}'.format(iold, j, j / self.nDaughter, j // self.nDaughter))
                        #if not (j == iold*self.nDaughter or j-1 == iold*self.nDaughter):
                        if not ( j // self.nDaughter == iold):
                            continue
                    line = ROOT.TObject()
                    if self.nDaughter > 0:
                        line = ROOT.TArrow(oldnode.x, oldnode.y, x, y, 0.01, '-|>-')
                    else:
                        line = ROOT.TLine(oldnode.x, oldnode.y, x, y)
                        #line.SetLineColor(ROOT.kGray+2)
                    line.Draw()
                    lines.append(line)
                print('-------------------------------------')
            rnode.Draw()
        self.rnodes.append(rnodes)
        self.nodes.append(nodes)
        self.slines.append(lines)
        return
        
    def draw(self, cn = 'nnArch', x = 1, y = 1, cw = 1000, ch = 800):
        if self.nDaughter > 0:
            cn = cn + 'Tree'
        can = ROOT.TCanvas(cn, cn, int(x), int(y), int(cw), int(ch))
        for i in range(0,len(self.nNodes)):
            self.drawLayer(i)
        # redraw markers:
        for rns in self.rnodes:
            for rn in rns:
                rn.Draw()
        can.Update()
        return can

##########################################
# https://www.tutorialspoint.com/python/python_command_line_arguments.htm
def main(argv):
    #if len(sys.argv) > 1:
    #  foo = sys.argv[1]

    ### https://www.tutorialspoint.com/python/python_command_line_arguments.htm
    ### https://pymotw.com/2/getopt/
    ### https://docs.python.org/3.1/library/getopt.html
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


    cols = [ROOT.kBlack, ROOT.kBlue, ROOT.kGreen+2, ROOT.kRed, ROOT.kMagenta, ROOT.kCyan, ROOT.kGray]

    doRandom = False

    nNodes = [ [ 10, 20, 10, 5],
               [ 10, 20, 5],
               [ 10, 30, 10, 5],
               [ 10, 15, 15, 5],
               [ 10, 20, 40, 20, 5],
               [ 10, 40, 30, 20, 5],
               [ 20, 10, 5, 2]
               ]
    if doRandom:
        nNodes = []
        # make random architectures:
        nNnodes = []
        ngen = 2 # 12
        meannlay = 5
        meannodes = 15
        minnl = 3
        minn = 5
        for ig in range(ngen):
            nodes = []
            nl = max(minnl,random.poisson(meannlay))
            for il in range(nl):
                nn = max(minn, random.poisson(meannodes))
                nodes.append(nn)
            nNodes.append(nodes)

    # the binary tree:
    nNodes.append([-1, -1, -1, -1, -1])
    drawnns = []
    iN = -1
    for nNode in nNodes:
        iN = iN+1
        drawnn = drawNNarch(nNode, cols)
        drawnns.append(drawnn)
        cn = 'nnArch{}'.format(iN)
        x = iN*50
        y = iN*50
        can = drawnn.draw(cn, x, y)
        cans.append(can)
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

