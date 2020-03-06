#!/usr/bin/python

from __future__ import print_function
import ROOT
# jk 12.2.2020

from math import sqrt, pow

from Tools import *

stuff = []

# data from https://www.who.int/emergencies/diseases/novel-coronavirus-2019/situation-reports/
# date, total cases, deaths total
# global data
# cases here are laboratory testes, not clinically
Data = [ ['20.1.2020', 282, 6],
         ['21.1.2020', 314, 6],
         ['23.1.2020', 581, 17],
         ['24.1.2020', 846, 25],
         ['25.1.2020', 1320, 41],
         ['26.1.2020', 2014, 56],
         ['27.1.2020', 2798, 80],
         ['28.1.2020', 4593, 106],
         ['29.1.2020', 6065, 132],
         ['30.1.2020', 7818, 170],
         ['31.1.2020', 9826, 213],
         [ '1.2.2020', 11953, 259],
         [ '2.2.2020', 14557, 305],
         [ '3.2.2020', 17391, 362],
         [ '4.2.2020', 20630, 426],
         [ '5.2.2020', 24554, 494],
         [ '6.2.2020', 28276, 565],
         [ '7.2.2020', 31481, 638],
         [ '8.2.2020', 34886, 724],
         [ '9.2.2020', 37558, 813], 
         ['10.2.2020', 40554, 910],
         ['11.2.2020', 43103, 1018],
         ['12.2.2020', 45171, 1115],
         ['13.2.2020', 46997, 1369],
         ['14.2.2020', 49053, 1383],
         ['15.2.2020', 50580, 1526],
         ['16.2.2020', 51857, 1669],
         ['17.2.2020', [70635, 794], [1772, 3]], # laboratory and clinically confirmed case from now on!
         ['18.2.2020', [72528, 804], [1870, 3]],
         ['19.2.2020', [74280, 924], [2006, 3]],
         ['20.2.2020', [74675, 1073], [2121, 8]],
         ['21.2.2020', [75569, 1200], [2239, 8]],
         ['22.2.2020', [76392, 1402], [2348, 11]], # again, back to the lab confirmed cases only!
         ['23.2.2020', [77042, 1769], [2445, 17]],
         ['24.2.2020', [77262, 2069], [2595, 23]],
         ['25.2.2020', [77780, 2459], [2666, 34]],
         ['26.2.2020', [78191, 2918], [2718, 43]],
         ['27.2.2020', [78630, 3664], [2747, 57]],
         ['28.2.2020', [78961, 4691], [2791, 67]],
         ['29.2.2020', [79394, 6009], [2838, 86]],
         [ '1.3.2020', [79968, 7169], [2873, 104]],
         [ '2.3.2020', [80174, 8774], [2915, 128]],
         [ '3.3.2020', [80304, 10566], [2946, 166]],
         [ '4.3.2020', [80422, 12668], [2984, 214]],
         [ '5.3.2020', [80565 , 14768], [3015, 267]],
        #[ '6.3.2020', [, ], [, ]],
        #[ '7.3.2020', [, ], [, ]],
        #[ '8.3.2020', [, ], [, ]],
        #[ '9.3.2020', [, ], [, ]],
        #['10.3.2020', [, ], [, ]],
        #['11.3.2020', [, ], [, ]],
        #['12.3.2020', [, ], [, ]],
        #['13.3.2020', [, ], [, ]],
        #['14.3.2020', [, ], [, ]],
        #['15.3.2020', [, ], [, ]],
        #['16.3.2020', [, ], [, ]],
        #['17.3.2020', [, ], [, ]],
        #['18.3.2020', [, ], [, ]],
        #['19.3.2020', [, ], [, ]],
        #['20.3.2020', [, ], [, ]],
        #['21.3.2020', [, ], [, ]],
        #['22.3.2020', [, ], [, ]],
        #['23.3.2020', [, ], [, ]],
        #['24.3.2020', [, ], [, ]],
        #['25.3.2020', [, ], [, ]],
        #['26.3.2020', [, ], [, ]],
        #['27.3.2020', [, ], [, ]],
        #['28.3.2020', [, ], [, ]],
        #['29.3.2020', [, ], [, ]],
        #['30.3.2020', [, ], [, ]],
        #['31.3.2020', [, ], [, ]],

]

print(Data)


gr_cases = []
gr_deaths = []
mst = [20, 21, 22]
for i in range(0,3):
    gr_case = ROOT.TGraphErrors()
    gr_case.SetMarkerColor(ROOT.kBlack)
    gr_case.SetLineColor(ROOT.kBlack)
    gr_case.SetMarkerStyle(mst[i])
    gr_case.SetMarkerSize(1)
    gr_cases.append(gr_case)

    gr_death = ROOT.TGraphErrors()
    gr_death.SetMarkerColor(ROOT.kRed)
    gr_death.SetLineColor(ROOT.kRed)
    gr_death.SetMarkerStyle(mst[i])
    gr_death.SetMarkerSize(1)
    gr_deaths.append(gr_death)

ipcs = [0, 0, 0]
ipds = [0, 0, 0]

for data in Data:
    date = data[0]
    cases, deaths = data[1],data[2]
    ncases = 0.
    print(cases,deaths)
    try:
        if len(cases) >  1:
            for i in range(1, len(cases)+1):
                ncases = ncases + cases[i-1]
                gr_cases[i].SetPoint(ipcs[i], ipcs[0], cases[i-1])
                gr_cases[i].SetPointError(ipcs[i], 0, sqrt(cases[i-1]) )
                ipcs[i] = ipcs[i] + 1
    except:
        ncases = cases
    gr_cases[0].SetPoint(ipcs[0], ipcs[0], ncases)
    gr_cases[0].SetPointError(ipcs[0], 0, sqrt(ncases) )
    ipcs[0] = ipcs[0] + 1

    ndeaths = 0.
    try:
        if len(deaths) > 1:
            for i in range(1, len(deaths)+1):
                ndeaths = ndeaths + deaths[i-1]
                gr_deaths[i].SetPoint(ipds[i], ipds[0], deaths[i-1])
                gr_deaths[i].SetPointError(ipds[i], 0, sqrt(deaths[i-1]) )
                ipds[i] = ipds[i] + 1
    except:
        ndeaths = deaths
    gr_deaths[0].SetPoint(ipds[0], ipds[0], ndeaths)
    gr_deaths[0].SetPointError(ipds[0], 0, sqrt(ndeaths) )
    ipds[0] = ipds[0]+1


tags = ['Global', 'China', 'World']

can = ROOT.TCanvas()
can.cd()
ROOT.gPad.SetGridx()
ROOT.gPad.SetGridy()
opt = 'AP'
leg = ROOT.TLegend(0.12, 0.7, 0.36, 0.87)
for gr_case,gr_death,tag in zip(gr_cases, gr_deaths,tags):
    gr_case.Draw(opt)
    opt = 'P'
    gr_death.Draw(opt)
    leg.AddEntry(gr_case, '{} cases'.format(tag), 'P')
    leg.AddEntry(gr_death, '{} deaths'.format(tag), 'P')
    gr_case.GetXaxis().SetTitle('WHO report number (~daily)')
    gr_case.GetYaxis().SetTitle('Counts')
    gr_case.GetYaxis().SetRangeUser(1., gr_case.GetYaxis().GetXmax())

leg.Draw()

can.Print('Coronavirus_liny.png')

ROOT.gPad.SetLogy()

gr_cases[0].GetYaxis().SetMoreLogLabels()
gr_cases[0].GetYaxis().SetRangeUser(3., gr_cases[0].GetYaxis().GetXmax()*10.)
           
dgr_cases = []
dgr_deaths = []
lsts = [1, 2, 4]
for gr_case, gr_death, tag, lst in zip(gr_cases, gr_deaths, tags, lsts):
    dgr_case = MakeDerivative(gr_case)
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

    dgr_case.Draw('L')
    dgr_death.Draw('L')

ROOT.gPad.Update()
can.Print('Coronavirus_logy.png')


stuff.append([can, gr_deaths, gr_cases, leg])

ROOT.gApplication.Run()
