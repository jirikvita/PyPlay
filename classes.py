#!/usr/bin/python
# jiri kvita 2020

import ROOT

from math import sqrt, pow, log, exp, log10

# indices for dict.'s
gHealthy = 0
gInfected = 1
gSick = 2
gSuperSpreader = 3
gDead = 4
gHealed = 5

gmaxAge = 100

gCols = { gHealthy : ROOT.kBlack,
         gSick : ROOT.kGreen+2,
         gSuperSpreader : ROOT.kGreen + 2,
         gDead : ROOT.kRed,
         gInfected : ROOT.kAzure + 7,
         gHealed : ROOT.kBlack}
gMarks = { gHealthy : 20,
          gSick : 21,
          gSuperSpreader : 29,
          gDead : 34,
          gInfected : 20,
          gHealed : 24}

gKeys = [gHealthy, gInfected, gSick, gSuperSpreader, gDead, gHealed]
gKeyNames = { gHealthy : 'healthy', gInfected : 'infected', gSick : 'sick', gSuperSpreader : 'super-spreaders', gDead : 'dead', gHealed : 'healed'}

#########################################

def Count(families, status):
    n = 0
    for fam in families:
        for mem in fam.GetMembers():
            if mem.GetStatus() == status:
                n = n+1
    return n

#########################################
def GetWorldStatus(families):      
    status = {}
    for key in gKeys:
        status[key] = Count(families, key)
    return status

#########################################

class cfamily:
  # code generated by PrintGettersAndSetters.py
  def __init__(self, members, x0, y0):
    self._members = members
    self._x0 = x0
    self._y0 = y0

  def GetMembers(self): return self._members
  def GetX0(self): return self._x0
  def GetY0(self): return self._y0

  def SetMembers(self, members): self._members = members
  def SetX0(self, x0): self._x0 = x0
  def SetY0(self, y0): self._y0 = y0

#########################################

class cworld:
  # code generated by PrintGettersAndSetters.py
  def __init__(self, can, histos, day, step, xmin, xmax, ymin, ymax, nPeople, rand, randSpeedX, randSpeedY, cols, marks, attractorIndex):
    self._can = can
    self._histos = histos
    self._day = day
    self._step = step
    self._xmin = xmin
    self._xmax = xmax
    self._ymin = ymin
    self._ymax = ymax
    self._nPeople = nPeople
    self._rand = rand
    self._randSpeedX = randSpeedX
    self._randSpeedY = randSpeedY
    self._cols = cols
    self._marks = marks
    self._attractorIndex = attractorIndex

  def GetCan(self): return self._can
  def GetHistos(self): return self._histos
  def GetDay(self): return self._day
  def GetStep(self): return self._step
  def GetXmin(self): return self._xmin
  def GetXmax(self): return self._xmax
  def GetYmin(self): return self._ymin
  def GetYmax(self): return self._ymax
  def GetNPeople(self): return self._nPeople
  def GetRand(self): return self._rand
  def GetRandSpeedX(self): return self._randSpeedX
  def GetRandSpeedY(self): return self._randSpeedY
  def GetCols(self): return self._cols
  def GetMarks(self): return self._marks
  def GetAttractorIndex(self): return self._attractorIndex

  def SetCan(self, can): self._can = can
  def SetHistos(self, histos): self._histos = histos
  def SetDay(self, day): self._day = day
  def SetStep(self, step): self._step = step
  def SetXmin(self, xmin): self._xmin = xmin
  def SetXmax(self, xmax): self._xmax = xmax
  def SetYmin(self, ymin): self._ymin = ymin
  def SetYmax(self, ymax): self._ymax = ymax
  def SetNPeople(self, nPeople): self._nPeople = nPeople
  def SetRand(self, rand): self._rand = rand
  def SetRandSpeedX(self, randSpeedX): self._randSpeedX = randSpeedX
  def SetRandSpeedY(self, randSpeedY): self._randSpeedY = randSpeedY
  def SetCols(self, cols): self._cols = cols
  def SetMarks(self, marks): self._marks = marks
  def SetAttractorIndex(self, attractorIndex): self._attractorIndex = attractorIndex

  # manual:
  def YieldNewId(self):
      self._nPeople = self._nPeople + 1
      return self._nPeople
  def IncDay(self, families):
      # new day! time for some changes!
      self._day = self._day + 1
      # inc people's days in status
      for family in families:
          for mem in family.GetMembers():
              mem.SetNDaysInStatus(mem.GetNDaysInStatus()+1)
      # swap home and school/work attraction indices
      # every family member returns home;-)
      self._attractorIndex[1],self._attractorIndex[0] = self._attractorIndex[0],self._attractorIndex[1]
  def IncStep(self):
      self._step = self._step + 1

  def GetStatusStr(self, families):
      status = GetWorldStatus(families)
      nh = status[gHealthy]
      ns = status[gSick] 
      nss = status[gSuperSpreader]
      nd = status[gDead]
      sstr = ''
      for key in gKeys:
          sstr = sstr + '{:}: {:} '.format(gKeyNames[key], status[key])
      return sstr

  def PrintStatus(self, families):
      sstr = self.GetStatusStr(families)
      print('day {} step {} '.format(self._day, self._step,) + sstr)

  def FillHistos(self, families):
      ##setMax = False
      #for key in self._histos:
      #    val = self._histos[key].GetMaximum()
      #    if val > ymax:
      #        ymax = val
      #if self._histos['age'].GetEntries() > 0:
      #    ageMax = self._histos['age'].GetMaximum()
      #    setMax = True
      for key in self._histos:
          if key == 'iage': continue
          self._histos[key].Reset()
      counts = {}
      for key in self._histos:
          counts[key] = 0
      for family in families:
          for mem in family.GetMembers():
              key = mem.GetStatus()
              counts[key] = counts[key] + 1
              if key != gDead:
                  self._histos['age'].Fill(mem.GetAge())
      for ikey in gKeys:
          #print('ikey={}'.format(ikey))
          #self._histos[key].Fill(key, counts[key])
          for hkey in self._histos:
              #print('hkey={}'.format(hkey))
              if ikey == hkey:
                  self._histos[hkey].SetBinContent(ikey+1, counts[hkey])
      #if setMax:
      #    self._histos['age'].SetMaximum(ageMax)
      ymax = self._nPeople
      for key in self._histos:
         if key == 'age' or key == 'iage':
             continue
         self._histos[key].SetMaximum(ymax)

  #########################################
class cparams:
  # code generated by PrintGettersAndSetters.py
  def __init__(self, spreadFrequency, spreadRadius, deathProb, healProb, getWellTime, incubationTime, superSpreadFraction, initialSickFraction, maxDaysSick, ageDeathFact, maxAge):
    self._spreadFrequency = spreadFrequency
    self._spreadRadius = spreadRadius
    self._deathProb = deathProb
    self._healProb = healProb
    self._getWellTime = getWellTime
    self._incubationTime = incubationTime
    self._superSpreadFraction = superSpreadFraction
    self._initialSickFraction = initialSickFraction
    self._maxDaysSick = maxDaysSick
    self._ageDeathFact = ageDeathFact
    self._maxAge = maxAge

  def GetSpreadFrequency(self): return self._spreadFrequency
  def GetSpreadRadius(self): return self._spreadRadius
  def GetDeathProb(self): return self._deathProb
  def GetHealProb(self): return self._healProb
  def GetGetWellTime(self): return self._getWellTime
  def GetIncubationTime(self): return self._incubationTime
  def GetSuperSpreadFraction(self): return self._superSpreadFraction
  def GetInitialSickFraction(self): return self._initialSickFraction
  def GetMaxDaysSick(self): return self._maxDaysSick
  def GetAgeDeathFact(self): return self._ageDeathFact
  def GetMaxAge(self): return self._maxAge

  def SetSpreadFrequency(self, spreadFrequency): self._spreadFrequency = spreadFrequency
  def SetSpreadRadius(self, spreadRadius): self._spreadRadius = spreadRadius
  def SetDeathProb(self, deathProb): self._deathProb = deathProb
  def SetHealProb(self, healProb): self._healProb = healProb
  def SetGetWellTime(self, getWellTime): self._getWellTime = getWellTime
  def SetIncubationTime(self, incubationTime): self._incubationTime = incubationTime
  def SetSuperSpreadFraction(self, superSpreadFraction): self._superSpreadFraction = superSpreadFraction
  def SetInitialSickFraction(self, initialSickFraction): self._initialSickFraction = initialSickFraction
  def SetMaxDaysSick(self, maxDaysSick): self._maxDaysSick = maxDaysSick
  def SetAgeDeathFact(self, ageDeathFact): self._ageDeathFact = ageDeathFact
  def SetMaxAge(self, maxAge): self._maxAge = maxAge

#########################################
class cattractor:
  # code generated by PrintGettersAndSetters.py
  def __init__(self, x, y, rmin, rmax, strength):
    self._x = x
    self._y = y
    self._rmin = rmin
    self._rmax = rmax
    self._strength = strength

  def GetX(self): return self._x
  def GetY(self): return self._y
  def GetRmin(self): return self._rmin
  def GetRmax(self): return self._rmax
  def GetStrength(self): return self._strength

  def SetX(self, x): self._x = x
  def SetY(self, y): self._y = y
  def SetRmin(self, rmin): self._rmin = rmin
  def SetRmax(self, rmax): self._rmax = rmax
  def SetStrength(self, strength): self._strength = strength

#########################################
class cperson:
  # code generated by PrintGettersAndSetters.py
  def __init__(self, id, age, x, y, attractors, status, sickDays, healed, nDaysInStatus):
    self._id = id
    self._age = age
    self._x = x
    self._y = y
    self._attractors = attractors
    self._status = status
    self._sickDays = sickDays
    self._healed = healed
    self._nDaysInStatus = nDaysInStatus

  def GetId(self): return self._id
  def GetAge(self): return self._age
  def GetX(self): return self._x
  def GetY(self): return self._y
  def GetAttractors(self): return self._attractors
  def GetStatus(self): return self._status
  def GetSickDays(self): return self._sickDays
  def GetHealed(self): return self._healed
  def GetNDaysInStatus(self): return self._nDaysInStatus

  def SetId(self, id): self._id = id
  def SetAge(self, age): self._age = age
  def SetX(self, x): self._x = x
  def SetY(self, y): self._y = y
  def SetAttractors(self, attractors): self._attractors = attractors
  def SetSickDays(self, sickDays): self._sickDays = sickDays
  def SetHealed(self, healed): self._healed = healed
  def SetNDaysInStatus(self, nDaysInStatus): self._nDaysInStatus = nDaysInStatus

  # manual:
  def SetXY(self, x,y):
      self._x = x
      self._y = y
  def SetStatus(self, status):
      self._status = status
      self._nDaysInStatus = 0
      
#########################################
def ComputeDistance(m1, m2):
    return sqrt( pow(m1.GetX() - m2.GetX(), 2) + pow(m1.GetY() - m2.GetY(), 2) )


    
