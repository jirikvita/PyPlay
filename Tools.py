#!/usr/bin/python
# jiri kvita 2020

import ROOT
from math import log10

# distance scaling:
gkm = 1.


cans = []
stuff = []

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

def MakePads(can, ratio_size = 0.35, PadSeparation = 0.0, UpperPadBottomMargin = 0.1, LowerPadTopMargin = 0.0): 
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

    # two pads on the right above each other
    
    pad1 = ROOT.TPad("p1","p1",x0,ratio_size + PadSeparation/2,x1,y1)
    pad1.Draw()
    pad1.SetTopMargin(0.07)
    pad1.SetBottomMargin(UpperPadBottomMargin)
    #pad1.SetFillColor(ROOT.kBlue)
    #pad1.SetBorderSize(1)
    #pad1.SetFillColor(ROOT.kYellow)
    pad1.Draw()
    
    pad2 = ROOT.TPad("p2","p2",x0,y0,x1,ratio_size - PadSeparation/2)
    pad2.Draw()
    pad2.SetTopMargin(LowerPadTopMargin)
    pad2.SetBottomMargin(0.10)
    #pad2.SetLineColor(ROOT.kRed)
    #pad2.SetFillColor(ROOT.kOrange)
    #pad2.SetBorderSize(1)
    #pad2.SetFillColor(ROOT.kGray)
    pad2.Draw()
    
             
    return padMain,pad1,pad2
