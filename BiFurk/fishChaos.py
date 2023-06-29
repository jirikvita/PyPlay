#!/snap/bin/pyroot
# was: #!/usr/bin/python3
# Čt 29. června 2023, 19:01:02 CEST

#from __future__ import print_function

# model of fish population
# chaotic deterministic system
# inspired by Veda podle abecedy by Petr Koubsky
# see also https://geoffboeing.com/2015/03/chaos-theory-logistic-map/
# https://courses.lumenlearning.com/waymakermath4libarts/chapter/logistic-growth/
# https://math.stackexchange.com/questions/2738034/population-growth-model-with-fishing-term-logistic-differential-equation


import ROOT
from math import sqrt, pow, log, exp
import os, sys, getopt

cans = []
stuff = []

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

    ROOT.gStyle.SetPalette(1)

    print('*** Settings:')
    print('tag={:}, batch={:}'.format(gTag, gBatch))


    def iterate(y0, r, cycles):
        y = 1.*y0
        for i in range(0, cycles):
            y = r*y*(1.-y)
        return y

    def MakeGraph(y0, rmin,     rmax, n, step):
        gr = ROOT.TGraph()
        ip = -1
        for r in [rmin + step * j for j in range(0, n)]:
            ip = ip + 1
            yconverged = iterate(y0, r, cycles)
            #print(ip,r,yconverged)
            gr.SetPoint(ip, r, yconverged)
        return gr

    rmax = 4.
    rmin = 2.4
    n = 3000
    step = (rmax - rmin) / n
    cycles = 350
    nn = 100
    y0s = [1./nn*(j+1) for j in range(0, nn)]
    grs = []
    for y0 in y0s:
        print(f'y0={y0}')
        gr = MakeGraph(y0, rmin, rmax, n, step)
        grs.append(gr)
        
    canname = 'FishChaos'
    can = ROOT.TCanvas(canname, canname, 0, 0, 1200, 900)
    cans.append(can)
    opt = 'P pmc'
    hn = 'tmp'
    h = ROOT.TH2D(hn, hn + ';r;converged y', 1000, rmin, rmax, 1000, 0, 1)
    h.SetStats(0)
    ROOT.gStyle.SetOptTitle(0)
    h.Draw()
    #opt = 'AP pmc'
    for gr in grs:
        gr.SetMarkerStyle(20)
        gr.SetMarkerSize(0.2)
        gr.Draw(opt)
        #opt = 'P pmc'
    can.Update()
    can.Print(can.GetName() + '.png')
    #can.Print(can.GetName() + '.pdf')
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

