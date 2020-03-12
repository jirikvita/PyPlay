#!/usr/bin/python
# Thu 12 Mar 12:20:43 CET 2020

from __future__ import print_function

import ROOT
from math import sqrt, pow, log, exp
import os, sys, getopt

cans = []
stuff = []

##########################################
def MakeGraphs(fname):
    csvfile = open(fname, 'r')
    graphs = {}
    iline = -1
    dates = []
    
    for xline in csvfile.readlines():
        iline = iline + 1
        line = xline[:-1]
        items = line.split(',')[:-1]
        if iline == 0:
            dates = items[4:]
            continue
        graph = ROOT.TGraphErrors()
        vals = items[4:]
        province,state = items[0], items[1]

        # skip provinces for the moment
        if province != '' and province != 'Hubei' and province != 'UK':
            continue
        print(items)
        gname = '{}{}'.format(province,state)
        if province != '':
            gname = '{} {}'.format(province,state)
        graph.SetName(gname)
        ip = 0
        id = 0
        for date,sval in zip(dates,vals):
            val = int(sval)
            if val > 0:
                graph.SetPoint(ip, id+1, val)
                err = sqrt(val)
                graph.SetPointError(ip, 0, err)
                ip = ip + 1
            id = id + 1
        graphs[gname] = graph
    return graphs

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

    canname = 'ConfirmedCases'
    can = ROOT.TCanvas(canname, canname)
    cans.append(can)

    filename = 'time_series_19-covid-Confirmed.csv'
    graphs = MakeGraphs(filename)
    opt = 'PL'
    can.cd()
    ROOT.gPad.SetLogy(1)
    ROOT.gPad.SetGridy(1)
    ROOT.gPad.SetGridx(1)
    h2 = ROOT.TH2D("tmp", "tmp;days;Cases", 100, -40, 55, 500, 1., 1.e5)
    h2.SetStats(0)
    h2.SetTitle('')
    h2.Draw()
    countries = []
    CountriesToPlot = [ 'Hubei China', 'Italy', 'Germany', 'France', 'Spain', 'Japan', 'Korea South', 'Czechia', 'UK United Kingdom']
    leg = ROOT.TLegend(0.12, 0.52, 0.34, 0.88)
    
    for gname in graphs:
        countries.append(gname)
    print(countries)
    cols = [ROOT.kRed, ROOT.kBlack, ROOT.kBlue, ROOT.kGreen+2, ROOT.kViolet,
            ROOT.kOrange+10, ROOT.kTeal, ROOT.kPink, ROOT.kAzure+4, ROOT.kMagenta,
            ROOT.kSpring, ROOT.kBlue+2, ROOT.kGray+2]
    
    msts = range(20, 50)
    lsts = range(1, 30)

    ig = -1
    for gname in graphs:
        if gname not in CountriesToPlot:
            continue
        graph = graphs[gname]
        ig = ig + 1
        graph.SetMarkerColor(cols[ig])
        graph.SetLineColor(cols[ig])
        graph.SetMarkerStyle(msts[ig])
        graph.SetMarkerSize(1)
        leg.AddEntry(graph, gname, 'PL')
        graph.Draw(opt)
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

