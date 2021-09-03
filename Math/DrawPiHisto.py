#!/usr/bin/python

# jiri kvita, 12.4.2017
# http://www.thealmightyguru.com/Pointless/PI-10000.html
# http://www.geom.uiuc.edu/~huberty/math5337/groupe/digits.html
# http://3.141592653589793238462643383279502884197169399375105820974944592.com/

from myAll import *

fnames = ['pi_10k.txt', 'pi_100k.txt']


h1s = []
cols = [ROOT.kBlack, ROOT.kRed]



for col,fname in zip(cols,fnames):

    tfile = open(fname, 'r')
    tag = fname
    tag= tag.replace('.txt', '').replace('pi_', '')
    h1 = ROOT.TH1D('pistat_' + tag, '#pi to ' + tag + ' digits', 10, -0.5, 9.5)
    h1.Sumw2()
    for line in tfile.readlines():
        for char in line[:-1]:
            if char == '' or char == ' ':
                continue
            #print '"%s"' % (char,)
            val = int(char)
            #print '%s == %i' % (char,val,)
            h1.Fill(1.*val)

    h1.SetMarkerColor(col)
    h1.SetMarkerStyle(20)
    #h1.SetMarkerColor(ROOT.kRed)
    h1.SetLineColor(col)
    h1.SetStats(0)
    h1.Scale(1./h1.Integral())
    h1.SetMinimum(0.)
    tfile.close()
    h1s.append(h1)

can = nextCan.nextTCanvas('pistat', 'pistat', 0, 0, 1000, 800)
#can.Divide(2,2)
can.cd(1)
ROOT.gPad.SetGridx() ; ROOT.gPad.SetGridy()
opt = ''
leg = ROOT.TLegend(0.5, 0.25, 0.9, 0.55)
for h1 in h1s:
     h1.Draw('e1hist' + opt)
     opt = 'same'
     leg.AddEntry(h1, h1.GetTitle(), 'PL')
   
leg.Draw()
ROOT.gApplication.Run()

