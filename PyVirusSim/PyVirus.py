#!/usr/bin/python3

# c.f. https://www.washingtonpost.com/graphics/2020/world/corona-simulator/

# https://stackoverflow.com/questions/50311406/how-to-draw-a-random-sample-from-a-poisson-distribution
import numpy as np

# Jiri Kvita 26.1.2020
# Sun 26 Jan 18:44:50 CET 2020

import os, sys, getopt

import random

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
        histo = [name, title, {}]
        histos[str(key)] = histo

        # histograms of overall numbers as function of iteration!
        name = 'h_{:}_vs_nIter'.format(gKeyNames[key])
        title = ';;people'
        histo = [name, title, {}]
        histos[MakeIterHkey(key)] = histo

    #for key in gKeys:
    #    histo = histos[str(key)]
    #    for key2 in gKeys:
    #        print('Setting bin {:} label to {:}'.format(key2+1, gKeyNames[key2]))
    #        #histo.GetXaxis().SetBinLabel(key2+1, gKeyNames[key2])
    name = 'h_age'
    title = ';age;people'
    n = 40
    histo = [name, title, [] ]
    histos['age'] = histo
    return histos
    
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
    rmin = 0.02*gkm
    rmax = 10*gkm # exceeds the world radius, attractor works for all practical distances
    speed = 2 # exceeding factor over random walk speed
    sf = 0.55 # scale factor
    attractors.append(cattractor(sx-sf*hwx, sy-sf*hwy, rmin, rmax, speed))
    attractors.append(cattractor(sx+sf*hwx, sy+sf*hwy, rmin, rmax, speed))
    return attractors

#########################################
def MakeFamily(world, attractors, params, x, y, nAverInFamily):
    family = []
    rand = world.GetRand()
    for im in range(0, int(0.5 + np.random.poisson(nAverInFamily, 2)[0]) ):
        id = world.YieldNewId()
        age = -1
        while age <= 0:
            age = rand.gauss(35, 15)
        if age > params.GetMaxAge():
            age = params.GetMaxAge()
        # TODO: randomize x, y within family members
        status = gHealthy
        if rand.uniform(0,1) < params.GetInitialSickFraction():
          status = gInfected
        # TODO!
        # randomize attractors for family members!
        randx = rand.uniform(0,1)
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
    x = rand.uniform(world.GetXmin(), world.GetXmax())
    y = rand.uniform(world.GetYmin(), world.GetYmax())
    return x,y

#########################################    
def MakeFamilies(world, attractors, params, Nfamilies, nAverInFamily, xmin, xmax, ymin, ymax):
    families = []
    for i in range(0, Nfamilies):
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
    x = person.GetX() + rand.uniform(-world.GetRandSpeedX(), world.GetRandSpeedX())
    y = person.GetY() + rand.uniform(-world.GetRandSpeedY(), world.GetRandSpeedY())

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
          # actually, make a triangular search (compute indices or rather use range?) and check both options;)
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
                              if rand.uniform(0,1) < params.GetSpreadFrequency():
                                  mem.SetStatus(gInfected)

                  elif mem.GetStatus() == gSick:
                      # and randomly infect
                      if othermem.GetStatus() == gHealthy:
                          # can infect only healthy people;-)
                          distance = ComputeDistance(mem, othermem)
                          if distance < params.GetSpreadRadius():
                              if rand.uniform(0,1) < params.GetSpreadFrequency():
                                  othermem.SetStatus(gInfected)
                  
                      # try randomly die:
                      if rand.uniform(0,1) < params.GetDeathProb()*(1. + params.GetAgeDeathFact()*mem.GetAge()/params.GetMaxAge()):
                          mem.SetStatus(gDead)
                          # try randomly heal:
                      elif rand.uniform(0,1) < params.GetHealProb():
                          mem.SetStatus(gHealed)

                  elif mem.GetStatus() == gInfected:
                      # randomly get sick from infected
                      tau = params.GetIncubationTime()
                      # TO FINISH!!! NO, KEEP the SICK turning probability as below;-)
                      #if rand.uniform(0,1) > 1./tau*exp(-world.GetDay() / tau):
                      if rand.uniform(0,1) < 0.00001:
                          mem.SetStatus(gSick)

             
             
          # dead person does not move...
          if mem.GetStatus() != gDead:
            MovePerson(world, family, mem)
          pass
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

    print('*** Settings:')
    print('tag={:}, batch={:}'.format(gTag, gBatch))


    ############
    # Settings #
    ############

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

    nDays = 6 # 30
    nTimeSteps = 172
    nTotIters = nDays*nTimeSteps
    histos = MakeHistos(nTotIters)

    # dummy canvas
    can = []
    # attractor indices [0,1] symbolize home and world
    world = cworld(can, histos, 0, 0, xmin, xmax, ymin, ymax, 0, random, randSpeedX, randSpeedY, gCols, gMarks, [0, 1])

    attractors = MakeAttractors(world)

    # TODO:
    # define gInfected
    # add ndays sick to cperson!
    # add exponencial death prob!
    # tau = 5
    # add heal probability after some steps
    # tauheal =

    # TODOS:
    # watch ages histos of each category and plot them, too
    # keep and the write and plot some summaries
    # like numbers of all the categories in each day and step!
    # write this also to a file for further analysis and plotting;-)
    # TO FINISH the exp. distribution
    # make some people immune?
    # FINISH the super spreaders
    # mark by lines also initial and current mean age
    
    # later: enable mutations, heal from certain stem, but can be infected by a new one
    # pads, histograms, age, death prob. age dependent...
    # also control histos of how long people were infectious, sick, healthy before getting sick
    
    # allow treatment from some day in some areas?
    #    -- increase heal prob. close to some hospital attractor
    #   -- send a fraction of people to such attractor
    
    # click and game-like interaction character?;-)
    # initial infection random, but only in certain area
    # attraction indices of work/school based on age? ;-)
    # make also the heal prob. age dependent?
    # create functions for these!
    
    # TO USE!!!
    # exp() param
    getWellTime = 2
    maxDaysSick = 4

    incubationTime = 1002 # days

    healProb  = 0.0000005
    deathProb = 0.00000065 # per step

    spreadFrequency = 0.015 # transmission prob. per encounter within radius
    spreadRadius = 0.025*gkm
    superSpreadFraction = 0.01 # out of sick
    initialSickFraction = 0.05
    ageDeathFact = 0.3

    # affect people speed by age?
    
    params = cparams(spreadFrequency, spreadRadius, deathProb, healProb, getWellTime, incubationTime, superSpreadFraction, initialSickFraction, maxDaysSick, ageDeathFact, gmaxAge)

    Nfamilies = 500
    nAverInFamily = 3.5
    families = MakeFamilies(world, attractors, params, Nfamilies, nAverInFamily, xmin, xmax, ymin, ymax)


    #########
    # LOOP! #
    #########
    nPeople = CountPeople(families)
    
    for day in range(0, nDays):
        world.SetStep(0)
        for it in range(0, nTimeSteps):
            world.FillHistos(families)
            world.PrintStatus(families)
            MakeStep(world, families, attractors, params)
            world.IncStep()
        world.IncDay(families)

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



