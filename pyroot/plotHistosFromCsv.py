#!/snap/bin/pyroot
# was: #!/usr/bin/python3
# Ne 15. ledna 2023, 16:10:23 CET

#from __future__ import print_function

import ROOT
from math import sqrt, pow, log, exp
import os, sys, getopt

stuff = []

cols =  { 0 : ROOT.kBlack,
           1 : ROOT.kGray + 2,
           2 : ROOT.kGray + 1,
           3: ROOT.kGreen + 2,
           4: ROOT.kBlue
          }
sampleName = { 0 : 't#bar{t} p_{T,j1,j2}^{min} = 200 GeV',
               1 : 't#bar{t} p_{T,j1,j2}^{min} = 60 GeV, p_{T,j1,j2}^{max} = 200 GeV',
               2 : 't#bar{t} p_{T,j1}^{min} = 200 GeV, p_{T,j2} #in (60,200) GeV',
               3: "Z' m=1000 GeV",
               4: "Z' m=1250 GeV"
              }

xLabels = {'tau21' : '#tau_{21}',
           'tau32' : '#tau_{32}',
           'mass' : 'm_{J} [GeV]'}

####################################################################################

def MakeHisto(items, sample, isample, var):
    print('  in MakeHisto:')
    vals = []
    print('    B items: ', items)
    for item in items:
        val = float(item)
        vals.append(val)
    print('    C vals: ', vals)
    nbins = 42
    x1 = 0
    x2 = 210
    if 'tau' in var:
        nbins = 40
        x1 = 0.
        x2 = 1.
    
    print('Histo ', nbins, x1, x2)
    hname = '{}_{}'.format(var, sample)
    htitle = hname + ';{};jet fraction [%]'.format(xLabels[var])
    h = ROOT.TH1D(hname, htitle, nbins, x1, x2)
    ibin = 1
    for val in vals:
        h.SetBinContent(ibin, val)
        ibin = ibin + 1
    h.Scale(1./h.Integral())
    h.Scale(100.)
    h.SetStats(0)
    h.SetLineColor(cols[isample])
    h.SetFillColorAlpha(cols[isample], 0.2)
    h.SetFillStyle(1111)
    h.SetLineWidth(2)
    return h

####################################################################################
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
    ROOT.gStyle.SetOptTitle(0)
        
    print('*** Settings:')
    print('tag={:}, batch={:}'.format(gTag, gBatch))

    path = 'histogramsNew/'
    fnames = ['tau21.csv', 'tau32.csv', 'mass.csv']
    hists = {}
    
    for fname in fnames:
        print('=== Fname: {}'.format(fname))
        var = fname.replace('.csv','')
        hists[var] = []
        samples = []
        lines = []
        infile = open(path + fname, 'r')
        isample = 0
        for xline in infile.readlines():
            line = xline[:-1] # remove CR
            print('*** isample: {}'.format(isample))
            print('line: ', line)
            lines.append(line)
            items = line.split(',')
            sample = items[0].replace('/','')
            if sample == '':
                print('ERROR: sample str is empty! Skipping...')
                continue
            print('-- Sample: {}, var: {}'.format(sample, var))
            print('A items: ', items)
            samples.append(sample)
            histo = MakeHisto(items[1:], sample, isample, var)
            hists[var].append(histo)
            isample = isample + 1


    cans = {}
    legs = {}
    for var in hists:
        canname = 'histo_{}'.format(var)
        cans[var] = ROOT.TCanvas(canname, canname, 0, 0, 900, 800)
        leg = ROOT.TLegend(0.30, 0.65, 0.88, 0.88)
        leg.SetBorderSize(0)
        opt = ''
        print('Hists for {}: {}'.format(var, len(hists[var])))
        ymax = -999
        for isample in range(0, len(hists[var])):
            h = hists[var][isample]
            hm = h.GetMaximum()
            if hm > ymax:
                ymax = 1.*hm

        for isample in range(0, len(hists[var])):
            h.SetMaximum(1.6*ymax)
            h = hists[var][isample]
            h.Draw('hist' + opt)
            leg.AddEntry(h, sampleName[isample], 'LF')
            opt = 'same'
        
        leg.Draw()
        legs[var] = leg
        
    stuff.append(cans)
    stuff.append(legs)
    stuff.append(hists)
    for var in cans:
        can = cans[var]
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

