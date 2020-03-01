#!/usr/bin/python
# from __future__ import print_function
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
         ['1.2.2020', 11953, 259],
         ['2.2.2020', 14557, 305],
         ['3.2.2020', 17391, 362],
         ['4.2.2020', 20630, 426],
         ['5.2.2020', 24554, 494],
         ['6.2.2020', 28276, 565],
         ['7.2.2020', 31481, 638],
         ['8.2.2020', 34886, 724],
         ['9.2.2020', 37558, 813], 
         ['10.2.2020', 40554, 910],
         ['11.2.2020', 43103, 1018],
         ['12.2.2020', 45171, 1115],
         ['13.2.2020', 46997, 1369],
         ['14.2.2020', 49053, 1383],
         ['15.2.2020', 50580, 1526],
         ['16.2.2020', 51857, 1669],
         ['17.2.2020', 71429, 1775], # laboratory and clinically confirmed case from now on!
         ['18.2.2020', 73332, 1873],
         ['19.2.2020', 75204, 2009],
         ['20.2.2020', 75748, 2129],
         ['21.2.2020', 76769, 2247],
         ['22.2.2020', 77794, 2348 + 11], # again, back to the lab confirmed cases only!
         ['23.2.2020', 78811, 2445 + 17],
         ['24.2.2020', 79331, 2595 + 23],
         ['25.2.2020', 80239, 2666 + 34],
         ['26.2.2020', 81109, 2718 + 43],
         ['27.2.2020', 82294, 2747 + 57],
         ['28.2.2020', 83652, 2791 + 67],
         ['29.2.2020',79394 + 6009 , 2838 + 86],
         ['1.3.2020', 79968 + 7169, 2873 + 104],
         #['2.3.2020', , ],
         #['3.3.2020', , ],
         #['.3.2020', , ],
]

print(Data)

gr_cases = ROOT.TGraphErrors()
gr_cases.SetMarkerColor(ROOT.kBlack)
gr_cases.SetLineColor(ROOT.kBlack)
gr_cases.SetMarkerStyle(20)
gr_cases.SetMarkerSize(1)

gr_deaths = ROOT.TGraphErrors()
gr_deaths.SetMarkerColor(ROOT.kRed)
gr_deaths.SetLineColor(ROOT.kRed)
gr_deaths.SetMarkerStyle(21)
gr_deaths.SetMarkerSize(1)


ip = 0
for data in Data:
    date = data[0]
    cases, deaths = data[1],data[2]
    gr_cases.SetPoint(ip, ip, cases)
    gr_cases.SetPointError(ip, 0, sqrt(cases) )
    gr_deaths.SetPoint(ip, ip, deaths)
    gr_deaths.SetPointError(ip, 0, sqrt(deaths) )
    ip = ip+1

can = ROOT.TCanvas()
can.cd()
ROOT.gPad.SetGridx()
ROOT.gPad.SetGridy()
gr_cases.Draw('AP')
gr_deaths.Draw('P')
leg = ROOT.TLegend(0.12, 0.7, 0.4, 0.87)
leg.AddEntry(gr_cases, 'Global cases', 'P')
leg.AddEntry(gr_deaths, 'Global deaths', 'P')
leg.Draw()
gr_cases.GetXaxis().SetTitle('WHO report number (~daily)')
gr_cases.GetYaxis().SetTitle('Counts')
gr_cases.GetYaxis().SetRangeUser(1., gr_cases.GetYaxis().GetXmax())

can.Print('Coronavirus_liny.png')

ROOT.gPad.SetLogy()
gr_cases.GetYaxis().SetMoreLogLabels()
gr_cases.GetYaxis().SetRangeUser(3., gr_cases.GetYaxis().GetXmax()*10.)

dgr_cases = MakeDerivative(gr_cases)
dgr_cases.SetLineColor(gr_cases.GetLineColor())
dgr_cases.SetLineWidth(2)
dgr_deaths = MakeDerivative(gr_deaths)
dgr_deaths.SetLineColor(gr_deaths.GetLineColor())
dgr_deaths.SetLineWidth(2)

leg.AddEntry(gr_cases, 'Derivative of cases', 'L')
leg.AddEntry(gr_deaths, 'Derivative of deaths', 'L')


dgr_cases.Draw('L')
dgr_deaths.Draw('L')

ROOT.gPad.Update()
can.Print('Coronavirus_logy.png')


stuff.append([can, gr_deaths, gr_cases, leg])

ROOT.gApplication.Run()
