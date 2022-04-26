#!/usr/bin/python
# jiri kvita 2020

import ROOT
from math import log10, sqrt, pow, fabs

# distance scaling:
gkm = 1.
import ctypes

cans = []
stuff = []

#########################################

def MakeAgeDeathFact():
    # data: https://www.vox.com/2020/3/12/21173783/coronavirus-death-age-covid-19-elderly-seniors
    acan = ROOT.TCanvas()
    acan.cd()
    print('Fitting age death fact')
    deathprobDict = { 9: 0.01e-2, 19: 0.02e-2, 29: 0.09e-2, 39: 0.18e-2, 49: 0.40e-2, 59: 1.3e-2, 69: 4.6e-2, 79: 9.8e-2, 85: 18e-2}
    gr_ageDeathFact = ROOT.TGraphErrors()
    ip = 0
    x0 = 0.
    ages = []
    for age in deathprobDict:
        ages.append(age)
    ages.sort()
    for age in ages:
        print((x0, age))
        errSF = 0.10 # arb. fractional error for better fit behaviour
        gr_ageDeathFact.SetPoint(ip, 0.5 * (age + x0), deathprobDict[age])
        gr_ageDeathFact.SetPointError(ip, 0., errSF*deathprobDict[age])
        x0 = 1.*age
        ip += 1
    gr_ageDeathFact.SetMarkerStyle(20)
    gr_ageDeathFact.SetMarkerSize(1)
    gr_ageDeathFact.SetMarkerColor(ROOT.kBlack)
    fit_ageDeathFact = ROOT.TF1('myexp', '[0]*exp([1]*x)+[2]', 0, 100)
    fit_ageDeathFact.SetParameters(0.001, 0.01, 0.)
    gr_ageDeathFact.Fit('myexp')
    gr_ageDeathFact.Draw('AP')
    return acan, gr_ageDeathFact, fit_ageDeathFact

#########################################
def CountPeople(families):
    n = 0
    for fam in families:
        n = n + len(fam.GetMembers())
    return n

#########################################
def MakeDiffGr(gr1, gr2):
    dgr = ROOT.TGraphErrors()
    x1 = ctypes.c_double()
    y1 = ctypes.c_double()
    x2 = ctypes.c_double()
    y2 = ctypes.c_double()
    i1 = 0
    i2 = 0
    ip = 0
    n1,n2 =  gr1.GetN(),gr2.GetN()
    for i in range(0, max(n1,n2) - 1):
        if i1 >= n1 or i2 >= n2:
            break
        gr1.GetPoint(i1, x1, y1)
        gr2.GetPoint(i2, x2, y2)
        xx1 = x1.value
        xx2 = x2.value
        yy1 = y1.value
        yy2 = y2.value
        if fabs(xx1 - xx2) > 1e-3:
            print(('WARNING in MakeDiffGr: too different x values {}, {}. Shifting indices {} {}'.format(xx1, xx2, i1, i2)))
            if xx1 < xx2:
                i1 += 1
            else:
                i2 += 1
            continue
        diff = yy1-yy2
        err = sqrt(fabs(diff))
        dgr.SetPoint(ip, x1, diff)
        dgr.SetPointError(ip, 0, err)
        ip = ip + 1
        i1 += 1
        i2 += 1

    return dgr
#########################################
def MakeDerivative(gr):
    dgr = ROOT.TGraph()
    x1 = ctypes.c_double()
    y1 = ctypes.c_double()
    x2 = ctypes.c_double()
    y2 = ctypes._double()
    xx1 = x1.value
    xx2 = x2.value
    yy1 = y1.value
    yy2 = y2.value
    for i in range(0,gr.GetN()-1):
        gr.GetPoint(i, x1, y1)
        gr.GetPoint(i + 1, x2, y2)
        der = (yy2-yy1) / (xx2-xx1)
        x = 0.5*(xx1+xx2)
        dgr.SetPoint(i, x, der)
        # err = ...
        # dgr.SetPointError(i, x, err)
    return dgr

#########################################
def CopyStyle(g1, g2):
    g2.SetLineColor(g1.GetLineColor())
    g2.SetLineStyle(g1.GetLineStyle())
    g2.SetLineWidth(g1.GetLineWidth())
    g2.SetMarkerStyle(g1.GetMarkerStyle())
    g2.SetMarkerSize(g1.GetMarkerSize())
    g2.SetMarkerColor(g1.GetMarkerColor())

#########################################
def MakeSeqRatio(gr):
    dgr = ROOT.TGraph()
    x1 = ctypes.c_double()
    y1 = ctypes.c_double()
    x2 = ctypes.c_double()
    y2 = ctypes.c_double()
    i = 0
    for ii in range(0,gr.GetN()-1):
        gr.GetPoint(ii, x1, y1)
        gr.GetPoint(ii + 1, x2, y2)
        if y1 > 0.:
            val = y2 / y1
            x = 0.5*(x1+x2)
            dgr.SetPoint(i, x, val)
            i = i + 1
    return dgr

#########################################
def MakeDigitStr(i, digits = 4):
    # from /home/qitek/Dropbox/work/Vyuka/SFVE/Poznamky_Cz/Toys/PeakSim/PeakSim.py
    tag = str(i)
    n = digits
    try: 
        n = int(log10(i))
    except ValueError:
        pass
    if i is 0:
        n = 0
    for i in range(0, digits - n):
        tag = '0' + tag
    return tag



#########################################################

def MakePads(can, ratio_size = 0.35, nSubPads = 3, PadSeparation = 0.0, UpperPadBottomMargin = 0.1, LowerPadTopMargin = 0.0): 
    x0 = 0.75
    x1 = 0.99
    y0 = 0.01
    y1 = 0.99

    # main pad on the left
    padMain = ROOT.TPad("padMain","padMain",0.01, y0, x0, y1);
    padMain.SetTopMargin(0.15);
    padMain.SetBottomMargin(0.20);
    #padMain.SetFillColor(ROOT.kGreen+2)
    padMain.Draw();

    # three pads on the right above each other
    pads = []
    for i in range(0,nSubPads):
        pad = ROOT.TPad('pad{}'.format(i),'pad'.format(i),x0, (y1-y0)/nSubPads*i ,x1,(y1-y0)/nSubPads*(i+1))
        pad.Draw()
        #pad.SetTopMargin(0.07)
        #pad.SetBottomMargin(UpperPadBottomMargin)
        #pad.SetFillColor(ROOT.kBlue)
        #pad.SetBorderSize(1)
        #pad.SetFillColor(ROOT.kYellow)
        pad.Draw()
        pads.append(pad)

    return padMain,pads
