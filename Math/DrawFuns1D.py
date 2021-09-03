#!/usr/bin/python
from math import pi
# jk 26.2.2021

import ROOT

stuff = []

canname = 'FunFunctions1D'
can = ROOT.TCanvas(canname, canname, 0, 0, 1200,900)
can.Divide(2,2)

can.cd(1)
ROOT.gPad.SetGridy(1)
fun1 = ROOT.TF1("sin1", "sin(1/x)", -0.1, 0.1)
fun1.SetNpx(10000)
fun1.SetLineWidth(1)
fun1.Draw()

can.cd(2)
ROOT.gPad.SetGridx(1)
ROOT.gPad.SetGridy(1)
fun2 = ROOT.TF1("hat", "exp(-1/(1-x^2))", -1, 1)
#fun2.SetNpx(10000)
#fun2.SetLineWidth(1)
fun2.Draw()


can.cd(3)
ROOT.gPad.SetGridx(1)
ROOT.gPad.SetGridy(1)
fun3 = ROOT.TF1("fun3", "sin(x^2)", -3*pi, 3*pi)
fun3.SetNpx(10000)
fun3.SetLineWidth(1)
fun3.Draw()

can.cd(4)
ROOT.gPad.SetGridx(1)
ROOT.gPad.SetGridy(1)
fun4 = ROOT.TF1("sinc", "sin(x)/x", -15*pi, 15*pi)
fun4.SetNpx(1000)
fun4.Draw()
# asymptotes
afun4a = ROOT.TF1("sina", "1/x", -15*pi, 15*pi)
afun4a.SetNpx(1000)
afun4a.SetLineColor(ROOT.kBlack)
afun4a.SetLineStyle(4)
#afun4a.Draw('same')
afun4b = ROOT.TF1("sinb", "-1/x", -15*pi,15*pi)
afun4b.SetNpx(1000)
afun4b.SetLineColor(ROOT.kBlack)
afun4b.SetLineStyle(4)
#afun4b.Draw('same')




canname = 'TaylorExample'
can2 = ROOT.TCanvas(canname, canname, 100, 100, 1400, 700)
can2.Divide(2,1)
ROOT.gPad.SetGridx(1)
ROOT.gPad.SetGridy(1)

can2.cd(1)
# Taylor sin(x)
k = 1
x1 = -k*pi
x2 = k*pi
fun5 = ROOT.TF1("fun5", "sin(x)", x1, x2)
fun5.Draw()
fun5.SetLineWidth(3)

p1 = ROOT.TF1("p1", "x", x1,x2)
p1.SetLineColor(ROOT.kMagenta)
p1.SetLineStyle(2)
p1.Draw('same')

p3 = ROOT.TF1("p3", "x-x^3/6", x1, x2)
p3.SetLineColor(ROOT.kBlack)
p3.SetLineStyle(2)
p3.Draw('same')

p5 = ROOT.TF1("p5", "x-x^3/6+x^5/TMath::Factorial(5)", x1, x2)
p5.SetLineColor(ROOT.kGreen+2)
p5.SetLineStyle(2)
p5.Draw('same')

p7 = ROOT.TF1("p7", "x-x^3/6+x^5/TMath::Factorial(5)-x^7/TMath::Factorial(7)", x1,x2)
p7.SetLineColor(ROOT.kBlue)
p7.SetLineStyle(2)
p7.Draw('same')

# redraw
fun5.Draw('same')
leg1 = ROOT.TLegend(0.2, 0.6, 0.50, 0.88)
leg1.SetBorderSize(0)
leg1.AddEntry(fun5, 'sin(x)', 'L')
leg1.AddEntry(p1, 'Taylor p_{1}', 'L')
leg1.AddEntry(p3, 'Taylor p_{3}', 'L')
leg1.AddEntry(p5, 'Taylor p_{5}', 'L')
leg1.AddEntry(p7, 'Taylor p_{7}', 'L')
leg1.Draw()



can2.cd(2)
# Taylor cos(x)
k = 1
x1 = -k*pi
x2 = k*pi
fun6 = ROOT.TF1("fun6", "cos(x)", x1, x2)
fun6.Draw()
fun6.SetLineWidth(3)

p0 = ROOT.TF1("p0", "1", x1,x2)
p0.SetLineColor(ROOT.kMagenta)
p0.SetLineStyle(2)
p0.Draw('same')

p2 = ROOT.TF1("p2", "1 - x^2/2", x1, x2)
p2.SetLineColor(ROOT.kBlack)
p2.SetLineStyle(2)
p2.Draw('same')

p4 = ROOT.TF1("p4", "1 - x^2/2 + x^4/TMath::Factorial(4)", x1, x2)
p4.SetLineColor(ROOT.kGreen+2)
p4.SetLineStyle(2)
p4.Draw('same')

p6 = ROOT.TF1("p6", "1-x^2/2 + x^4/TMath::Factorial(4) - x^6/TMath::Factorial(6)", x1,x2)
p6.SetLineColor(ROOT.kBlue)
p6.SetLineStyle(2)
p6.Draw('same')

# redraw
fun6.Draw('same')
leg2 = ROOT.TLegend(0.3, 0.12, 0.70, 0.40)
leg2.SetBorderSize(0)
leg2.AddEntry(fun6, 'cos(x)', 'L')
leg2.AddEntry(p1, 'Taylor p_{0}', 'L')
leg2.AddEntry(p3, 'Taylor p_{2}', 'L')
leg2.AddEntry(p5, 'Taylor p_{4}', 'L')
leg2.AddEntry(p7, 'Taylor p_{6}', 'L')
leg2.Draw()



ps = [p1, p3, p5, p7, p0, p2, p4, p6]
for p in ps:
    p.SetLineWidth(3)
ROOT.gPad.Update()


can.Print(can.GetName() + '.png')
can.Print(can.GetName() + '.pdf')
can2.Print(can2.GetName() + '.png')
can2.Print(can2.GetName() + '.pdf')

stuff.append([can, can2, fun1, fun2, fun3, fun4, fun5, leg1, leg2])

ROOT.gApplication.Run()
