#!/usr/bin/python
# Jiri Kvita 26.1.2020
# Sun 26 Jan 18:44:50 CET 2020
# updates Jan-March 2020

import ROOT
import os, sys, getopt

from classes import *
from Tools import *


#########################################
def MakeHistos(nTotIters):
    histos = {}
    # prepare hsitograms of different color
    # where each will have only one non-zero bin filled with the number of people in each category
    # need also to add the age histo! TODO
    n = len(gKeys)
    for key in gKeys:
        # histograms of overall numbers
        name = 'h_{:}'.format(gKeyNames[key])
        title = ';;people'
        histo = ROOT.TH1D(name, title, n, 0, n)
        histo.SetFillColor(gCols[key])
        histo.SetStats(0)
        histos[str(key)] = histo

        # histograms of overall numbers as function of iteration!
        name = 'h_{:}_vs_nIter'.format(gKeyNames[key])
        title = ';;people'
        histo = ROOT.TH1D(name, title, nTotIters, 0, nTotIters)
        histo.SetLineColor(gCols[key])
        histo.SetMarkerColor(gCols[key])
        histo.SetMarkerStyle(24)
        histo.SetMarkerSize(0.5)
        histo.SetLineWidth(2)
        histo.SetStats(0)
        histos[MakeIterHkey(key)] = histo

    for key in gKeys:
        histo = histos[str(key)]
        for key2 in gKeys:
            print('Setting bin {:} label to {:}'.format(key2+1, gKeyNames[key2]))
            histo.GetXaxis().SetBinLabel(key2+1, gKeyNames[key2])
    name = 'h_age'
    title = ';age;people'
    n = 25
    histo = ROOT.TH1D(name, title, n, 0, gmaxAge)
    histo.SetFillColor(gCols[key])
    histo.SetFillColor(ROOT.kBlue)
    histo.SetStats(0)
    histos['age'] = histo
    return histos
    
#########################################
def MakeAttractors(world, speed):
    attractors = []
    # some manually placed attractors
    # center:
    sx = (world.GetXmax() + world.GetXmin()) / 2.
    sy = (world.GetYmax() + world.GetYmin()) / 2.
    # halfwidths:
    hwx = (world.GetXmax() - world.GetXmin()) / 2.
    hwy = (world.GetYmax() - world.GetYmin()) / 2.
    rmin = 0.02*gkm
    rmax = 10*gkm # exceeds the world radius, attractor works for all practical distances
    sf = 0.55 # scale factor
    attractors.append(cattractor(sx-sf*hwx, sy-sf*hwy, rmin, rmax, speed))
    attractors.append(cattractor(sx+sf*hwx, sy+sf*hwy, rmin, rmax, speed))
    attractors.append(cattractor(sx+sf*hwx, sy-sf*hwy, rmin, rmax, speed))
    attractors.append(cattractor(sx-sf*hwx, sy+sf*hwy, rmin, rmax, speed))
    return attractors

#########################################
def MakeFamily(world, attractors, params, x, y, nAverInFamily):
    family = []
    rand = world.GetRand()
    for im in range(0, rand.Poisson(nAverInFamily)):
        id = world.YieldNewId()
        age = -1
        while age <= 0:
            age = rand.Gaus(35, 15)
        if age > params.GetMaxAge():
            age = params.GetMaxAge()
        # TODO: randomize x, y within family members
        status = gHealthy
        if rand.Uniform(0,1) < params.GetInitialSickFraction():
          status = gInfected
          if rand.Uniform(0,1) < params.GetSuperSpreadFraction():
              status = gSuperSpreader
        # TODO!
        # randomize attractors for family members!
        randx = rand.Uniform(0., len(attractors)-1)
        randi = int(round(randx))
        # so far support only one attractor per person in a list
        family.append(cperson(id, age, x, y, [attractors[randi]], status, 0, 0, 0))
    Family = cfamily(family, x, y)
    return Family

#########################################
def MakeRandomXY(world):
    rand = world.GetRand()
    x = rand.Uniform(world.GetXmin(), world.GetXmax())
    y = rand.Uniform(world.GetYmin(), world.GetYmax())
    return x,y

#########################################    
def MakeFamilies(world, attractors, params, Nfamilies, nAverInFamily, xmin, xmax, ymin, ymax):
    families = []
    for i in xrange(0, Nfamilies):
        x,y = MakeRandomXY(world)
        Family = MakeFamily(world, attractors, params, x, y, nAverInFamily)
        families.append(Family)
    return families

#########################################
def EnsureIndividual(x, xmin, xmax):
  if x < xmin: x = xmin
  if x > xmax: x = xmax
  return

#########################################
def EnsureReality(world, x, y):
  EnsureIndividual(x, world.GetXmin(), world.GetXmax())
  EnsureIndividual(y, world.GetYmin(), world.GetYmax())
  return

#########################################
def MovePerson(world, family, person):
    # random move
    rand = world.GetRand()
    x = person.GetX() + rand.Uniform(-world.GetRandSpeedX(), world.GetRandSpeedX())
    y = person.GetY() + rand.Uniform(-world.GetRandSpeedY(), world.GetRandSpeedY())

    # move to the current attractor
    # get the destintion coordinates and compute vector to move along
    destX = 0
    destY = 0
    # move to an attractor, but quaranteened people go and stay home!
    if world.GetAttractorIndex()[0] == 0 and person.GetStatus() != gQuarantine:
        # go to the attractor
        destX = person.GetAttractors()[0].GetX() # ? world.GetAttractorIndex()[0]
        destY = person.GetAttractors()[0].GetY()
    else:
        # go home, these are family coordinates
        destX = family.GetX0()
        destY = family.GetY0()
    vect = [destX - x, destY - y]
    # check whether in effective radious of the attractor
    speed = 0
    r2 = pow(vect[0], 2) + pow(vect[1], 2)
    if world.GetAttractorIndex()[0] == 0:
        if r2 < pow(person.GetAttractors()[0].GetRmax(), 2)\
           and r2 > pow(person.GetAttractors()[0].GetRmin(), 2):
             speed =  person.GetAttractors()[0].GetStrength()
        else:
            speed = 0
    else:
        speed = 1
    x = x + vect[0]*world.GetRandSpeedX()*speed
    y = y + vect[1]*world.GetRandSpeedY()*speed
    EnsureReality(world, x,y)
    person.SetXY(x,y)
    return

#########################################
def MakeStep(world, families, attractors, params):
  rand = world.GetRand()
  for family in families:
        for mem in family.GetMembers():
          # reverse the search, and for many sick people search around the healthy ones for sick!
          # actually, make a triangular search (compute indices or rather use xrange?) and check both options;)
          for otherfam in families:
              for othermem in otherfam.GetMembers():
                  # rely on the ordering!
                  if othermem.GetId() >= mem.GetId():
                      # can't interact with oneself;-)
                      # avoid double checks
                      continue
                  if mem.GetStatus() == gHealthy:
                      if othermem.GetStatus() == gSick:
                          distance = ComputeDistance(mem, othermem)
                          if distance < params.GetSpreadRadius():
                              if rand.Uniform(0,1) < params.GetSpreadFrequency():
                                  mem.SetStatus(gInfected)

                  elif mem.GetStatus() == gSick or mem.GetStatus() == gSuperSpreader:
                      # and randomly infect, but only wen not in quarantene!
                      if mem.GetStatus != gQuarantine and othermem.GetStatus() == gHealthy:
                          # can infect only healthy people;-)
                          distance = ComputeDistance(mem, othermem)
                          if distance < params.GetSpreadRadius():
                              if rand.Uniform(0,1) < params.GetSpreadFrequency():
                                  othermem.SetStatus(gInfected)
                  
                      refAge = 40.
                      ageDeathFact = params.GetAgeDeathFact().Eval(mem.GetAge()) / params.GetAgeDeathFact().Eval(refAge)
                      if mem.GetStatus() != gSuperSpreader:
                          if rand.Uniform(0,1) < params.GetDeathProb()*ageDeathFact:
                              mem.SetStatus(gDead)
                              # try randomly heal:
                          elif rand.Uniform(0,1) < params.GetHealProb():
                              mem.SetStatus(gHealed)

                  elif mem.GetStatus() == gInfected and mem.GetStatus() != gSuperSpreader:
                      # turn sick from infected
                      if rand.Uniform(0,1) < params.GetSickTurnProb():
                          mem.SetStatus(gSick)

             
             
          # dead person does not move...
          if mem.GetStatus() != gDead:
            MovePerson(world, family, mem)
          pass
  return


#########################################
def ShowWorld(world, attractors, nPeople):
  world.GetCan()[0].Draw()
  world.GetCan()[1].cd()
  for attractor in attractors:
      # scaling to NDC?
      circ = ROOT.TEllipse(attractor.GetX(), attractor.GetY(), attractor.GetRmin())
      circ.SetLineStyle(2)
      circ.SetLineWidth(4)
      circ.SetLineColor(ROOT.kMagenta)
      circ.Draw()
      stuff.append(circ)
  # draw age
  world.GetCan()[2][0].cd()
  #ROOT.gPad.SetLogy(1)
  if world.GetDay() == 0 and world.GetStep() == 0:
      Age_h = world.GetHistos()['age']
      cloneAge_h = Age_h.Clone('age_h_initial')
      cloneAge_h.SetLineColor(Age_h.GetFillColor())
      cloneAge_h.SetFillColor(0)
      cloneAge_h.SetFillStyle(0)
      print('Initial age mean: {:}'.format(cloneAge_h.GetMean()))
      world.GetHistos()['iage'] = cloneAge_h
  #world.GetHistos()['iage'].SetMinimum(1.)
  world.GetHistos()['iage'].Draw('hist')
  world.GetHistos()['age'].Draw('histsame')
  
  # draw counts
  world.GetCan()[2][2].cd()
  sameopt = ''
  for key in world.GetHistos():
      if key == 'age' or key == 'iage':
          continue
      if 'Iter' in key:
          pass
      else:
          histo = world.GetHistos()[key]
          histo.Draw('hbar' + sameopt)
          sameopt = 'same'


  # draw counts as function of nIter
  world.GetCan()[2][1].cd()
  sameopt = ''
  for key in world.GetHistos():
      if key == 'age' or key == 'iage':
          continue
      try:
          if 'Iter' in key:
              #hkey = MakeIterHkey(key)
              histo = world.GetHistos()[key]
              #print('Drawing {}'.format(key))
              histo.SetMinimum(1.)
              histo.SetMaximum(nPeople)
              #print(histo.GetBinContent(1))
              histo.Draw('P' + sameopt)
              sameopt = 'same'
              ROOT.gPad.SetLogy(1)
      except:
          pass

  return stuff

#########################################
def DrawPerson(world, mem):
    world.GetCan()[1].cd()
    # scaling to NDC?
    mark = ROOT.TMarker(mem.GetX(), mem.GetY(), world.GetMarks()[mem.GetStatus()])
    
    # add marker into cperson, and create it only for day and step 0
    # do not create it every time!

    mark.SetNDC()
    mark.SetMarkerColor(world.GetCols()[mem.GetStatus()])
    mark.SetMarkerSize(0.5)
    if mem.GetStatus() == gDead:
      mark.SetMarkerSize(1.)
    mark.Draw()
    #print('drawing member {:},{:}'.format(mem.GetX(), mem.GetY()))
    return mark

#########################################
def DrawFamilies(world, families):
  markers = []
  for family in families:
    for member in family.GetMembers():
      markers.append(DrawPerson(world, member))
  return markers

#########################################
def Draw(world, families, attractors, nPeople, tag):

    ShowWorld(world, attractors, nPeople)

    # hm, memory grow...?
    markers = DrawFamilies(world, families)
    
    sday = MakeDigitStr(world.GetDay(),2)
    sstep = MakeDigitStr(world.GetStep(),2)
    sss = 'day {:} step {:}'.format(sday, sstep)
    
    world.GetCan()[2][2].cd()
    txt = ROOT.TLatex(0.12, 0.92, sss)
    txt.SetTextSize(0.10)
    txt.SetNDC()
    txt.SetTextColor(ROOT.kBlue)
    txt.Draw()

    #status = world.GetStatusStr(families)
    #wtxt = ROOT.TLatex(0.02, 0.02, status)
    #wtxt.SetTextSize(0.03)
    #wtxt.SetNDC()
    #wtxt.SetTextColor(ROOT.kBlue)
    #wtxt.Draw()
    
    #stuff.append(txt)
    world.GetCan()[0].Print(world.GetCan()[0].GetName() + '_day{:}_step{:}{:}.png'.format(sday, sstep, tag))
    
    return

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

    print('*** Settings:')
    print('tag={:}, batch={:}'.format(gTag, gBatch))


    ############
    # Settings #
    ############

    canname = 'world'
    canc = ROOT.TCanvas(canname, canname, 0, 0, 800, 600)
    mainPad,pads = MakePads(canc)
    can = [canc, mainPad, pads]
    cans.append(can)

    # day, night
    # age, school attractors, work attractors, shopping attractors
    # incubation time
    # spread frequency, radius

    xmin = 0.*gkm
    xmax = 1.*gkm
    ymin = 0.*gkm
    ymax = 1.*gkm
    randSpeedX = 0.005*gkm
    randSpeedY = 0.005*gkm

    nDays = 30 # 6; 30
    nTimeSteps = 50 # 172
    nTotIters = nDays*nTimeSteps
    histos = MakeHistos(nTotIters)
    
    # attractor indices [0,1] symbolize home and world
    world = cworld(can, histos, 0, 0, xmin, xmax, ymin, ymax, 0, ROOT.TRandom3(), randSpeedX, randSpeedY, gCols, gMarks, [0, 1])

    speed = 6 # 2 exceeding factor over random walk speed
    attractors = MakeAttractors(world, speed)

    # TODO:
    # define gInfected
    # add ndays sick to cperson!
    # add exponencial death prob!

    # TODOS:
    # watch ages histos of each category and plot them, too
    # keep and the write and plot some summaries
    # like numbers of all the categories in each day and step!
    # write this also to a file for further analysis and plotting;-)
    # make some people immune?
    # FINISH the super spreaders
    # mark by lines also initial and current mean age
    
    # later: enable mutations, heal from certain stem, but can be infected by a new one
    # pads, histograms, age, death prob. age dependent...
    # death prob below age:

    # TODOs
    # enable septums

    # TESTING:
    # current quarantene model makes sick people not to ifect other by a status
    # they are also forced go and stay home, but they do not infect already on the way home
    # and when home; we do still allow some fraction of people who break it and move around
    
    # enable veils to decrease transmissionProb
    
    acan, gr_ageDeathFact, fit_ageDeathFact = MakeAgeDeathFact()
    stuff.append([acan, gr_ageDeathFact, fit_ageDeathFact])
    
    # also control histos of how long people were infectious, sick, healthy before getting sick
    
    # allow treatment from some day in some areas?
    #    -- increase heal prob. close to some hospital attractor
    #   -- send a fraction of people to such attractor
    
    # click and game-like interaction character?;-)
    # initial infection random, but only in certain area
    # attraction indices of work/school based on age? ;-)
    # make also the heal prob. age dependent?
    # create functions for these!
    
    # TO USE?
    # maxDaysSick = 4

    # probs per step
    # tragic scenario parameters, Jan-Feb-March 2020
    #sickTurnProb = 0.00001
    #healProb     = 0.0000005
    #deathProb    = 0.00000065

    # probs per step
    sickTurnProb = 0.00001
    healProb     = 0.000008
    deathProb    = 0.000003 # per step

    transmissionProb = 0.015 # transmission prob. per encounter within radius
    spreadRadius = 0.020*gkm # 0.025
    initialSickFraction = 0.05
    superSpreadFraction = 0.10 # out of sick TO USE!
    
    params = cparams(transmissionProb, spreadRadius, deathProb, healProb, sickTurnProb,
                     superSpreadFraction, initialSickFraction, 
                     fit_ageDeathFact, gmaxAge)

    #tag = '_SuperSpreadAndQuaranteen'
    tag = '_SuperSpreadNoQuaranteen'
    params.PrintParamsToFile(tag)
    Nfamilies = 300    # 500
    nAverInFamily = 3. # 3.5
    families = MakeFamilies(world, attractors, params, Nfamilies, nAverInFamily, xmin, xmax, ymin, ymax)


    #########
    # LOOP! #
    #########
    nPeople = CountPeople(families)

    # to move to params:
    quarantineDay = 1 # nDays / 3
    qfrac = 0.8
    
    for day in xrange(0, nDays):
        world.SetStep(0)
        ###!!!if day >= quarantineDay:
        ###!!!    ApplyQuarantine(families, world.GetRand(), qfrac)
        for it in xrange(0, nTimeSteps):
            world.FillHistos(families)
            Draw(world, families, attractors, nPeople, tag)
            world.PrintStatus(families)
            MakeStep(world, families, attractors, params)
            world.IncStep()
        world.IncDay(families)

    print ('DONE!;-)')
    ROOT.gApplication.Run()

    return
#########################################
#########################################
#########################################



###################################
###################################
###################################

if __name__ == "__main__":
    # execute only if run as a script"
    main(sys.argv)
    
###################################
###################################
###################################



