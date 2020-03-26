#!/usr/bin/python

from __future__ import print_function
import ROOT, os, sys
# jk 12.2.2020

from math import sqrt, pow
from Tools import *
from Data import *

cans = []
stuff = []
print(Data)

kLastDaysToFit = 5

gr_cases = []
gr_deaths = []


CountriesCols = { 'China'   : [ ROOT.kRed,       24],
                  'non-China'   : [ ROOT.kBlack,       24],
                  'Global'   : [ ROOT.kRed,       20],
                  'Hong Kong'     : [ ROOT.kGreen+3,       24],
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
                  'USA'           :  [ ROOT.kAzure+4,   23],
                  'Singapore'      : [ ROOT.kMagenta+3,   23],
                  'Japan'         : [ ROOT.kMagenta,   24],
                  'Korea South'   : [ ROOT.kSpring+2,    25],
                  'UK'            : [ ROOT.kBlue+2,    22],
                  'Iran'          : [ ROOT.kBlue-2,    23],
                  'Thailand'      : [ ROOT.kRed+2,     29],
                  'Switzerland' : [ ROOT.kYellow+2 , 33], # 'Washington US'
                  #'Canada, BC' : [ ROOT.kYellow+2 , 33], # 'Washington US'
}

lsts = range(1, 30)
tags = ['Global', 'China', 'non-China', 'Korea South', 'Japan', 'Italy', 'Germany', 'Czechia', 'Austria', 'France', 'Spain', 'UK', 'Iran', 'USA' ]
#toFitIndices = range(3,10)
##toFitIndices = [5, 6, 7,]
#toFitIndices = [7,]
toFitIndices = range(3,len(tags)-1)
# not to add to the non-China sum twice:
skipIndices = range(3,13)
# for prediction:
evalPoints = range(55, 69)

ndata = len(tags)
for i in range(0,ndata):
    gr_case = ROOT.TGraphErrors()
    col = CountriesCols[tags[i]][0]
    mst = CountriesCols[tags[i]][1]
    gr_case.SetMarkerColor(col)
    gr_case.SetLineColor(col)
    gr_case.SetMarkerStyle(mst)
    gr_case.SetMarkerSize(1)
    gr_cases.append(gr_case)
    gr_death = ROOT.TGraphErrors()
    gr_death.SetMarkerColor(col)
    gr_death.SetLineColor(col)
    gr_death.SetMarkerStyle(mst)
    gr_death.SetMarkerSize(1)
    gr_deaths.append(gr_death)

ipcs = [0 for x in range(0, 100) ]
ipds = [0 for x in range(0, 100) ]

for data in Data:
    date = data[0]
    cases, deaths = data[1],data[2]
    ncases = 0.
    print(cases,deaths)
    try:
        if len(cases) >  1:
            for i in range(1, len(cases)+1):
                if i not in skipIndices:
                    ncases = ncases + cases[i-1]
                if cases[i-1] > 0:
                    gr_cases[i].SetPoint(ipcs[i], ipcs[0]+1, cases[i-1])
                    gr_cases[i].SetPointError(ipcs[i], 0, sqrt(cases[i-1]) )
                    ipcs[i] = ipcs[i] + 1
    except:
        ncases = cases
    gr_cases[0].SetPoint(ipcs[0], ipcs[0]+1, ncases)
    gr_cases[0].SetPointError(ipcs[0], 0, sqrt(ncases) )
    ipcs[0] = ipcs[0] + 1

    ndeaths = 0.
    try:
        if len(deaths) > 1:
            for i in range(1, len(deaths)+1):
                ndeaths = ndeaths + deaths[i-1]
                gr_deaths[i].SetPoint(ipds[i], ipds[0]+1, deaths[i-1])
                gr_deaths[i].SetPointError(ipds[i], 0, sqrt(deaths[i-1]) )
                ipds[i] = ipds[i] + 1
    except:
        ndeaths = deaths
    gr_deaths[0].SetPoint(ipds[0], ipds[0]+1, ndeaths)
    gr_deaths[0].SetPointError(ipds[0], 0, sqrt(ndeaths) )
    ipds[0] = ipds[0]+1

canname = 'CanCases'
can_cases = ROOT.TCanvas(canname, canname, 0, 0, 1189,844)
cans.append(can_cases)
can_cases.cd()
ROOT.gPad.SetGridx()
ROOT.gPad.SetGridy()

canname = 'CanDeaths'
can_deaths = ROOT.TCanvas(canname, canname)
cans.append(can_deaths)
can_deaths.cd()
ROOT.gPad.SetGridx()
ROOT.gPad.SetGridy()


opt = 'AP'

sdate = Data[-1][0]
leg = ROOT.TLegend(0.12, 0.52, 0.34, 0.88)
leg.SetHeader(sdate)
for gr_case,gr_death,tag in zip(gr_cases, gr_deaths,tags):
    can_cases.cd()
    gr_case.SetName('cases_{}'.format(tag))
    gr_case.Draw(opt)
    can_deaths.cd()
    gr_death.Draw(opt)
    opt = 'P'
    leg.AddEntry(gr_case, '{} cases'.format(tag), 'P')
    #leg.AddEntry(gr_death, '{} deaths'.format(tag), 'P')
    gr_case.GetXaxis().SetTitle('WHO report number (~daily)')
    gr_case.GetYaxis().SetTitle('Counts')
    gr_case.GetYaxis().SetRangeUser(1., gr_case.GetYaxis().GetXmax()*1.5)

can_cases.cd()
leg.Draw()
can_deaths.cd()
leg.Draw()
stuff.append(leg)

can_cases.Print('CoronavirusCases_liny.png')
ROOT.gPad.SetLogy()
gr_cases[0].GetYaxis().SetMoreLogLabels()
gr_cases[0].GetYaxis().SetRangeUser(1., gr_cases[0].GetYaxis().GetXmax()*10000.)

can_deaths.Print('CoronavirusDeaths_liny.png')
ROOT.gPad.SetLogy()
gr_deaths[0].GetYaxis().SetMoreLogLabels()
gr_deaths[0].GetYaxis().SetRangeUser(1., gr_deaths[0].GetYaxis().GetXmax()*10000.)

dgr_cases = []
dgr_deaths = []
fit_cases = []
fit_cases2 = []

ig = -1


canCountries = ROOT.TCanvas('CanCountries', 'CanCountries', 200, 200, 1000, 800)
cans.append(canCountries)
canCountries.cd()
ROOT.gPad.SetGridx()
ROOT.gPad.SetGridy()

for gr_case, gr_death, tag, lst in zip(gr_cases, gr_deaths, tags, lsts):
    ig = ig+1
    print(ig)
    
    dgr_case = MakeDerivative(gr_case)
    can_cases.cd()
    dgr_case.SetLineColor(gr_case.GetLineColor())
    dgr_case.SetLineWidth(2)
    dgr_case.SetLineStyle(lst)

    dgr_death = MakeDerivative(gr_death)
    dgr_death.SetLineColor(gr_death.GetLineColor())
    dgr_death.SetLineWidth(2)
    dgr_death.SetLineStyle(lst)
    dgr_cases.append(dgr_case)
    dgr_deaths.append(dgr_death)

    #leg.AddEntry(gr_case, 'Derivative of {} cases'.format(tag), 'L')
    #leg.AddEntry(gr_death, 'Derivative of {} deaths'.format(tag), 'L')
    can_deaths.cd()
    dgr_case.Draw('C')
    dgr_death.Draw('C')

    if ig in toFitIndices:
        xx = ROOT.Double()
        yy = ROOT.Double()
        gr_case.GetPoint(gr_case.GetN()-1, xx, yy)
        x2 = xx + kLastDaysToFit + 0.5
        x1 = xx - kLastDaysToFit + 0.5
        fitname = gr_case.GetName() + '_fit'
        fit_case = ROOT.TF1(fitname, '[0]*exp([1]*x)', x1, x2)
        fit_case.SetLineColor(gr_case.GetMarkerColor())
        fit_case.SetLineStyle(2)
        fit_case.SetParameters(1., 0.3)
        fit_cases.append(fit_case)
        gr_case.GetYaxis().SetMoreLogLabels()
        gr_case.Fit(fitname, '', '', x1, x2)
        for ep in evalPoints:
            print('Est. cases  in day {}: {:4.0f}'.format(ep, fit_case.Eval(1.*ep)))
        # firt data fit:
        fitname = gr_case.GetName() + '_fit2'
        xx = ROOT.Double()
        yy = ROOT.Double()
        gr_case.GetPoint(0, xx, yy)
        if 'Korea' in fitname or 'Iran' in fitname:
            x1 = xx + 6
        else:
            xx += 10
        fit_case2 = ROOT.TF1(fitname, '[0]*exp([1]*x)', xx, x1)
        fit_case2.SetLineColor(gr_case.GetMarkerColor())
        fit_case2.SetLineStyle(2)
        fit_case2.SetParameters(1., 0.3)
        fit_cases2.append(fit_case2)
        gr_case.Fit(fitname, '', '', xx, x1)
        

            
canCountries.cd()
ig = 0
ifit = 0
h2 = ROOT.TH2D("tmp", "tmp;WHO report number;Cases", 100, 30, 65, 5000, 1., 1.e7)
###h2 = ROOT.TH2D("tmp", "tmp;WHO report number;Cases", 1000, 0, 55, 500, 1., 5.e2)
h2.SetStats(0)
h2.SetTitle('')
h2.Draw()
opt = 'P'
icol = -1
legFit = ROOT.TLegend(0.12, 0.60, 0.55, 0.88)
legFit.SetHeader(sdate)
legFit.SetBorderSize(0)
for tag,gr_case in zip(tags,gr_cases):
    icol = icol+1
    if ig in toFitIndices:
        gr_case.SetMarkerColor(CountriesCols[tag][0])
        gr_case.Draw(opt)
        opt = 'P'
        fit_case = fit_cases[ifit]
        fit_case2 = fit_cases2[ifit]
        fit_case.SetLineColor(gr_case.GetMarkerColor())
        fit_case.Draw('same')
        fit_case2.Draw('same')
        chi2 = fit_case.GetChisquare()
        ndf = fit_case.GetNDF()
        chi2early = fit_case2.GetChisquare()
        ndfearly = fit_case2.GetNDF()
        #text = ROOT.TLatex(0.15, 0.84 - ifit*0.065, '{:8}'.format(tag) + ' #chi^{2}/ndf' + '={:1.1f}'.format(chi2/ndf) + + ' a_{' + '{:}'.formart(kLastDaysToFit)  + '}={:1.2f}'.format(fit_case.GetParameter(1)) )
        #text.SetTextSize(0.04)
        #text.SetTextColor(gr_case.GetMarkerColor())
        #text.SetNDC()
        #text.Draw()
        #stuff.append(text)
        legtext = '{:20}'.format(tag)
        #legtext += ' #chi^{2}/ndf' + '={:1.1f}'.format(chi2early/ndfearly) + ' a_{0}' + '={:1.2f}'.format(fit_case2.GetParameter(1))
        #legtext += ' #chi^{2}/ndf' + '={:1.1f}'.format(chi2/ndf) + ' a_{' + '{:}'.format(kLastDaysToFit)  + '}' + '={:1.2f}'.format(fit_case.GetParameter(1))
        legtext += ' a_{0}' + '={:1.2f}'.format(fit_case2.GetParameter(1))
        legtext += ' a_{' + '{:}'.format(kLastDaysToFit)  + '}' + '={:1.2f}'.format(fit_case.GetParameter(1))
        legFit.AddEntry(gr_case, legtext, 'PL' )
        stuff.append([fit_case, gr_case])
        ifit = ifit+1
    ig = ig+1
legFit.Draw()
stuff.append(legFit)
canname = 'CanGrowth'
canGrowth = ROOT.TCanvas(canname, canname, 500,500,500,500)
cans.append(canGrowth)
canGrowth.cd()
ROOT.gPad.SetGridx()
ROOT.gPad.SetGridy()
opt = 'ACX'
growthFact_cases = []
canGrowth.cd()
for gr_case,dgr_case in zip(gr_cases,dgr_cases):
    growthFact_case = MakeSeqRatio(dgr_case)
    CopyStyle(gr_case, growthFact_case)
    growthFact_case.SetMarkerSize(0)
    growthFact_case.SetLineWidth(1)
    growthFact_case.Draw(opt)
    growthFact_cases.append(growthFact_case)
    opt = 'C'
canGrowth.Print(canGrowth.GetName() + '.png')
####################################
can_cases.cd()
ROOT.gPad.SetLogy()
ROOT.gPad.Update()
can_cases.Print('CoronavirusCases_logy.png')

####################################
can_deaths.cd()
ROOT.gPad.SetLogy()
ROOT.gPad.Update()
can_deaths.Print('CoronavirusDeaths_logy.png')

####################################

canGrowth.cd()
ROOT.gPad.Update()
canGrowth.Print('Coronavirus_growth_liny.png')

####################################
canCountries.cd()
ROOT.gPad.Update()
h2.GetYaxis().SetRangeUser(0., 8e4)
canCountries.Print('CoronavirusCases_Countries_liny.png')
ROOT.gPad.SetLogy()
h2.GetYaxis().UnZoom()
canCountries.Print('CoronavirusCases_Countries_logy.png')

####################################

canname = 'CZ_SickOverTested'
canRatio = ROOT.TCanvas(canname, canname, 0, 300, 1200, 600)
cans.append(canRatio)
canRatio.Divide(2,1)
gr_ratio_cummulative = ROOT.TGraphErrors()
gr_ratio_daily = ROOT.TGraphErrors()
gr_cz_cases = ROOT.TGraphErrors()
gr_cz_tests = ROOT.TGraphErrors()
# find matching date index
id = -1
tdate = cz_tests[0][0]
idate = ''
while idate != tdate:
    id = id + 1
    idate = Data[id][0]
ip = 0
icz = 6 # fixed!
oldntest = -1.
for tests in cz_tests:
    tdate = tests[0]
    idate = Data[id][0]
    if tdate != idate:
        print('Hm, this should not happen... {} != {}'.format(tdate, idate))
        continue
    #print(Data[id][1])
    ntests = tests[1]
    cases = Data[id][1][icz]
    ratio = 1.*cases / (1.*ntests)
    # daily numbers:
    dcases = cases
    ndtests = ntests
    if ip > 0:
        dcases = dcases - Data[id-1][1][icz]
        ndtests = ndtests - oldntests
    oldntests = 1.*ntests
    dratio = dcases/ndtests
    gr_cz_cases.SetPoint(ip, ip+1, cases)
    gr_cz_cases.SetPointError(ip, 0, sqrt(cases))
    gr_cz_tests.SetPoint(ip, ip+1, ntests)
    gr_cz_tests.SetPointError(ip, 0, sqrt(ntests))
        
    gr_ratio_cummulative.SetPoint(ip, ip+1, ratio) 
    gr_ratio_cummulative.SetPointError(ip, 0, sqrt(cases)/ntests)
    gr_ratio_daily.SetPoint(ip, ip+1, dratio) 
    gr_ratio_daily.SetPointError(ip, 0, sqrt(dcases)/ndtests)
    ip = ip + 1
    id = id + 1
gr_ratio_cummulative.SetLineColor(ROOT.kRed)
gr_ratio_cummulative.SetMarkerColor(ROOT.kRed)
gr_ratio_cummulative.SetMarkerStyle(20)

gr_ratio_daily.SetLineColor(ROOT.kBlack)
gr_ratio_daily.SetMarkerColor(ROOT.kBlack)
gr_ratio_daily.SetMarkerStyle(20)

canRatio.cd(1)
x2 = len(cz_tests) + 5
x1 = x2-15
hh2 = ROOT.TH2D("tmp2", ";Days since 1.3.2020;#", 100, 0, x2, 5000, 1., 500000)
hh2.SetStats(0)
hh2.Draw()
gr_cz_tests.SetLineColor(ROOT.kBlue)
gr_cz_tests.SetMarkerColor(ROOT.kBlue)
gr_cz_tests.SetMarkerStyle(21)
gr_cz_tests.Draw('P')
ff1 = ROOT.TF1('ff1', '[0]*exp([1]*x)', x1, x2)
ff1.SetLineColor(ROOT.kBlue)
ff1.SetParameters(1., 0.2)
gr_cz_tests.Fit(ff1, '', '', x1, x2)
gr_cz_cases.SetLineColor(ROOT.kRed)
gr_cz_cases.SetMarkerColor(ROOT.kRed)
gr_cz_cases.SetMarkerStyle(20)
gr_cz_cases.Draw('P')
ff2 = ROOT.TF1('ff2', '[0]*exp([1]*x)', x1, x2)
ff2.SetLineColor(ROOT.kRed)
ff2.SetParameters(1., 0.2)
gr_cz_cases.Fit(ff2, '', '', x1, x2)
ROOT.gPad.SetLogy(1)

tleg = ROOT.TLegend(0.45, 0.15, 0.84, 0.30)
tleg.AddEntry(gr_cz_tests, 'Cummulative tests a={:1.2f}'.format(ff1.GetParameter(1)), 'PL')
tleg.AddEntry(gr_cz_cases, 'Cummulative cases a={:1.2f}'.format(ff2.GetParameter(1)), 'PL')
tleg.SetBorderSize(0)
tleg.Draw()
ROOT.gPad.SetGridy(1)
ROOT.gPad.SetGridx(1)
ROOT.gPad.Update()

canRatio.cd(2)

hhh2 = ROOT.TH2D("tmp3", ";Days since 1.3.2020;CZ Positive/Tested", 100, 0, x2, 100, 0., 0.35)
hhh2.SetStats(0)
hhh2.Draw()

gr_ratio_cummulative.Draw('P')
gr_ratio_cummulative.GetYaxis().SetTitle('CZ Positive/Tested')
gr_ratio_cummulative.GetXaxis().SetTitle('Days since 1.3.2020')
gr_ratio_cummulative.Fit('pol1')

gr_ratio_daily.Draw('P')

rleg = ROOT.TLegend(0.12, 0.70, 0.55, 0.85)
rleg.AddEntry(gr_ratio_cummulative, 'Cummulative cases/tests', 'PL')
rleg.AddEntry(gr_ratio_daily, 'Daily cases/tests', 'PL')
rleg.SetBorderSize(0)
rleg.Draw()
ROOT.gPad.Update()
canRatio.Print(canRatio.GetName() + '.png')

stuff.append([can_cases, can_deaths, canCountries, gr_deaths, gr_cases, leg, legFit, canRatio, gr_ratio_cummulative, gr_ratio_daily, rleg])


name='CoronavirusCases_Countries_liny'
cmd='myput.py slo public_html/virus/covid-19 "{}.png"'.format(name)
os.system(cmd)
name='CoronavirusCases_Countries_logy'
cmd='myput.py slo public_html/virus/covid-19 "{}.png"'.format(name)
os.system(cmd)
name='CZ_SickOverTested'
cmd='myput.py slo public_html/virus/covid-19 "{}.png"'.format(name)
os.system(cmd)


ROOT.gApplication.Run()
