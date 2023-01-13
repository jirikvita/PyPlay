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
    
    data2021 = { 1 : 13.3,
                 2 :  4.3,
                 3 :  3.2,
                 4 :  9.7,
                 5 : 19.3,
                 6 :  3.4,
                 7 :  3.4,
                 8 : 11.4,
                 9 : 25.1,
                10 : 11.6,
                11 : 28.8,
                12 : 10.1,
        }
    
    data2022 = { 1 :  4.2,
                 2 : 21.7,
                 3 :  9.8,
                 4 : 26.0,
                 5 : 20.8,
                 6 : 43.3,
                 7 :  7.5,
                 8 : 20.0,
                 9 : 23.7,
                10 : 34.6,
                11 : 40.6,
                12 : 44.8 - 10.7, # korekce ceske drahy, prac. cesta
            }
    
    data2023 = { 1 : 46.4,}
    
    data = {2021 : data2021,
            2022 : data2022,
            2023 : data2023}
    hs = {}
    cols = {2021 : ROOT.kGreen+2, 
            2022 : ROOT.kBlue,
            2023 : ROOT.kRed + 2}
    #opt = "A b"
    for Y in data:
        hname = 'h_{}'.format(Y)
        htitle = hname + ';month;CZK'
        x1 = 0.5
        x2 = 12.5
        nbins = int(x2-x1)
        h1 = ROOT.TH1D(hname, htitle, nbins, x1, x2)
        h1.SetStats(0)
        hs[Y] = h1
        ip = -1
        for m in data[Y]:
            ip = ip + 1
            h1.SetBinContent(m, data[Y][m])
            h1.SetBinError(m, 0.)
            
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
        leg.AddEntry(hs[Y],'{}'.format(Y),"f")
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

