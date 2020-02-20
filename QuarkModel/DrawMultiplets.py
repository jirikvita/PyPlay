#!/usr/bin/python
# Thu 20 Feb 08:07:46 CET 2020

# jiri kvita (c) 2020

# TODOs: draw thick axes
# draw vectors of d->s etc?

from __future__ import print_function

from qmclasses import *

import ROOT
from math import sqrt, pow, log, exp
import os, sys, getopt

cans = []
stuff = []

##########################################
# https://www.tutorialspoint.com/python/python_command_line_arguments.htm
def main(argv):
    #if len(sys.argv) > 1:
    #  foo = sys.argv[1]

    ### https://www.tutorialspoint.com/python/python_command_line_arguments.htm
    ### https://pymotw.com/2/getopt/
    ### https://docs.python.org/3.1/library/getopt.html
    gBatch = False
    gTag=''
    print(argv[1:])
    try:
        # options that require an argument should be followed by a colon (:).
        opts, args = getopt.getopt(argv[2:], 'hbt:', ['help','batch','tag='])

        print('Got options:')
        print(opts)
        print(args)
    except getopt.GetoptError:
        print('Parsing...')
        print ('Command line argument error!')
        print('{:} [ -h -b --batch -tTag --tag="MyCoolTag"]]'.format(argv[0]))
        sys.exit(2)
    for opt,arg in opts:
        print('Processing command line option {} {}'.format(opt,arg))
        if opt == '-h':
            print('{:} [ -h -b --batch -tTag --tag="MyCoolTag"]'.format(argv[0]))
            sys.exit()
        elif opt in ("-b", "--batch"):
            gBatch = True
        elif opt in ("-t", "--tag"):
            gTag = arg
            print('OK, using user-defined histograms tag for output pngs {:}'.format(gTag,) )

    if gBatch:
        ROOT.gROOT.SetBatch(1)

    ROOT.gStyle.SetOptTitle(0)
    print('*** Settings:')
    print('tag={:}, batch={:}'.format(gTag, gBatch))

    canname = 'qcan'
    qcan = ROOT.TCanvas(canname, canname, 800, 400)
    qcan.Divide(2,1)
    cans.append(qcan)


    qtmp = ROOT.TH2D('qtmp', 'qtmp;I_{3};S', 10, -1, 1, 10, -1.5, 1.5)
    qtmp.SetStats(0)

    ###############################
    # make triplet
    Quarks = {}
    for qq in quarks:
        Quarks[qq] =  cquark(qq,
                             quarks[qq][0], quarks[qq][1], quarks[qq][2], quarks[qq][3],
                             quarks[qq][4], quarks[qq][5], quarks[qq][6] )
    for Qname in Quarks:
        Quarks[Qname].Print()
    # draw triplet
    qcan.cd(1)
    ROOT.gPad.SetGridx(1)
    ROOT.gPad.SetGridy(1)

    qtmp.DrawCopy()
    
    qmarks = []
    for Qname in Quarks:
        Q = Quarks[Qname]
        mark = ROOT.TMarker(Q.GetI3(), Q.GetS(), Q.GetMark())
        mark.SetMarkerColor(Q.GetCol())
        mark.Draw()
        qmarks.append(mark)

    ###############################
    # make antitriplet
    AQuarks = {}
    for qq in aquarks:
        AQuarks[qq] = cquark(qq,
                             aquarks[qq][0], aquarks[qq][1], aquarks[qq][2], aquarks[qq][3],
                             aquarks[qq][4], aquarks[qq][5], aquarks[qq][6] ) 
    for AQname in AQuarks:
        AQuarks[AQname].Print()

    # draw antitriplet
    qcan.cd(2)
    ROOT.gPad.SetGridx(1)
    ROOT.gPad.SetGridy(1)
    
    qtmp.DrawCopy()
    aqmarks = []
    for AQname in AQuarks:
        Q = AQuarks[AQname]
        mark = ROOT.TMarker(Q.GetI3(), Q.GetS(), Q.GetMark())
        mark.SetMarkerColor(Q.GetCol())
        mark.Draw()
        aqmarks.append(mark)
    
    qcan.Update()
    
    mhtmp = ROOT.TH2D('mhtmp', 'mhtmp;I_{3};S', 10, -1.5, 1.5, 10, -1.5, 1.5)
    mhtmp.SetStats(0)
 
  
    
    ###############################
    # make meson octet
    ###############################
    moctet = {}
    moctet['pi+'] = ( chadron('pi+', [ Quarks['u'],   AQuarks['db'] ], '#pi^{+}') )
    moctet['pi-'] = ( chadron('pi-', [ AQuarks['ub'], Quarks['d'] ], '#pi^{-}') )
    moctet['pi0'] = ( chadron('pi0', [ Quarks['u'],   AQuarks['ub'],
                                       Quarks['d'],   AQuarks['db' ]], '#pi^{0}') )

    moctet['K0'] = ( chadron('K0', [ Quarks['d'],   AQuarks['sb'] ], 'K^{0}') )
    moctet['aK0'] = ( chadron('aK0', [ Quarks['s'],   AQuarks['db'] ], '#bar{K}^{0}') )

    moctet['K+'] = ( chadron('K+', [ Quarks['u'],   AQuarks['sb'] ], 'K^{+}') )
    moctet['K-'] = ( chadron('K-', [ Quarks['s'],   AQuarks['ub'] ], 'K^{-}') )
    
    moctet['eta'] = ( chadron('eta', [ AQuarks['sb'],   Quarks['s'] ], '#eta^{0}') )
    
    xoff = -0.15
    yoff = 0.19

    cw = 800
    ch = 800
    
    # draw mezon octet
    canname = 'mesonOctet'
    mcan = ROOT.TCanvas(canname, canname, 0, 0, cw, ch)
    #can.Divide(3,1)
    cans.append(mcan)
    mcan.cd()
    mhtmp.DrawCopy()
    ROOT.gPad.SetGridx(1)
    ROOT.gPad.SetGridy(1)
    mmarks = []
    for bb in moctet:
        B = moctet[bb]
        marks = B.MakeMarks()
        for mark in marks:
            mark.Draw()
        mmarks.append(marks)
        if 'eta' in B.GetName():
            ysign = -1.5
        else: ysign = 1
        tex = ROOT.TLatex(B.GetI3() + xoff, B.GetS() + yoff*ysign, B.GetTexName())
        tex.Draw()
        stuff.append(tex)
    
    # draw meson octet

    ###############################
    # make baryon octet
    ###############################
    
    boctet = {}
    boctet['p'] = ( chadron('proton', [ Quarks['u'], Quarks['u'], Quarks['d'] ], 'p') )
    boctet['n'] = ( chadron('neutron', [ Quarks['u'], Quarks['d'], Quarks['d'] ], 'n') )
    boctet['Sigma-'] = ( chadron('Sigma-', [ Quarks['s'], Quarks['d'], Quarks['d'] ], '#Sigma^{-}') )
    boctet['Sigma0'] = ( chadron('Sigma0', [ Quarks['s'], Quarks['u'], Quarks['d'] ], '#Sigma^{0}') )
    boctet['Sigma+'] = ( chadron('Sigma+', [ Quarks['s'], Quarks['u'], Quarks['u'] ], '#Sigma^{+}') )
    boctet['Lambda0'] = ( chadron('Lambda0', [ Quarks['s'], Quarks['u'], Quarks['d'] ], '#Lambda^{0}') )
    boctet['Xi-'] = ( chadron('Xi-', [ Quarks['s'], Quarks['s'], Quarks['d'] ], '#Xi^{-}') )
    boctet['Xi0'] = ( chadron('Xi0', [ Quarks['s'], Quarks['s'], Quarks['u'] ], '#Xi^{0}') )

    xoff = -0.15
    yoff = 0.19

    ohtmp = ROOT.TH2D('ohtmp', 'ohtmp;I_{3};S', 10, -1.5, 1.5, 10, -2.5, 0.5)
    ohtmp.SetStats(0)

    # draw baryon octet
    canname = 'baryonOctet'
    bcan = ROOT.TCanvas(canname, canname, 400, 200, cw, ch)
    #can.Divide(3,1)
    cans.append(bcan)
    bcan.cd()
    ohtmp.DrawCopy()
    ROOT.gPad.SetGridx(1)
    ROOT.gPad.SetGridy(1)

    bmarks = []
    for bb in boctet:
        B = boctet[bb]
        marks = B.MakeMarks()
        for mark in marks:
            mark.Draw()
        bmarks.append(marks)
        if 'Lambda' in B.GetName():
            ysign = -2.
        else: ysign = 1
        tex = ROOT.TLatex(B.GetI3() + xoff, B.GetS() + yoff*ysign, B.GetTexName())
        tex.Draw()
        stuff.append(tex)

    ###############################
    # make baryon decuplet
    ###############################
    
    bdecuplet = {}
    bdecuplet['Delta++'] = ( chadron('Delta++', [ Quarks['u'], Quarks['u'], Quarks['u'] ], '#Delta^{++}') )
    bdecuplet['Delta+'] = ( chadron('Delta+', [ Quarks['u'], Quarks['u'], Quarks['d'] ], '#Delta^{+}') )
    bdecuplet['Delta0'] = ( chadron('Delta0', [ Quarks['u'], Quarks['d'], Quarks['d'] ], '#Delta^{0}') )
    bdecuplet['Delta-'] = ( chadron('Delta-', [ Quarks['d'], Quarks['d'], Quarks['d'] ], '#Delta^{-}') )
    bdecuplet['Sigma*-'] = ( chadron('Sigma-', [ Quarks['s'], Quarks['d'], Quarks['d'] ], '#Sigma^{-}') )
    bdecuplet['Sigma*0'] = ( chadron('Sigma0', [ Quarks['s'], Quarks['u'], Quarks['d'] ], '#Sigma^{0}') )
    bdecuplet['Sigma*+'] = ( chadron('Sigma+', [ Quarks['s'], Quarks['u'], Quarks['u'] ], '#Sigma^{+}') )
    bdecuplet['Xi*-'] = ( chadron('Xi*-', [ Quarks['s'], Quarks['s'], Quarks['d'] ], '#Xi^{*-}') )
    bdecuplet['Xi*0'] = ( chadron('Xi*0', [ Quarks['s'], Quarks['s'], Quarks['u'] ], '#Xi^{*0}') )
    bdecuplet['Omega-'] = ( chadron('Omega-', [ Quarks['s'], Quarks['s'], Quarks['s'] ], '#Omega^{-}') )

    xoff = -0.15
    yoff = 0.15
    
    # draw baryon decuplet
    canname = 'baryonDecuplet'
    dcan = ROOT.TCanvas(canname, canname, 800, 400, cw, ch)
    #can.Divide(3,1)
    cans.append(dcan)
    dcan.cd()
    dhtmp = ROOT.TH2D('dhtmp', 'dhtmp;I_{3};S', 10, -2., 2., 10, -3.5, 0.5)
    dhtmp.SetStats(0)
    dhtmp.DrawCopy()

    ROOT.gPad.SetGridx(1)
    ROOT.gPad.SetGridy(1)

    dmarks = []
    for bb in bdecuplet:
        B = bdecuplet[bb]
        marks = B.MakeMarks()
        for mark in marks:
            mark.Draw()
        dmarks.append(marks)
        if 'Lambda' in B.GetName():
            ysign = -3
        else: ysign = 1
        tex = ROOT.TLatex(B.GetI3() + xoff, B.GetS() + yoff*ysign, B.GetTexName())
        tex.Draw()
        stuff.append(tex)
        
    # draw baryon decuplet
    stuff.append(bmarks)
    stuff.append(dmarks)
    stuff.append(mmarks)
    #stuff.append()


    ###############################
    ###############################
    ###############################



    for can in cans:
        can.Update()
        can.Print(can.GetName() + '.png')
        can.Print(can.GetName() + '.pdf')
    
    ROOT.gApplication.Run()
    return

###################################
###################################
###################################

if __name__ == "__main__":
    # execute only if run as a script"
    main(sys.argv)
    
###################################
###################################
###################################

