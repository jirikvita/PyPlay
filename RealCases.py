#!/usr/bin/python
# from __future__ import print_function
import ROOT

stuff = []

# data from https://www.who.int/emergencies/diseases/novel-coronavirus-2019/situation-reports/
# date, total cases, deaths total
# global data
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
]

print(Data)

gr_cases = ROOT.TGraph()
gr_cases.SetMarkerColor(ROOT.kBlack)
gr_cases.SetLineColor(ROOT.kBlack)
gr_cases.SetMarkerStyle(20)
gr_cases.SetMarkerSize(1)

gr_deaths = ROOT.TGraph()
gr_deaths.SetMarkerColor(ROOT.kRed)
gr_deaths.SetLineColor(ROOT.kRed)
gr_deaths.SetMarkerStyle(21)
gr_deaths.SetMarkerSize(1)


ip = 0
for data in Data:
    date = data[0]
    cases, deaths = data[1],data[2]
    gr_cases.SetPoint(ip, ip, cases)
    gr_deaths.SetPoint(ip, ip, deaths)
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

can.Print('Coronavirus_liny.png')

ROOT.gPad.SetLogy()
gr_cases.GetYaxis().SetMoreLogLabels()
gr_cases.GetYaxis().SetRangeUser(3., gr_cases.GetYaxis().GetXmax()*10.)

ROOT.gPad.Update()
can.Print('Coronavirus_logy.png')


stuff.append([can, gr_deaths, gr_cases, leg])

ROOT.gApplication.Run()
