#!/usr/bin/python
# Thu 12 Mar 12:20:43 CET 2020
# using data from https://github.com/CSSEGISandData/COVID-19

#,Czechia,49.8175,15.473,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,4,5,8,12,19,26,32,38,63,94,113,141,189,298,383,434
#,Czechia,49.8175,15.473,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,4,5,8,12,19,26,32,38,63,94,113,141,189,293,344

from __future__ import print_function

import ROOT
from math import sqrt, pow, log, exp
import os, sys, getopt

cans = []
stuff = []

kMinCasesToPlot = 4
kLastDaysToFit = 14
kLastDaysToFitShort = 7
kHistoryDay0 = 30

kAcceptProvinces = ['', 'Hubei', 'Hong Kong' ,'United Kingdom' ,'British Columbia' ,'Washington' ,'France'] # 

##########################################
def GetChi2Ndf(fit):
    chi2 = fit.GetChisquare()
    ndf = fit.GetNDF()
    return chi2,ndf
def GetChi2Str(chi2,ndf):
    if ndf > 0:
        return '#chi^{2}/ndf' + '={:1.1f}'.format(chi2/ndf)
    else:
        return 'ndf=0!'

##########################################
def MakeGraphs(fname):
    csvfile = open(fname, 'r')
    graphs = {}
    iline = -1
    dates = []
    
    for xline in csvfile.readlines():
        iline = iline + 1
        line = xline[:-1]
        items = line.split(',')
        if iline == 0:
            dates = items[4:]
            continue
        graph = ROOT.TGraphErrors()
        vals = items[4:]
        province,state = items[0], items[1]

        # skip provinces for the moment
        if province not in kAcceptProvinces:
            continue
        print(items)
        gname = '{}{}'.format(province,state)
        if province != '':
            gname = '{} {}'.format(province,state)
        if gname == 'France France':
            gname = 'France'
        if gname == 'Hong Kong China':
            gname = 'Hong Kong'
        if gname == 'British Columbia Canada':
            gname = 'Canada, BC'
        if gname == 'United Kingdom United Kingdom':
            gname = 'UK'
        graph.SetName(gname)
        ip = 0
        id = -len(dates)
        for date,sval in zip(dates,vals):
            if sval == '':
                continue
            if sval[-1] == '\r':
                sval = sval[:-1]
            val = int(sval)
            if val > kMinCasesToPlot:
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

    ROOT.gStyle.SetPadTickX(1);
    ROOT.gStyle.SetPadTickY(1);
        
    print('*** Settings:')
    print('tag={:}, batch={:}'.format(gTag, gBatch))

    canname = 'ConfirmedCases'
    can = ROOT.TCanvas(canname, canname, 0, 0, 800, 1200)
    cans.append(can)

    filename = 'time_series_19-covid-Confirmed.csv'
    graphs = MakeGraphs(filename)

    
    can.cd()
    ROOT.gPad.SetLogy(1)
    ROOT.gPad.SetGridy(1)
    ROOT.gPad.SetGridx(1)

    Xmax = 5.
    Xmin = -95
    h2 = ROOT.TH2D("tmp", "tmp;days;       Cases", 100, Xmin, Xmax, 1000, kMinCasesToPlot, 5.e4)
    h2.SetStats(0)
    h2.SetTitle('')
    h2.GetYaxis().SetMoreLogLabels()
    h2.Draw()
    countries = []
    CountriesCols = { 'Hubei China'     : [ ROOT.kRed,       20],
                      'Hong Kong' : [ ROOT.kGreen+3,       24],
                      'Italy'         : [ ROOT.kBlack,     21],
                      'Germany'       : [ ROOT.kBlue,      22],
                      'France'        : [ ROOT.kGreen+2,   23],
                      'Spain'         : [ ROOT.kViolet,    20],
                      #'Belgium'       : [ ROOT.kViolet+2,  33],
                      #'Sweden'        : [ ROOT.kViolet+4,   34],
                      'Czechia'       : [ ROOT.kOrange+10, 33],
                      'Austria'       : [ ROOT.kTeal+3,      20],
                      #'Hungary'       : [ ROOT.kPink,      22],
                      #'Slovakia'      : [ ROOT.kAzure+4,   23],
                      'Singapore'      : [ ROOT.kMagenta+3,   23],
                      'Japan'         : [ ROOT.kMagenta,   20],
                      'Korea South'   : [ ROOT.kSpring,    21],
                      'UK'       : [ ROOT.kBlue+2,    22],
                      'Iran'                    : [ ROOT.kBlue-2,    23],
                      'Thailand'                : [ ROOT.kRed+2,     29],
                      'Canada, BC' : [ ROOT.kYellow+2 , 33], # 'Washington US'
    }
    CountriesToPlot = []
    for country in CountriesCols:
        CountriesToPlot.append(country)
    leg = ROOT.TLegend(0.115, 0.12, 0.34, 0.88)
    leg.SetBorderSize(0)
    
    for gname in graphs:
        countries.append(gname)
    print(countries)
    
    msts = range(20, 50)
    lsts = range(1, 30)
    opt = 'P'
    ig = -1
    fits = {}
    fits2 = {}
    fits_history = {}
    xmax = Xmax
    xmin = - kLastDaysToFit + 0.5
    # fits exp. params
    fitsa = {}
    fitsashort = {}
    for country in graphs:
        if country not in CountriesToPlot:
            continue
        graph = graphs[country]
        ig = ig + 1
        graph.SetMarkerColor(CountriesCols[country][0])
        graph.SetLineColor(CountriesCols[country][0])
        graph.SetMarkerStyle(CountriesCols[country][1])
        graph.SetMarkerSize(1)
        fit = ROOT.TF1('fit_{}'.format(country), '[0]*exp([1]*(x-[2]))', xmin, xmax)
        fit.SetLineColor(graph.GetMarkerColor())
        fit.SetLineStyle(1)
        fit.SetParameters(1., 0.3, xmin)
        fits[country] = fit
        graph.Fit(fit, "", "", xmin, xmax)
        fitsa[country] = fit.GetParameter(1)

        drawHistoricFit = False
        if country == 'Korea South' or country == 'Iran' or country == 'Italy':
            drawHistoricFit = True
            # historic fit
            # off = 11.
            xx1 = -graphs['Hubei China'].GetN() + kHistoryDay0
            xx2 = xx1 + kLastDaysToFit - 0.5
            print('*** OK, Running an historic fit for {} between days {} and {} ***'.format(country, xx1, xx2))
            fit_hist = ROOT.TF1('fit_hist_{}'.format(country), '[0]*exp([1]*(x-[2]))', xx1, xx2) # xmin - off, xmax - off)
            fit_hist.SetLineColor(graph.GetMarkerColor())
            fit_hist.SetLineStyle(1)
            xx = ROOT.Double()
            yy = ROOT.Double()
            iday =  - (graphs['Hubei China'].GetN() - graphs[country].GetN() ) + kHistoryDay0
            graphs[country].GetPoint(iday, xx, yy)
            aguess = 0.3
            print('Setting parameters from point {} to {} {} {}'.format(iday, yy, aguess, xx))
            fit_hist.SetParameters(yy, aguess, xx)
            fits_history[country] = fit_hist
            graph.Fit(fit_hist, "", "", xx1, xx2) #xmin - off, xmax - off)
            chi2,ndf = GetChi2Ndf(fit_hist)
            chi2str = GetChi2Str(chi2,ndf)
            print(chi2str)
        # last days fit
        xx1 = -kLastDaysToFitShort  + 0.5
        xx2 = xmax
        fit2 = ROOT.TF1('fit2_{}'.format(country), '[0]*exp([1]*(x-[2]))', xx1, xx2) # xmin - off, xmax - off)
        fit2.SetLineColor(graph.GetMarkerColor())
        fit2.SetLineStyle(1)
        fit2.SetLineStyle(2)
        fit2.SetParameters(1., 0.3, xx1)
        fits2[country] = fit2
        graph.Fit(fit2, "", "", xx1, xx2) #xmin - off, xmax - off)
        fitsashort[country] = fit2.GetParameter(1)
        leg.AddEntry(graph, country + ' a_{' + '{:}'.format(kLastDaysToFit) + '}=' + '{:1.2f}'.format(fitsa[country]) + ' a_{' + '{}'.format(kLastDaysToFitShort) + '}' + '={:1.2f}'.format(fitsashort[country]), 'PL')
        graph.Draw(opt)
        fit.Draw('same')
        fit2.Draw('same')
        if drawHistoricFit:
            fits_history[country].Draw('same')
    leg.Draw()
    stuff.append([graphs, fits])
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

