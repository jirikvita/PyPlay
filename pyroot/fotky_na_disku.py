#!/snap/bin/pyroot
# was: #!/usr/bin/python3
# Po 26. prosince 2022, 12:24:00 CET

#from __future__ import print_function

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

    print('*** Settings:')
    print('tag={:}, batch={:}'.format(gTag, gBatch))

    canname = 'can'
    can = ROOT.TCanvas(canname, canname)
    cans.append(can)
    
    fulldata = {
        1999 : 0.001069,
        2001 : 0.006216,
        2002 : 0.09563,
        2003 : 0.1106,
        2004 : 0.3288,
        2005 : 0.1166,
        2006 : 3.189,
        2007 : 4.018,
        2008 : 16.183,
        2009 : 43.66,
        2010 : 71.82,
        2011 : 162.5,
        2012 : 345.6,
        2013 : 864.3,
        2014 : 914.7,
        2015 : 723.9,
        2016 : 420.8,
        2017 : 480.1,
        2018 : 471.3,
        2019 : 513.4,
        2020 : 715.6,
        2021 : 561.1,
        2022 : 363.98,
    }
    descr = 'Total photo size'
    data = { descr : fulldata, }
    hs = {}
    cols = { descr : ROOT.kBlue}
            
    #opt = "A b"
    for Y in data:
        hname = 'h_{}'.format(Y)
        htitle = hname + ';year;GiB'
        x1 = 1997.5
        x2 = 2023.5
        nbins = int(x2-x1)
        h1 = ROOT.TH1D(hname, htitle, nbins, x1, x2)
        h1.SetStats(0)
        hs[Y] = h1
        ip = -1
        for m in data[Y]:
            ip = ip + 1
            h1.Fill(m, data[Y][m])
            h1.SetBinError(h1.FindBin(m), 0.)
            
        #h1.SetMarkerStyle(20)
        #h1.SetMarkerSize(2)
        #h1.SetMarkerColor(ROOT.kBlack)
        h1.SetFillColor(cols[Y])
        h1.SetFillStyle(1111)
        h1.Scale(1.)
        h1.SetMinimum(0.)
        
    boff = 0.1
    w = 1.
    nhs = len(hs)
    opt = 'bar2'
    iy = 0
    ymax = -9e9
    for Y in hs:
        h = hs[Y]
        hm = h.GetMaximum()
        if hm > ymax:
            ymax = 1.*hm
    
    ROOT.gStyle.SetOptTitle(0)
    for Y in hs:
        h = hs[Y]
        h.SetMaximum(1.3*ymax)
        bw = (w - 2*boff) / nhs
        h.SetBarWidth(bw)
        h.SetBarOffset(boff + iy*bw)
        
        h.Draw(opt)
        opt = opt + 'same'
        iy = iy + 1
        
    leg = ROOT.TLegend(0.15,0.75,0.45,0.88)
    leg.SetBorderSize(0)
    for Y in hs:
        leg.AddEntry(hs[Y],'{} {:1.0f} TiB'.format(Y, hs[Y].Integral()/1000.),"f")
    leg.Draw()
    stuff.append(leg)
    ROOT.gPad.Update()
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

