#!/usr/bin/python

from __future__ import print_function
import ROOT
# jk 12.2.2020

from math import sqrt, pow
from Tools import *
from Data import *

stuff = []
print(Data)

kLastDaysToFit = 5

gr_cases = []
gr_deaths = []


cols = [ROOT.kRed, ROOT.kBlack, ROOT.kBlue, ROOT.kGreen+2, ROOT.kViolet,
        ROOT.kOrange+10, ROOT.kTeal, ROOT.kPink, ROOT.kAzure+4, ROOT.kMagenta,
        ROOT.kSpring, ROOT.kBlue+2, ROOT.kGray+2]

mst = range(20, 50)
lsts = range(1, 30)
tags = ['Global', 'China', 'non-China', 'Korea', 'Japan', 'Italy', 'Germany', 'Czech', 'France', 'Spain', 'UK', 'Iran', 'USA' ]
toFitIndices = range(3,10)
#toFitIndices = [5, 6, 7,]
toFitIndices = [7,]
# not to add to the non-China sum twice:
skipIndices = range(3,13)
# for prediction:
evalPoints = range(55, 69)

ndata = len(tags)
for i in range(0,ndata):
    gr_case = ROOT.TGraphErrors()
    gr_case.SetMarkerColor(cols[i])
    gr_case.SetLineColor(cols[i])
    gr_case.SetMarkerStyle(mst[i])
    gr_case.SetMarkerSize(1)
    gr_cases.append(gr_case)
    gr_death = ROOT.TGraphErrors()
    gr_death.SetMarkerColor(cols[i])
    gr_death.SetLineColor(cols[i])
    gr_death.SetMarkerStyle(mst[i])
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
can_cases.cd()
ROOT.gPad.SetGridx()
ROOT.gPad.SetGridy()

canname = 'CanDeaths'
can_deaths = ROOT.TCanvas(canname, canname)
can_deaths.cd()
ROOT.gPad.SetGridx()
ROOT.gPad.SetGridy()


opt = 'AP'

sdate = Data[-1][0]
leg = ROOT.TLegend(0.12, 0.52, 0.34, 0.88)
leg.SetHeader(sdate)
for gr_case,gr_death,tag in zip(gr_cases, gr_deaths,tags):
    can_cases.cd()
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

ig = -1


canCountries = ROOT.TCanvas('can', 'can', 200, 200, 1000, 800)
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
    dgr_case.Draw('L')
    dgr_death.Draw('L')

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
            
canCountries.cd()
ig = 0
ifit = 0
h2 = ROOT.TH2D("tmp", "tmp;WHO report number;Cases", 100, -10, 65, 5000, 1., 5.e5)
###h2 = ROOT.TH2D("tmp", "tmp;WHO report number;Cases", 1000, 0, 55, 500, 1., 5.e2)
h2.SetStats(0)
h2.SetTitle('')
h2.Draw()
opt = 'P'
icol = -1
legFit = ROOT.TLegend(0.12, 0.46, 0.40, 0.85)
legFit.SetHeader(sdate)
legFit.SetBorderSize(0)
for tag,gr_case in zip(tags,gr_cases):
    icol = icol+1
    if ig in toFitIndices:
        gr_case.SetMarkerColor(cols[icol])
        gr_case.Draw(opt)
        opt = 'P'
        fit_case = fit_cases[ifit]
        fit_case.SetLineColor(gr_case.GetMarkerColor())
        fit_case.Draw('same')
        chi2 = fit_case.GetChisquare()
        ndf = fit_case.GetNDF()
        #text = ROOT.TLatex(0.15, 0.84 - ifit*0.065, '{:8}'.format(tag) + ' #chi^{2}/ndf' + '={:1.1f}'.format(chi2/ndf) + + ' a_{' + '{:}'.formart(kLastDaysToFit)  + '}={:1.2f}'.format(fit_case.GetParameter(1)) )
        #text.SetTextSize(0.04)
        #text.SetTextColor(gr_case.GetMarkerColor())
        #text.SetNDC()
        #text.Draw()
        #stuff.append(text)
        legFit.AddEntry(gr_case, '{:8}'.format(tag) + ' #chi^{2}/ndf' + '={:1.1f}'.format(chi2/ndf) + ' a_{' + '{:}'.format(kLastDaysToFit)  + '}' + '={:1.2f}'.format(fit_case.GetParameter(1)), 'PL' )
        stuff.append([fit_case, gr_case])
        ifit = ifit+1
    ig = ig+1
legFit.Draw()
stuff.append(legFit)
canname = 'CAnGrowth'
canGrowth = ROOT.TCanvas(canname, canname, 500,500,500,500)
canGrowth.cd()
ROOT.gPad.SetGridx()
ROOT.gPad.SetGridy()
opt = 'APL'
growthFact_cases = []
canGrowth.cd()
for gr_case,dgr_case in zip(gr_cases,dgr_cases):
    growthFact_case = MakeSeqRatio(dgr_case)
    CopyStyle(gr_case, growthFact_case)
    growthFact_case.Draw(opt)
    growthFact_cases.append(growthFact_case)
    opt = 'PL'

can_cases.cd()
ROOT.gPad.SetLogy()
ROOT.gPad.Update()
can_cases.Print('CoronavirusCases_logy.png')

can_deaths.cd()
ROOT.gPad.SetLogy()
ROOT.gPad.Update()
can_deaths.Print('CoronavirusDeaths_logy.png')


canGrowth.cd()
ROOT.gPad.Update()
canGrowth.Print('Coronavirus_growth_liny.png')

canCountries.cd()
ROOT.gPad.Update()
canCountries.Print('CoronavirusCases_Countries_liny.png')
ROOT.gPad.SetLogy()
canCountries.Print('CoronavirusCases_Countries_logy.png')

stuff.append([can_cases, can_deaths, canCountries, gr_deaths, gr_cases, leg, legFit])

ROOT.gApplication.Run()
