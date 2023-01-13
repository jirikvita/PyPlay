#!/snap/bin/pyroot
# JK 2022 based on data by KMA converted to tables by PB
import numpy as np
import matplotlib.pyplot as plt
import ROOT

stuff = []
cans = []

###########################################################################
fnames = { 1 : 't#bar{t} p_{T,j1,j2}^{min} = 200 GeV',
           2 : 't#bar{t} p_{T,j1,j2}^{min} = 60 GeV, p_{T,j1,j2}^{max} = 200 GeV',
           3 : 't#bar{t} p_{T,j1}^{min} = 200 GeV, p_{T,j2} #in (60,200) GeV',
           4: "Z' m=1000 GeV",
           5: "Z' m=1250 GeV"
          }
cols =  { 1 : ROOT.kBlack,
           2 : ROOT.kGray + 2,
           3 : ROOT.kGray + 1,
           4: ROOT.kGreen + 2,
           5: ROOT.kBlue
          }

###########################################################################
def PlotMultiHbarWithLabels(cname, cols, fnames, data, ylabel):
    nfiles = len(fnames)
    can = ROOT.TCanvas(cname, cname)
    hs = {}
    nbins = len(data)
    x1 = 0
    x2 = nbins
    
    labels = []
    for label in data:
        labels.append(label)
    for ifile in range(1,1+len(data[labels[0]])):
        hname = 'histo_{}_{}'.format(cname,ifile)
        htitle = hname + ';;{}'.format(ylabel)
        h1 = ROOT.TH1D(hname, htitle, nbins, x1, x2)
        il = 0
        for label in data:
            il = il + 1
            h1.GetXaxis().SetBinLabel(il, label)
        h1.GetXaxis().SetLabelSize(max(0.07,0.16 / nbins))
        h1.SetFillColor(cols[ifile])
        h1.SetFillStyle(1111)
        il = 0
        for label in data:
            il = il + 1
            h1.SetBinContent(il, data[label][ifile-1])
            h1.SetBinError(il, 0.)
        h1.Scale(1.)
        hs[ifile] = h1
      
    ymax = -9e9
    for ifile in hs:
        h = hs[ifile]
        hm = h.GetMaximum()
        if hm > ymax:
            ymax = 1.*hm
    
    ROOT.gStyle.SetOptTitle(0)    
    w = 1.
    boff = 0.05
    for ifile in hs:
        h = hs[ifile]
        h.SetMaximum(1.5*ymax)
        h.SetMinimum(0.)
        h.SetStats(0)
        bw = (w - 2*boff) / (nfiles+1)
        h.SetBarWidth(bw)
        h.SetBarOffset(boff + ifile*bw)
 
    opt = ''

    lx1, ly1, lx2, ly2 = 0.4, 0.65, 0.88, 0.88
    if len(hs) < 3:
        lx1, ly1, lx2, ly2 = 0.6, 0.80, 0.88, 0.88
    leg = ROOT.TLegend(lx1, ly1, lx2, ly2)
    leg.SetBorderSize(0)

    for ifile in hs:    
        h = hs[ifile]
        h.Draw('bar' + opt)
        opt = 'same'
        leg.AddEntry(h, fnames[ifile], 'f')
    leg.Draw()
    return can,leg,hs

###########################################################################
def PlotMultiHbarWithLabelsColumns(cname, cols, fnames, columns, data, ylabel = ''):
    nfiles = len(fnames)
    can = ROOT.TCanvas(cname, cname)
    hs = {}
    leg = ROOT.TLegend(0.4, 0.65, 0.88, 0.88)
    leg.SetBorderSize(0)
    nbins = len(columns)
    x1 = 0
    x2 = nbins
    
    labels = []
    for label in columns:
        labels.append(label)
    for ifile in range(1,1+len(data)):
        hname = 'histo_{}_{}'.format(cname,ifile)
        htitle = hname + ';;{}'.format(ylabel)
        h1 = ROOT.TH1D(hname, htitle, nbins, x1, x2)
        il = 0
        for label in labels:
            il = il + 1
            h1.GetXaxis().SetBinLabel(il, label)
        h1.GetXaxis().SetLabelSize(max(0.05,0.16 / nbins))
        h1.SetFillColor(cols[ifile])
        h1.SetFillStyle(1111)
        hs[ifile] = (h1)
        
    for fdata in data:
        ifile = fdata[0]
        for il in range(1,len(fdata)):
            hs[ifile].SetBinContent(il, fdata[int(il)])
            hs[ifile].SetBinError(il, 0.)
        
    ymax = -9e9
    for ifile in hs:
        h = hs[ifile]
        h.Scale(1.)
        hm = h.GetMaximum()
        if hm > ymax:
            ymax = 1.*hm
    
    ROOT.gStyle.SetOptTitle(0)    
    w = 1.
    boff = 0.05
    for ifile in hs:
        h = hs[ifile]
        h.SetMaximum(1.5*ymax)
        h.SetMinimum(0.)
        h.SetStats(0)
        bw = (w - 2*boff) / (nfiles+1)
        h.SetBarWidth(bw)
        h.SetBarOffset(boff + ifile*bw)
 
    opt = ''
    for ifile in hs:    
        h = hs[ifile]
        h.Draw('bar' + opt)
        opt = 'same'
        leg.AddEntry(h, fnames[ifile], 'f')
    leg.Draw()
    return can,leg,hs
    
    
###########################################################################
###########################################################################
###########################################################################

#Table 1
d1 = {#'File \#': [1, 2, 3, 4, 5], 
      'Jets': [797363,446838,781675,449606,388593], 
      'Events': [317338,236406,325029,273762,212983] }
can1,leg1,hs1 = PlotMultiHbarWithLabels('Tab1EventsJetsMulti', cols, fnames, d1, 'Multiplicity')
stuff.append([can1, leg1, hs1])
ROOT.gPad.Update()
cans.append(can1)

###########################################################################
# Table 2
columns2=[#'Files/Jets',
          't', 'w', 'l']
d2 = np.array([[1,11.83, 13.20, 74.97],
               [2,0.86 , 8.88 , 90.27],
               [3,5.06 , 10.45, 84.49],
               [4,15.76, 14.49, 69.75],
               [5,23.77, 11.78, 64.45]])
can2,leg2,hs2 = PlotMultiHbarWithLabelsColumns('Tab2SamplesJetStructure', cols, fnames, columns2, d2, 'True jet multiplicity fractions [%]')
ROOT.gPad.Update()
cans.append(can2)

###########################################################################
# Table 3
columns3 = [#'Files/Number of Jets',
            '1','2','3','4','5','6','7','8','9']
d3 = np.array([[1 , 4.68 , 41.85 , 37.82 , 13.05 , 2.33 , 0.25 , 0.02 , 0 , 0],
               [2 , 26.97 , 45.22 , 22.65 , 4.65 , 0.48 , 0.03 , 0 , 0, 0],
               [3 , 8.34 , 42.61 , 34.88 , 11.97 , 2.00 , 0.20 , 0.01 , 0 , 0],
               [4 , 17.66 , 56.07 , 21.30 , 4.39 , 0.54 , 0.05 , 0 , 0 ,0],
               [5 , 14.51 , 57.81 , 22.45 , 4.54 , 0.62 , 0.06 , 0.01 , 0 ,0]])
can3,leg3,hs3 = PlotMultiHbarWithLabelsColumns('Tab3LJetsMulti', cols, fnames, columns3, d3, 'Jet multiplicity frations [%]')
ROOT.gPad.Update()
cans.append(can3)

###########################################################################
# Tabel 4
columns5 = [#'File',
            'tt','tl', 'lt','tW','Wt','Wl','lW','ll']
d5 = np.array([[1, 10.36,38.40,19.25,8.41,3.86,1.57,2.67,15.48],
               [2, 7.16,48.55,11.48,7.58,1.42,0.53,2.83,20.45],
               [3, 6.21,39.97,17.44,7.64,3.43,1.38,2.63,21.30],
               [4, 14.53,42.01,15.62,10.12,5.62,1.24,1.59,9.28],
               [5, 19.91,40.16,17.18,8.24,4.69,0.98,1.26,7.59]])
can5,leg5,hs5 = PlotMultiHbarWithLabelsColumns('Tab4DijetTrueStructureTop', cols, fnames, columns5, d5, 'True event fractions, t [%]')
ROOT.gPad.Update()
cans.append(can5)

###########################################################################
# Tabel 5
columns6 = [#'File',
            'WW','Wl','lW','Wt','tW','tl','lt','ll']
d6 = np.array([[1, 7.98,28.59,21.23,3.04,6.63,4.96,2.15,25.42],
               [2, 3.56,32.89,10.38,0.09,0.49,1.09,0.20,51.30],
               [3, 4.00,23.84,16.52,1.17,2.61,3.33,1.24,47.29],
               [4, 5.15,24.11,14.42,4.42,7.97,8.38,2.65,32.89],
               [5, 4.12,22.44,14.46,6.53,11.47,9.26,3.45,28.26]])

can6,leg6,hs6 = PlotMultiHbarWithLabelsColumns('Tab5DijetTrueStructureW', cols, fnames, columns6, d6, 'True event fractions, W [%]')
ROOT.gPad.Update()
cans.append(can6)

###########################################################################
# Table 6
columns7 = [#'File',
            't','w','l']
d7a = np.array([[1, 74.56 ,0,25.44],
               [2,73.89,0,26.11],
               [3,69.3,0,30.70],
               [4,84.44,0,15.56],
               [5,86.63,0,13.37]])
d7b = np.array([[1 ,0,49.94,50.06],
               [2 ,0,38.64,61.36],
               [3 ,0,35.41,64.59],
               [4 ,0,46.94,53.06],
               [5 ,0,48.65,51.35]])
can7a,leg7a,hs7a = PlotMultiHbarWithLabelsColumns('Tab6TrueStructureTop', cols, fnames, columns7, d7a, 'Training fractions, t [%]')
ROOT.gPad.Update()
can7b,leg7b,hs7b = PlotMultiHbarWithLabelsColumns('Tab6TrueStructureW', cols, fnames, columns7, d7b, 'Training fractions, W [%]')
ROOT.gPad.Update()
cans.append(can7a)
cans.append(can7b)

###########################################################################
# Table 7
columns8 = [#'File', 
            #'Set',
            'Accuracy','Precision','Recall','False positive rate']
d8a = np.array([[1, 75.51,75.84,98.57,92.15],
                [2, 76.30,75.81,99.93,91.55],
                [3, 70.44,98.21,70.60,33.84],
                [4, 84.64,84.64,99.96,98.96],
                [5, 84.74,86.77,99.94,98.82] ])
d8b = np.array([[1, 75.15,75.60,98.39,92.68],
                [2,  72.90,73.30,98.95,97.71],
                [3, 70.11,70.57,97.73,92.79],
                [4,  84.26,84.32,99.89,99.30],
                [5, 84.64,86.68,99.93,99.30]])
can8a,leg8a,hs8a = PlotMultiHbarWithLabelsColumns('Tab7ResultsTopTrain', cols, fnames, columns8, d8a, 'Resuts, Top, train [%]')
ROOT.gPad.Update()
cans.append(can8a)
can8b,leg8b,hs8b = PlotMultiHbarWithLabelsColumns('Tab7ResultsTopTest', cols, fnames, columns8, d8b, 'Resuts, Top, test [%]')
ROOT.gPad.Update()
cans.append(can8b)


###########################################################################
# Table 8

# here was mistake ??? 32.30.97 ==> 32.30
columns9 = [#'File', 
            #'Set',
            'Accuracy','Precision','Recall','False positive rate']
d9a = np.array([[1, 63.75,62.33,69.53,42.03],
                [2, 64.83,58.21,32.13,14.54],
                [3, 66.40,57.60,19.62,7.92],
                [4, 61.73,59.65,57.11,34.18],
                [5, 62.95,61.42,64.69,38.70]])
d9b = np.array([[1, 63.19,61.61,68.91,42.48],
                [2, 64.72,57.52,32.30,14.96],
                [3, 66.17,56.28,18.99,8.06],
                [4, 61.49,59.35,57.08,34.60],
                [5, 62.44,60.53,63.67,38.71]])
can9a,leg9a,hs9a = PlotMultiHbarWithLabelsColumns('Tab8ResultsWTrain', cols, fnames, columns9, d9a, 'Resuts, W, train [%]')
ROOT.gPad.Update()
cans.append(can9a)
can9b,leg9b,hs9b = PlotMultiHbarWithLabelsColumns('Tab8ResultsWTest', cols, fnames, columns9, d9b, 'Resuts, W, test [%]')
ROOT.gPad.Update()
cans.append(can9b)


###########################################################################
# Table 9
columns10 = [#'File', 
             'Accuracy', 'Precision', 'Recall', 'False positive rate']
d10 = np.array([[1 , 75.46 , 75.89 , 98.32 , 91.54],
                [2 , 72.56 , 75.18 , 93.85 , 87.68],
                [3 , 69.79 , 71.01 , 95.33 , 87.85],
                [4 , 83.34 , 85.07 , 97.36 , 92.77],
                [5 , 86.21 , 87.07 , 98.75 , 95.02]])
can10,leg10,hs10 = PlotMultiHbarWithLabelsColumns('Tab9ResultsTopPartial', cols, fnames, columns10, d10, 'Resuts, Top partial test [%]')
ROOT.gPad.Update()
cans.append(can10)
###########################################################################
# Table 10
columns11 = [#'File', 
             'Accuracy','Precision','Recall','False positive rate']
d11 = np.array([[1 , 63.56 , 62.14 , 69.16 , 42.03 ],
                [2 , 61.09 , 49.10 , 19.39 , 12.66 ],
                [3 , 61.04 , 45.51 , 50.75 , 33.31 ],
                [4 , 58.94 , 55.29 , 65.48 , 46.84 ],
                [5 , 58.16 , 56.09 , 64.49 , 47.84 ]])
can11,leg11,hs11 = PlotMultiHbarWithLabelsColumns('Tab10ResultsWPartial', cols, fnames, columns11, d11, 'Resuts, W partial test [%]')
ROOT.gPad.Update()
cans.append(can11)



###########################################################################
# Table 11
# needs special care
#d12
columns12 = [#'File X?',
             't','w','l']
# , t prediction
d12a = np.array([[1, 53.28 , 8.36 , 38.36],
                [2, 34.16 , 6.19 , 59.65],
                [3, 23.67 , 4.58 , 71.76] ])
#W prediction
d12b = np.array([[1, 7.62 , 47.25 , 45.12],
                [2, 7.22 , 28.10 , 64.68],
                [3, 6.17 , 19.67 , 74.17]])
names = {1 : '2 jets', 2 : '3 jets', 3 : '4 jets'}
jcols = {1: ROOT.kMagenta, 2 : ROOT.kMagenta+1, 3:ROOT.kMagenta+2}
#jcols = {1: ROOT.kOrange-2, 2 : ROOT.kOrange-3, 3:ROOT.kOrange+7}
can12a,leg12a,hs12a = PlotMultiHbarWithLabelsColumns('Tab11DataStructurePerEventTop', jcols, names, columns12, d12a, 'Jet fractions, Top [%]')
ROOT.gPad.Update()
cans.append(can12a)
jcols = {1: ROOT.kCyan, 2 : ROOT.kCyan+1, 3:ROOT.kCyan+2}
can12b,leg12b,hs12b = PlotMultiHbarWithLabelsColumns('Tab11DataStructurePerEventW', jcols, names, columns12, d12b, 'Jet fractions, W [%]')
ROOT.gPad.Update()
cans.append(can12b)

###########################################################################
# Table 12, data structure for Top jets
# needs special care
#columns13 = [#'Jets in an event',
#             'Fraction']
d13 = {'tl' : [41.01],
       'tt' : [17.43],
       'tw' : [9.11],
       'lt' : [16.46],
       'll' : [8.37],
       'lw' : [1.41],
       'wt' : [5.12],
       'wl' : [1.10] }
names = {1 : 'Top tagging'}
ecols = {1 : ROOT.kMagenta+1}
can13,leg13,hs13 = PlotMultiHbarWithLabels('Tab12EventFractionsTop', ecols, names, d13, 'Event fractions, Top [%]')
stuff.append([can13, leg13, hs13])
ROOT.gPad.Update()
cans.append(can13)

###########################################################################
# Table 13, data structure for Top jets
# needs special care
columns14 = [#'Jets in an event', 
             'Fraction']
d14 = {'wl':[ 43.71],
       'll':[ 6.45],
       'ww':[ 8.29],
       'lw':[ 26.29],
       'tw':[ 5.47],
       'wt':[ 2.44],
       'tl':[ 5.28],
       'lt':[ 2.05] }
names = {1 : 'W tagging'}
ecols = {1 : ROOT.kCyan+2}
can14,leg14,hs14 = PlotMultiHbarWithLabels('Tab13EventFractionsW', ecols, names, d14, 'Event fractions, W [%]')
stuff.append([can14, leg14, hs14])
ROOT.gPad.Update()
cans.append(can14)

###########################################################################
# needs special care and split
# Table 14
columns15 = [#'File',
             #'Set',
             'Accuracy','Precision','Recall','False positive rate']
d15a = np.array([[1, 91.4 , 86.1 , 100 , 18.4],
                 [2, 94.8 , 86.9 , 99.7 , 7.7],
                 [3, 97.1 , 89.1 , 99.8 , 3.8]])
d15b = np.array([[1, 91.1 , 85.8 , 99.9 , 18.8], 
                 [2, 94.2 , 86.3 , 98.9 , 8.2],
                 [3, 93.8 , 81.8 , 95.2 , 6.7]])
names = {1 : '2 jets', 2 : '3 jets', 3 : '4 jets',}
jcols = {1: ROOT.kMagenta, 2 : ROOT.kMagenta+1, 3:ROOT.kMagenta+2}
can15a,leg15a,hs15a = PlotMultiHbarWithLabelsColumns('Tab14ResultsPerEventTopTrain', jcols, names, columns15, d15a, 'Event train tagging resuts, Top [%]')
ROOT.gPad.Update()
cans.append(can15a)
can15b,leg15b,hs15b = PlotMultiHbarWithLabelsColumns('Tab14ResultsPerEventTopTest', jcols, names, columns15, d15b, 'Event test tagging resuts, Top [%]')
ROOT.gPad.Update()
cans.append(can15b)



###########################################################################
# needs special care and split
# Table 15
columns16 = [#'File',
             #'Set',
             'Accuracy','Precision','Recall','False positive rate']
d16a = np.array([[1, 84 , 81.6 , 85.4 , 17.2],
                 [2, 87.6 , 79.6 , 75.2 , 7.6],
                 [3, 91.6 , 79.2 , 77.1 , 4.9]])
d16b = np.array([[1, 82.9 , 80.8 , 83.9 , 18], 
                 [2, 86.9 , 78.3 , 73.5 , 7.9],
                 [3, 89.6 , 75.2 , 71.1 , 5.8]])
names = {1 : '2 jets', 2 : '3 jets', 3 : '4 jets',}
jcols = {1: ROOT.kCyan, 2 : ROOT.kCyan+1, 3:ROOT.kCyan+2}
can16a,leg16a,hs16a = PlotMultiHbarWithLabelsColumns('Tab15ResultsPerEventWTrain', jcols, names, columns16, d16a, 'Event train tagging resuts, W [%]')
ROOT.gPad.Update()
cans.append(can16a)
can16b,leg16b,hs16b = PlotMultiHbarWithLabelsColumns('Tab15ResultsPerEventWTest', jcols, names, columns16, d16b, 'Event test tagging resuts, W [%]')
ROOT.gPad.Update()
cans.append(can16b)


###########################################################################


###########################################################################
for can in cans:
    can.Print(can.GetName() + '.png')
    can.Print(can.GetName() + '.pdf')
ROOT.gApplication.Run()
###########################################################################

