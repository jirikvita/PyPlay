#!/usr/bin/python
# Thu 17 Oct 09:24:40 CEST 2019

import ROOT

from math import sqrt, pow, log, exp, pi
import os, sys, getopt

cans = []
stuff = []

mparticlec2 = 0.511 # MeV
hc = 197 # MeV * fm
c = 3e8 # fm/fs ;-)
sf = 1.e6 # fm
addsf = 1e-6
    
##########################################
def MakeZeros(i):
    tag = ''
    for i in range(0, i):
        tag = tag + '0'
    return tag
##########################################
def MakeNumTag(i, n):
    tag = str(i)
    order = int(log(n, 10))
    if i == 0: tag = MakeZeros(order+1)
    else:
        orderi = int(log(i, 10))
        tag = MakeZeros(order - orderi) + tag
    return tag

##########################################
def MakeAndDraw2DRho(name, X, pars, npx = 150, npy = 150):
    xmin = X[0][0]
    xmax = X[0][1]
    ymin = X[1][0]
    ymax = X[1][1]
    fun2d = ROOT.TF2(name, "([0]*sin([1]*x)*sin([2]*y))^2 + ([3]*sin([4]*x)*sin([5]*y))^2 + 2*[0]*[3]*sin([1]*x)*sin([2]*y)*sin([4]*x)*sin([5]*y)*cos([7]*[8] - [6]) ", xmin, xmax, ymin, ymax)
    
    i = 0
    for par in pars:
        if i != 0 and i != 3 and i!=6:
            fun2d.SetParameter(i, par*pi / (X[i % 2][1] - X[i % 2][0]))
        else:
            fun2d.SetParameter(i, par)
        i = i+1

    # set the omega
    # omega = DeltaE/h = hc / (2mc^2) * c * ((n1^1-n'1^2)/a1^2 + (n2^1-n'2^2)/a2^2)
    #print( pars )
    fun2d.SetParameter(7, c*hc*pow(pi,2) / (2*mparticlec2) *  ( (pow(pars[1],2) - pow(pars[4],2))/pow(xmax - xmin, 2)*pow(addsf,2) + (pow(pars[2],2) - pow(pars[5],2))/pow(ymax - ymin, 2)*pow(addsf,2) ) )   

    fun2d.SetNpx(npx)
    fun2d.SetNpy(npy)

    stuff.append(fun2d)
    return fun2d

##########################################

# https://www.tutorialspoint.com/python/python_command_line_arguments.htm
def main(argv):
    #if len(sys.argv) > 1:
    #  foo = sys.argv[1]

    ### https://www.tutorialspoint.com/python/python_command_line_arguments.htm
    ### https://pymotw.com/2/getopt/
    ### https://docs.python.org/3.1/library/getopt.html


    ROOT.gStyle.SetOptTitle(0)

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

    print('*** Settings:')
    print('tag={:}, batch={:}'.format(gTag, gBatch))

    canname = 'InfWell2Danim'
    ww = 800
    can = ROOT.TCanvas(canname, canname, 0, 0, ww, ww)
    cans.append(can)
    #filename = 'foo.root'
    #rfile = ROOT.TFile(filename, 'read')
    #hname = 'histo_h'
    #h1 = rfile.Get('hname')

    # 2D function
    X = [ [0., addsf*sf*1.], [0., addsf*sf*1.]]
    # alfa, n1, n2, beta, n1, n2, delta
    Pars = [1./sqrt(2.), 2, 1,  1./sqrt(2.), 3, 4, 0.]
    #Pars = [1./sqrt(2.), 2, 1,  1./sqrt(2.), 4, 3, 0.]
    #Pars = [1./sqrt(2.), 2, 1,  1./sqrt(2.), 4, 2, 0.]
    #Pars = [1./sqrt(2.), 3, 2,  1./sqrt(2.), 4, 5, 0.]
    #Pars = [1./sqrt(2.), 5, 7,  1./sqrt(2.), 8, 12, 0.]
    j = 0
    #can.Divide(3,3)
    # steps in time:
    nsteps  = 200
    time0 = 0.
    time1 = 3. # fs
    tstep = (time1 - time0) / nsteps
    fun2d = MakeAndDraw2DRho('Infinite square well non-stationary #rho(x,y,t)'.format(j), X, Pars)
    for it in range(0, nsteps):
        ftime = time0 + it*tstep
        fun2d.SetParameter(8, ftime)
        #can.cd(it+1)
        fun2d.Draw("col")
        fun2d.GetXaxis().SetTitle('x [nm]')
        fun2d.GetYaxis().SetTitle('y [nm]')
        fun2d.GetZaxis().SetTitle('#rho(x,y,t)')

        #fun2d.DrawCopy("col")
        txt = ROOT.TLatex(0.06, 0.93, fun2d.GetName() + ', m={:1.3f} MeV, t={:3.2f} fs'.format(mparticlec2, ftime))
        txt.SetTextSize(0.030)
        txt.SetNDC()
        stuff.append(txt)
        txt.Draw()
        #print( MakeNumTag(it, nsteps))
        can.Print(can.GetName() + MakeNumTag(it, nsteps) + '.gif')
    
    
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

