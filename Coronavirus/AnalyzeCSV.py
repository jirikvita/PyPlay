#!/usr/bin/python
# Thu 12 Mar 12:20:43 CET 2020
# using data from https://github.com/CSSEGISandData/COVID-19


# TODO: clicable page with linear scale date from each country!

from __future__ import print_function

import ROOT
from math import sqrt, pow, log, exp
import os, sys, getopt

from Tools import CopyStyle, MakeDiffGr


cans = []
stuff = []

kMinCasesToPlot = 0
kLastDaysToFit = 7
kLastDaysToFitShort = 4
kHistoryDay0 = 30
kShiftAxisToSameMinCases = False

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
def MakeGraphs(fname, addtag = ''):
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
        #if items[0] == '':
        #    items = items[1:]
        if items[1] == '"Korea':
            items[2] = (items[1] + items[2]).replace('"','')
            items.pop(1)
        #items.pop(0)
        vals = items[4:]
        province,state = items[0], items[1]

        # skip provinces for the moment
        if province not in kAcceptProvinces:
            continue
        print('ITEMS: ', items)
        gname = '{}{}'.format(province,state)
        if province != '':
            gname = '{} {}'.format(province,state)
        if gname == 'France France':
            gname = 'France'
        if gname == 'Hong Kong China':
            gname = 'Hong Kong'
        if gname == 'British Columbia Canada':
            gname = 'Canada, BC'
        if gname == 'United Kingdom':
            gname = 'UK'
        print('Names+Tag: {} {}'.format(gname,addtag))
        graph.SetName(gname + addtag)
        ip = 0
        id = -len(dates)
        for date,sval in zip(dates,vals):
            if sval == '':
                continue
            if sval[-1] == '\r':
                sval = sval[:-1]
            val = int(sval)
            if val > kMinCasesToPlot:
                err = 0.
                if err > 0:
                    sqrt(val)
                if kShiftAxisToSameMinCases:
                    graph.SetPoint(ip, ip, val)
                    graph.SetPointError(ip, 0, err)
                else:
                    graph.SetPoint(ip, id+1, val)
                    graph.SetPointError(ip, 0, err)
                ip = ip + 1
            id = id + 1
        graphs[gname] = graph
    return graphs,dates

##########################################
def MakeActualCasesGraphs(CountriesToPlot, cgraphs, dgraphs, rgraphs):
    # sgraphs: a list of graphs to be subtracted
    agraphs = {}
    for country in cgraphs:
        if country not in CountriesToPlot:
            continue
        cgraph = cgraphs[country] # cases
        dgraph = dgraphs[country] # deaths

        tmpgraph = MakeDiffGr(cgraph, dgraph)

        tgraph = ROOT.TGraph()
        agraph = ROOT.TGraph()
        try:
            rgraph = rgraphs[country] # recovered
            agraph = MakeDiffGr(tmpgraph, rgraph)
        except:
            rgraphs[country] = ROOT.TGraph()
            agraphs[country] = ROOT.TGraph()
        agraph.SetName(cgraph.GetName() + '_actual')
        agraphs[country] = agraph
    return agraphs

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
    can = ROOT.TCanvas(canname, canname, 0, 0, 1390,844)
    cans.append(can)

    canname = 'ConfirmedCasesLiny'
    canlin = ROOT.TCanvas(canname, canname, 0, 0, 1400, 800)
    cans.append(canlin)
    canname = 'ConfirmedCasesLiny2'
    canlin2 = ROOT.TCanvas(canname, canname, 0, 0, 1400, 800)
    cans.append(canlin2)

    # cases:
    filename = 'time_series_covid19_confirmed_global.csv' # OLD: 'time_series_19-covid-Confirmed.csv'
    graphs,dates = MakeGraphs(filename,'cases')

    # deaths:
    dfilename = 'time_series_covid19_deaths_global.csv'
    dgraphs,ddates = MakeGraphs(dfilename,'deaths')

    # recovered:
    rfilename = 'time_series_covid19_recovered_global.csv'
    rgraphs,rdates = MakeGraphs(rfilename,'recovered')

    sdate = dates[-1].split('/')
    dd = sdate[1]
    mm = sdate[0]
    yy = sdate[2]
    yy = '20' + yy
    print(yy,mm,dd)
    if int(dd) < 10:
        dd = '0' + dd
    if int(mm) < 10:
        mm = '0' + mm
    tag = '{}{}{}'.format(yy,mm,dd)
    ltag = 'Johns Hopkins data as of {}.{}.{}'.format(dd,mm,yy)
    ltagshort = '{}.{}.{}'.format(dd,mm,yy)

    nx = 6
    ny = 3
    #drawSingle = 'Czech'
    drawSingle = ''
    if drawSingle == '':
        canlin.Divide(nx,ny)
        canlin2.Divide(nx,ny)
        for cnl in canlin,canlin2:
            for i in range(nx*ny):
                cnl.cd(i+1)
                ROOT.gPad.SetGridy(1)
                ROOT.gPad.SetGridx(1)

    can.cd()
    ROOT.gPad.SetLogy(1)
    ROOT.gPad.SetGridy(1)
    ROOT.gPad.SetGridx(1)

    Xmax = 5.
    Xmin = -len(dates)
    if kShiftAxisToSameMinCases:
        Xmin = 0
        Xmax = len(dates)
    h2 = ROOT.TH2D("tmp", "tmp;days; Cummulative Cases", 1000, Xmin, Xmax, 1000, kMinCasesToPlot/2. + 10., 5.e7)
    h2.SetStats(0)
    h2.SetTitle('')
    h2.GetYaxis().SetMoreLogLabels()
    h2.Draw()
    countries = []
    CountriesCols = { 'Hubei China'   : [ ROOT.kRed,       20],
                      'Hong Kong'     : [ ROOT.kGreen+3,       24],
                      'Italy'         : [ ROOT.kBlack,     21],
                      'Germany'       : [ ROOT.kBlue,      22],
                      'France'        : [ ROOT.kGreen+2,   23],
                      'Spain'         : [ ROOT.kViolet,    20],
                      'Belgium'       : [ ROOT.kViolet+2,  33],
                      'Australia'     : [ ROOT.kViolet+4,   34],
                      'Czechia'       : [ ROOT.kOrange+10, 33],
                      'Austria'       : [ ROOT.kTeal+3,      20],
                      'Hungary'       : [ ROOT.kPink,      22],
                      'Sweden'       : [ ROOT.kPink,      22],
                      'Slovakia'      : [ ROOT.kAzure+4,   23],
                      'Singapore'      : [ ROOT.kMagenta+3,   23],
                      'Japan'         : [ ROOT.kMagenta,   20],
                      'Korea South'   : [ ROOT.kSpring,    21],
                      'UK'            : [ ROOT.kBlue+2,    22],
                      'Iran'          : [ ROOT.kBlue-2,    23],
                      ###'Thailand'      : [ ROOT.kRed+2,     29],
                      'Taiwan*'      : [ ROOT.kPink+2,     24],
                      'Switzerland' : [ ROOT.kYellow+2 , 33], 
                      #'Canada, BC' : [ ROOT.kYellow+2 , 33],
                      'US' : [ ROOT.kRed+2 , 20],
                      'Brazil' : [ ROOT.kBlue+1 , 23],
                      'Russia' : [ ROOT.kRed , 22],
                      'Israel' : [ ROOT.kBlue-1 , 21],
                      'Portugal' : [ ROOT.kGreen , 25],
                      'Poland' : [ ROOT.kRed+4 , 24],
                      'Denmark' : [ ROOT.kGray+2 , 25],
                      'Netherlands' : [ ROOT.kTeal , 26],
                       'Philippines' : [ ROOT.kMagenta+2 , 24],
                      'Malaysia' : [ ROOT.kSpring+2 , 23],
                      'New Zeland' : [ ROOT.kSpring+1 , 23],
                      'Turkey' : [ ROOT.kRed-2 , 23],
                      'India' : [ ROOT.kGreen+1 , 25],
                       #'Peru' : [ ROOT.kBlue , 27],
                      'Ecuador' : [ ROOT.kRed , 28],
                      'Mexico' : [ ROOT.kGray , 24],
                      'Chile' : [ ROOT.kMagenta-2 , 23],
                      #'South Africa' : [ ROOT.kRed+5 , 23],
                      'Algeria' : [ ROOT.kSpring , 28],
                      'Argentina' : [ ROOT.kAzure , 20],
                      
                      
    }
    CountriesToPlot = []
    for country in CountriesCols:
        if drawSingle == '' or (drawSingle != '' and drawSingle in country):
            CountriesToPlot.append(country)

    # actual cases
    agraphs = MakeActualCasesGraphs(CountriesToPlot, graphs, dgraphs, rgraphs)
    
    x1, y1, x2, y2 = 0.115, 0.12, 0.34, 0.88
    if kShiftAxisToSameMinCases:
        x1, y1, x2, y2 = 0.65, 0.12, 0.87, 0.88
    leg = ROOT.TLegend(x1, y1, x2, y2)
    leg.SetBorderSize(0)
    leg.SetHeader(ltag)
    
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
    # fits exp. params
    fitsa = {}
    fitsashort = {}
    ipad = 1
    for country in graphs:
        if country not in CountriesToPlot:
            continue
        graph = graphs[country]
        dgraph = dgraphs[country]
        agraph = agraphs[country]
        #rcountry = country + ''
        #if 'Canada' in country: rcountry = 'Canada'
        rgraph = rgraphs[country]
        ig = ig + 1
        can.cd()
        graph.SetMarkerColor(CountriesCols[country][0])
        graph.SetLineColor(CountriesCols[country][0])
        graph.SetMarkerStyle(CountriesCols[country][1])
        graph.SetMarkerSize(1)
        CopyStyle(graph,dgraph)
        dgraph.SetLineWidth(2)
        dgraph.SetLineStyle(3)
        CopyStyle(graph,rgraph)
        rgraph.SetLineWidth(2)
        rgraph.SetLineStyle(2)
        CopyStyle(graph,agraph)
        agraph.SetMarkerSize(0)
        agraph.SetLineWidth(3)
        agraph.SetLineStyle(1)
        
        xmax = Xmax
        xmin = - kLastDaysToFit + 0.5
        if kShiftAxisToSameMinCases:
            pass
            ###TODO!!!
            ###get really last point x-coordinate

        
        fit = ROOT.TF1('fit_{}'.format(country), '[0]*exp([1]*x)', xmin, xmax)
        fit.SetLineColor(graph.GetMarkerColor())
        fit.SetLineStyle(1)
        fit.SetParameters(1., 0.3)#, xmin)
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
            fit_hist = ROOT.TF1('fit_hist_{}'.format(country), '[0]*exp([1]*x)', xx1, xx2) # xmin - off, xmax - off)
            fit_hist.SetLineColor(graph.GetMarkerColor())
            fit_hist.SetLineStyle(1)
            xx = ROOT.Double()
            yy = ROOT.Double()
            iday =  - (graphs['Hubei China'].GetN() - graphs[country].GetN() ) + kHistoryDay0
            graphs[country].GetPoint(iday, xx, yy)
            aguess = 0.3
            print('Setting parameters from point {} to {} {} {}'.format(iday, yy, aguess, xx))
            fit_hist.SetParameters(yy, aguess)#, xx)
            fits_history[country] = fit_hist
            graph.Fit(fit_hist, "", "", xx1, xx2) #xmin - off, xmax - off)
            chi2,ndf = GetChi2Ndf(fit_hist)
            chi2str = GetChi2Str(chi2,ndf)
            print(chi2str)
        # last days fit
        xx1 = -kLastDaysToFitShort  + 0.5
        xx2 = xmax
        fit2 = ROOT.TF1('fit2_{}'.format(country), '[0]*exp([1]*x)', xx1, xx2) # xmin - off, xmax - off)
        fit2.SetLineColor(graph.GetMarkerColor())
        fit2.SetLineStyle(1)
        fit2.SetLineStyle(2)
        fit2.SetParameters(1., 0.3)#, xx1)
        fits2[country] = fit2
        graph.Fit(fit2, "", "", xx1, xx2) #xmin - off, xmax - off)
        fitsashort[country] = fit2.GetParameter(1)
        leg.AddEntry(graph, '{:15}'.format(country) + ' a_{' + '{:}'.format(kLastDaysToFit) + '}=' + '{:1.3f}'.format(fitsa[country]) + ' a_{' + '{}'.format(kLastDaysToFitShort) + '}' + '={:1.3f}'.format(fitsashort[country]), 'PL')
        graph.Draw(opt)
        fit.Draw('same')
        fit2.Draw('same')
        if drawHistoricFit:
            fits_history[country].Draw('same')
            
        if ipad <= nx*ny:
            canlin.cd(ipad)
        else:
            canlin2.cd(ipad % (nx*ny) + 1)

        graph.Draw('AP')
        dgraph.Draw('L')
        rgraph.Draw('L')
        agraph.Draw('C')
        
        graph.GetYaxis().SetRangeUser(0., graph.GetYaxis().GetXmax())
        ctxt = ROOT.TLatex(0.14, 0.835, '{}'.format(country))
        ctxt.SetNDC()
        ctxt.Draw()
        ctxt.SetTextSize(0.07)
        stuff.append(ctxt)
        ctxt2 = ROOT.TLatex(0.55, 0.835, '{}'.format(ltagshort))
        ctxt2.SetNDC()
        ctxt2.Draw()
        ctxt2.SetTextSize(0.07)

        ctxt3 = ROOT.TLatex(0.56, 0.77, 'a_{' + '{:}'.format(kLastDaysToFitShort) + '}' + '={:1.3f}'.format(fitsashort[country]))
        ctxt3.SetNDC()
        ctxt3.Draw()
        ctxt3.SetTextSize(0.07)
        if fitsashort[country] >= 0.01:
            ctxt3.SetTextColor(ROOT.kRed)
        stuff.append(ctxt3)
        
        
        linleg = ROOT.TLegend(0.12, 0.50, 0.45, 0.80)
        #linleg.SetHeader('Cummulative')
        linleg.AddEntry(graph, 'Cumm. cases', 'P')
        linleg.AddEntry(agraph, 'Actual cases', 'L')
        linleg.AddEntry(rgraph, 'Recovered', 'L')
        linleg.AddEntry(dgraph, 'Deaths', 'L')
        linleg.SetBorderSize(0)
        linleg.Draw()
        stuff.append(linleg)
        stuff.append(ctxt2)
        ipad += 1
    
    can.cd()
    leg.Draw()
    stuff.append([graphs, fits])
    stuff.append(leg)
    
    canlin.Update()
    canlin.Print(canlin.GetName() + '_{}.png'.format(tag))
    canlin2.Update()
    canlin2.Print(canlin2.GetName() + '_{}.png'.format(tag))
    
    ROOT.gPad.Update()
    can.Print(can.GetName() + '_{}.png'.format(tag))
    h2.GetXaxis().SetRangeUser(-40, h2.GetXaxis().GetXmax())
    ROOT.gPad.Update()
    can.Print(can.GetName() + '_{}_zoom.png'.format(tag))
    print('Copying to remote server...')
    cmd='myput.py slo public_html/virus/covid-19 "{}*_{}*.png"'.format(can.GetName(),tag)
    os.system(cmd)
    print('Creating remote links to latest plots...')
    cmd = "ssh -Y kvita@slo.upol.cz 'bash -ci ./vln.sh'"
    os.system(cmd)
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

