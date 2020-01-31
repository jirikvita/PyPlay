#!/usr/bin/python
# Jiri Kvita 26.1.2020
# Sun 26 Jan 18:44:50 CET 2020

import ROOT
import os, sys, getopt

from classes import *

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


#########################################
def MakeAttractors(world):
    attractors = []
    # some manually placed attractors
    # center:
    sx = (world.GetXmax() + world.GetXmin()) / 2.
    sy = (world.GetYmax() + world.GetYmin()) / 2.
    # halfwidths:
    hwx = (world.GetXmax() - world.GetXmin()) / 2.
    hwy = (world.GetYmax() - world.GetYmin()) / 2.
    rmin = 0.02
    rmax = 10 # exceeds the world radius
    speed = 2 # exceeding factor over random walk speed
    sf = 0.55 # scale factor
    attractors.append(cattractor(sx-sf*hwx, sy-sf*hwy, rmin, rmax, speed))
    attractors.append(cattractor(sx+sf*hwx, sy+sf*hwy, rmin, rmax, speed))
    return attractors

#########################################
def MakeFamily(world, attractors, params, x, y, nAverInFamily):
    family = []
    rand = world.GetRand()
    for im in range(0, rand.Poisson(nAverInFamily)):
        id = world.YieldNewId()
        age = rand.Gaus(35, 15)
        if age < 0:
            age = 1
        # TODO: randomize x, y within family members
        status = gHealthy
        if rand.Uniform(0,1) < params.GetInitialSickFraction():
          status = gSick
        # TODO!
        # randomize attractors for family members!
        randx = rand.Uniform(0., 1.)
        randi = 0
        if randx > 0.5:
            randi = 1
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
    if world.GetAttractorIndex()[0] == 0:
        # go to the attractor
        destX = person.GetAttractors()[0].GetX() # ? world.GetAttractorIndex()[0]
        destY = person.GetAttractors()[0].GetY()
    else:
        # go home
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
                                  mem.SetStatus(gSick)

                  elif mem.GetStatus() == gSick:
                      # and randomly infect
                      if othermem.GetStatus() != gHealthy:
                          # can infect only healty people;-)
                          continue
                      distance = ComputeDistance(mem, othermem)
                      if distance < params.GetSpreadRadius():
                          if rand.Uniform(0,1) < params.GetSpreadFrequency():
                              othermem.SetStatus(gSick)
                  
          # randomly die:
          if rand.Uniform(0,1) < params.GetDieProb():
             mem.SetStatus(gDead)
          # randomly heal:
          if rand.Uniform(0,1) < params.GetHealProb():
             mem.SetStatus(gHealed)

             
          # dead person does not move...
          if mem.GetStatus() != gDead:
            MovePerson(world, family, mem)
          pass
  #world.IncStep()
  return


#########################################
def ShowWorld(world, attractors):
  world.GetCan().Draw()
  for attractor in attractors:
      circ = ROOT.TEllipse(attractor.GetX(), attractor.GetY(), attractor.GetRmin())
      circ.SetLineStyle(2)
      circ.SetLineWidth(4)
      circ.SetLineColor(ROOT.kMagenta)
      circ.Draw()
      stuff.append(circ)
  return stuff

#########################################
def DrawPerson(world, mem):
    world.GetCan().cd()
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
  marks = []
  for family in families:
    for member in family.GetMembers():
      marks.append(DrawPerson(world, member))
  return marks

#########################################
def Draw(world, families, attractors):
    ShowWorld(world, attractors)
    marks = DrawFamilies(world, families)
    sday = MakeDigitStr(world.GetDay(),2)
    sstep = MakeDigitStr(world.GetStep(),2)
    sss = 'day {:} step {:}'.format(sday, sstep)
    txt = ROOT.TLatex(0.02, 0.96, sss)
    txt.SetTextSize(0.03)
    txt.SetNDC()
    txt.SetTextColor(ROOT.kBlue)
    txt.Draw()
    status = world.GetStatusStr(families)
    wtxt = ROOT.TLatex(0.02, 0.02, status)
    wtxt.SetTextSize(0.03)
    wtxt.SetNDC()
    wtxt.SetTextColor(ROOT.kBlue)
    wtxt.Draw()
    
    #stuff.append(txt)
    world.GetCan().Print(world.GetCan().GetName() + '_day{:}_step{:}.png'.format(sday, sstep))
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

    canname = 'world'
    can = ROOT.TCanvas(canname, canname, 0, 0, 800, 800)
    cans.append(can)

    # day, night
    # age, school attractors, work attractors, shopping attractors
    # incubation time
    # spread frequency, radius

    xmin = 0
    xmax = 1
    ymin = 0
    ymax = 1
    randSpeedX = 0.005
    randSpeedY = 0.005
    cols = { gHealthy : ROOT.kBlack,
             gSick : ROOT.kGreen+2,
             gSuperSpreader : ROOT.kGreen + 2,
             gDead : ROOT.kRed,
             gInfected : ROOT.kAzure + 7,
             gHealed : ROOT.kBlack}
    marks = { gHealthy : 20,
              gSick : 21,
              gSuperSpreader : 29,
              gDead : 34,
              gInfected : 20,
              gHealed : 24}
    # attractor indices [0,1] symbolize home and world
    world = cworld(can, 0, 0, xmin, xmax, ymin, ymax, 0, ROOT.TRandom3(), randSpeedX, randSpeedY, cols, marks, [0, 1])

    attractors = MakeAttractors(world)
    

    spreadFrequency = 0.002 # transmission prob. per encounter within radius
    # TODO:
    # define gInfected
    # add ndays sick to cperson!
    # add exponencial die prob!
    # tau = 5
    # add heal probability after some steps
    # tauheal = 
    # TO USE!!!
    incubationTime = 7 # days

    # later: enable mutations, heal from certain stem, but can be infected by a new one
    # pads, histograms, age, die prob. age dependent...
    # also control histos of how long people were infectious, sick, healthy before getting sick
    # allow treatment from some day in some areas?
    # game-like interaction character?;-)
    # initial infection random, but only in certain area
    # attraction indices of work/school based on age? ;-)
    
    # TO USE!!!
    getWellTime = 4
    maxDaysSick = 6

    healProb = 0.0005
    dieProb = 0.0015

    spreadRadius = 0.04 
    superSpreadFraction = 0.01 # out of sick
    initialSickFraction = 0.02
    params = cparams(spreadFrequency, spreadRadius, dieProb, healProb, getWellTime, incubationTime, superSpreadFraction, initialSickFraction, maxDaysSick)

    
    Nfamilies = 500
    nAverInFamily = 3.5
    families = MakeFamilies(world, attractors, params, Nfamilies, nAverInFamily, xmin, xmax, ymin, ymax)

    
    nDays = 4 # 30
    for day in xrange(0, nDays):
        nTimeSteps = 128
        world.SetStep(0)
        for it in xrange(0, nTimeSteps):
            MakeStep(world, families, attractors, params)
            Draw(world, families, attractors)
            world.PrintStatus(families)
            world.IncStep()
        world.IncDay(families)

    ROOT.gApplication.Run()
    print ('DONE!;-)')
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



