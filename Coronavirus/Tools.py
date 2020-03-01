#!/usr/bin/python
# jiri kvita 2020

import ROOT
from math import log10

# distance scaling:
gkm = 1.


cans = []
stuff = []

#########################################
def CountPeople(families):
    n = 0
    for fam in families:
        n = n + len(fam.GetMembers())
    return n

#########################################
def MakeDerivative(gr):
    dgr = ROOT.TGraph()
    x1 = ROOT.Double()
    y1 = ROOT.Double()
    x2 = ROOT.Double()
    y2 = ROOT.Double()
    for i in range(0,gr.GetN()-1):
        gr.GetPoint(i, x1, y1)
        gr.GetPoint(i+1, x2, y2)
        der = (y2-y1) / (x2-x1)
        x = 0.5*(x1+x2)
        dgr.SetPoint(i, x, der)
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
