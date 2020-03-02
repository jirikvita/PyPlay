#!/usr/bin/python3

# jk 23.2.2020

# based on https://realpython.com/python-csv/
# https://matplotlib.org/gallery/lines_bars_and_markers/barh.html#sphx-glr-gallery-lines-bars-and-markers-barh-py
# https://stackoverflow.com/questions/4042192/reduce-left-and-right-margins-in-matplotlib-plot
# https://stackoverflow.com/questions/9764298/is-it-possible-to-sort-two-listswhich-reference-each-other-in-the-exact-same-w
# https://docs.python.org/3/howto/sorting.html
# https://stackoverflow.com/questions/29672375/histogram-in-matplotlib-time-on-x-axis
# https://matplotlib.org/3.1.1/api/dates_api.html

import csv, os, sys

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from math import log10

from collections import OrderedDict

#########################################
# generate zeros before a string from a short integer like '0012'
def MakeDigitStr(i, digits = 4):
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

##############################################################
def MakeNtotTitle(i):
   str = MakeDigitStr(i, 2)
   return ' N=' + str

##############################################################

def MakeKeyTag(itag, key):
   keytag = itag + '_' + key
   keytag = keytag.replace(' ','_').replace('/','nebo').replace(',','_').replace('(','_').replace(')','_').replace('?','_')
   if key == '':
       keytag = keytag.replace('_','')
   return keytag

##############################################################

barCharts = ['Informace získávám', 'Jsem z fakulty / odjinud', 'O anketě jsem se dozvěděl(a) ']

kComment = 'Comment'
kCommentKey = 'Comment'
kEmpty = 'empty'
kNotAnswered = 'Nezodpovězeno'
kTimeStamp = 'Timestamp'
toSkip = [kComment,
          # kTimeStamp
         ]

toSkip2d = [kComment,
            kTimeStamp,
            barCharts[0], barCharts[2],
            "Současné dění okolo VŠÚ na UP považuji za záležitost",
            "Současné etické kauzy na UP I","Současné etické kauzy na UP II","Dění okolo Etické komise UP","Etické podněty ohledně možného falšování dat považuji za","Etické podněty k chování, komunikaci, práci či rozhodování některých zaměstnanců či vedoucích pracovníků považuji za","Roli univerzitního ombudsmana/ky","Postoje a postup vedení UP v řešení vzniku VŠÚ považuji za","Postoje a postup vedení UP v řešení etických kauz považuji za","Způsob řešení problémů na UP ze strany vedení UP považuji za ","Univerzitu Palackého považuji z hlediska mé vědecké, pedagogické či jiné práce","Na dění na UP ohledně vzniku VŠÚ","Na dění na UP ohledně etických kauz","K dění na UP ohledně vzniku VŠÚ","K dění na UP v etických kauzách","Svůj názor na dění na UP ohledně vzniku VŠÚ","Svůj názor na dění na UP ohledně etických kauz",
            "Anketu jsem uvítal(a)","Rád budu seznámen(a) s výsledky (budou zveřejněny na UP reflexi)", "Mám možnost se svobodně rozhodnout, zda ve VŠÚ chci pracovat nebo ne"
]

def SkipKey(key):
   for toskip in toSkip:
      if toskip in key:
         return True
   return False

def IsCheckListForBarChart(key):
   for bch in barCharts:
      if key == bch:
         return True
   return False



#########################################
def GetIndex(key, keys, nUniq):
    s = 0
    for key2 in keys:
        if key == key2:
            break
        s += nUniq[key2]
    return s

#########################################
def MakeLabels(uniqs, numeric = True):
    labels = []
    ikey = 0
    for key in uniqs:
        ikey += 1
        for val in uniqs[key]:
            if numeric:
                labels.append('{}: {}'.format(ikey,val))
            else:
                labels.append('{}: {}'.format(key, val))
    return labels

#########################################

def PlotData2d(Data, dirname, pdfdirname, nmaxSegments = 6):

    keys = []
    for data in Data:
        for key in data:
            if key in toSkip2d:
                continue
            keys.append(key)
        break

    uniqueAnsws = {}
    for data in Data:
        ikey = 0
        for key in data:
            if key in toSkip2d:
                continue
            if not key in keys:
                keys.append(key)
            ikey += 1
            try:
                test = uniqueAnsws[key]
            except:
                uniqueAnsws[key] = []
            answ = data[key]
            if answ == '':
                answ = kNotAnswered
                continue # screw it!
            if not answ in uniqueAnsws[key]:
                if len(uniqueAnsws[key]) < nmaxSegments:
                    uniqueAnsws[key].append(answ)
                else:
                    uniqueAnsws[key][-1] = 'Jinak'

    #print('Unique answers are')
    #print(uniqueAnsws)

    nUniq = {}
    for key in uniqueAnsws:
        nUniq[key] = len(uniqueAnsws[key])
    nKeys = len(keys)


    #print('Key counts are')
    #print(nUniq)

    x = []
    y = []
    N = 0
    idata = -1
    for data1 in Data:
        idata = idata + 1
        for key1 in data1:
            if key1 in toSkip2d:
                continue
            if idata == 0:
                N = N + nUniq[key1]
            for data2 in Data:
                for key2 in data2:
                    if key2 in toSkip2d:
                        continue
                    if key1 != key2:
                        #print(uniqueAnsws[key1].index(data1[key1]), uniqueAnsws[key2].index(data2[key2]) )
                        li1 = 0
                        li2 = 0
                        #try:
                        answ1 = data1[key1]
                        if answ1 == '':
                            answ1 = kNotAnswered
                            continue
                        #print(uniqueAnsws[key1])
                        #print('"{}"'.format(answ1))
                        if answ1 in uniqueAnsws[key1]:
                            li1 = uniqueAnsws[key1].index(answ1)
                        #except ValueError:
                        else:
                            li1 = len(uniqueAnsws[key1])-1
                        #try:
                        answ2 = data2[key2]
                        if answ2 == '':
                            answ2 = kNotAnswered
                            continue
                        #print(uniqueAnsws[key2])
                        #print('"{}"'.format(answ2))
                        if answ2 in uniqueAnsws[key2]:
                            li2 = uniqueAnsws[key2].index(answ2)
                        #except ValueError:
                        else:
                            li2 = len(uniqueAnsws[key2])-1
                        i1 = GetIndex(key1, keys, nUniq) + li1
                        i2 = GetIndex(key2, keys, nUniq) + li2
                        #print(key1, data1[key1], key2, data2[key2], i1, i2)
                        x.append(i1)
                        y.append(i2)

    print('N of total bins: {}'.format(N))
    print('Number of data rows: {}'.format(len(Data)))

    #print(len(x), len(y))
    #for xx,yy in zip(x,y):
    #    print(xx,yy)

    fig, ax = plt.subplots(figsize=(10, 10))
    plt.subplots_adjust(bottom = 0.25, left = 0.25, right = 0.99, top = 0.99) # hspace = 0.3, wspace = 0.3
    ax.hist2d(x, y, bins = (range(0,N+1),range(0,N+1)), cmap=plt.cm.jet)

    bins = [  i + 0.5 for i in range(0,N) ]
    ax.set_xticks(bins)
    ax.set_yticks(bins)

    labels = MakeLabels(uniqueAnsws)
    ax.set_xticklabels(labels)
    ax.set_yticklabels(labels)

    for tick in ax.get_xticklabels():
        tick.set_rotation(90)
    for tick in ax.get_xticklabels():
        tick.set_rotation(90)
    
    plt.savefig('{}Data2d.png'.format(dirname))
    if not '00' in dirname:
        plt.savefig('{}Data2d.pdf'.format(pdfdirname))
    # plt.show()
        
    return fig

##############################################################

class ccondition:
  # code generated by PrintGettersAndSetters.py
   def __init__(self, reqAnsw, doReq, logic):
      self._reqAnsw = reqAnsw
      self._doReq = doReq
      self._logic = logic

   def GetReqAnsw(self): return self._reqAnsw
   def GetDoReq(self): return self._doReq
   def GetLogic(self): return self._logic

   def SetReqAnsw(self, reqAnsw): self._reqAnsw = reqAnsw
   def SetDoReq(self, doReq): self._doReq = doReq
   def SetLogic(self, logic): self._logic = logic


##############################################################
##############################################################
##############################################################

def makeQuickSummary(filename):
    print('Making quick summary results...')
    # data for correlations, should not include the empty answer nor the 'Jinak' key
    
    keys = []
    with open(filename, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        line_count = 0
        print('Making keys dict...')
        for row in csv_reader:
           # print(row)
           if line_count == 0:
              #print('Column names are')
              #print(row)
              for key in row:
                 keys.append(key)
           else:
              break
           line_count += 1

    results = {} # OrderedDict()

    Data = [] # for 2D plot

    with open(filename, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        line_count = 0
        print('Processing lines...')
        line_count = 0
        irow = -1
        for row in csv_reader:
           irow += 1
           #if irow < 100:
           Data.append(row)
           #print('Processing row')
           #print(row)
           ikey = 0
           for key in keys:
              ikey = ikey + 1
              if SkipKey(key):
                 continue
              if key == kTimeStamp:
                 answs = row[key].split(';')
                 for answ in answs:
                    #print(answ)
                    try:
                       tmp = results[key]
                    except:
                       results[key] = OrderedDict()
                    results[key][answ] = answ # kinda lame but works with downstream code;)
              else:
                 answs = []
                 if not IsCheckListForBarChart(key):
                    answs.append(row[key])
                 else:
                    answs = row[key].split(';')

                 for answ in answs:
                    #print(answ)
                    try:
                       tmp = results[key]
                    except:
                       results[key] = OrderedDict()
                    try:
                       results[key][answ] = results[key][answ] + 1
                    except:
                       results[key][answ] = 1
                    
           line_count += 1
        print('*** Processed {:} lines.'.format(line_count))
        #print('*** The results and counts are:')
        #print(results)
        return Data, line_count,results
    
##############################################################
def makeResults(filename, filtername, Filter, nReqLines = -1):
    print('*** Processing Filter {}'.format(filtername))

    # Get keys
    keys = []
    with open(filename, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        line_count = 0
        print('Making keys dict...')
        for row in csv_reader:
           #print(row)
           if line_count == 0:
              #print('Column names are')
              #print(row)
              for key in row:
                 keys.append(key)
           else:
              break
           line_count += 1

    # Check filter conditions
    results = {} # OrderedDict()
    line_count = 0
    with open(filename, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
           if nReqLines > 0 and line_count >= nReqLines:
              continue
           #print('*** Processing row {}'.format(line_count))
           #print(row)
           # First loop over keys to get the filter condition
           skipBasedOnComments = False
           for fkey in Filter:
              if kComment in fkey:
                 #print('OK, we want to filter on comments field!')
                 Conditions = Filter[fkey]
                 for condition in Conditions:
                    reqAnsw = condition.GetReqAnsw()
                    doReq = condition.GetDoReq()
                    logic = condition.GetLogic()
                    comment = row[kCommentKey]
                    #print(' condition: {} {}'.format(reqAnsw, doReq))
                    #print('  ...the comment is "{}"'.format(comment))
                    # we want non-empty comment:
                    if reqAnsw == kEmpty and doReq == False and comment == '':
                       skipBasedOnComments = True
                       # pop out the first comments condition in next upgrade?
                       #print('    Skip on empty comment request, {}'.format(skipBasedOnComments))
                       break
                    # we want empty comment: 
                    if reqAnsw == kEmpty and doReq == True and comment != '':
                       skipBasedOnComments = True
                       #print('    Skip on non-empty comment request, {}'.format(skipBasedOnComments))
                       break
              if skipBasedOnComments:
                 break

           if skipBasedOnComments:
              #print('         SKIPPING!')
              continue
                       
           #print('         PROCESSING!!')

           toPass = not skipBasedOnComments # True
           for key in keys:
              if SkipKey(key):
                 continue
              answs = []
              if not IsCheckListForBarChart(key):
                 answs.append(row[key])
              else:
                 answs = row[key].split(';')
              for answ in answs:
                 #print('* Processing key "{}"'.format(key))
                 # go through required filter keys
                 for fkey in Filter:
                    if fkey == kCommentKey:
                       continue
                    #print('  processing filter key {}'.format(fkey))
                    if key == fkey:
                         #print('    ok, have matching keys {} and {}'.format(key, fkey))
                         Conditions = Filter[fkey]
                         nCond = len(Conditions)
                         #print('  processing {} conditions'.format(nCond))
                         thisPass = True
                         icond = -1
                         for condition in Conditions:
                             icond = icond + 1
                             #print(condition)
                             reqAnsw = condition.GetReqAnsw()
                             doReq = condition.GetDoReq()
                             logic = condition.GetLogic()
                             #print('      row data are: "{}": "{}"'.format(key, answ))
                             microCondition = False
                             if doReq:
                                 microCondition = reqAnsw in answ
                             else:
                                 microCondition = not ( reqAnsw in answ )
                             if logic == 'OR':
                                #print('        ...ORing with previous condition')
                                thisPass = thisPass or microCondition
                             elif logic == 'AND':
                                #print('        ...ANDing with previous condition')
                                thisPass = thisPass and microCondition
                             elif logic == '' and (nCond == 1 or (nCond > 1 and icond == 0) ):
                                #print('        ...defining as current condition')
                                thisPass = microCondition
                             else:
                                print('        THIS SHOULD NEVER HAPPEN!')
                             #print('       processed key for "{}" condition "{}" "{}" "{}"'.format(fkey, reqAnsw, doReq, logic))
                             #print('       microCondition: {} thisPass: {}'.format(microCondition, thisPass))
                         if thisPass == False:
                            toPass = False
                         #print('  ...done processing conditions!')
                    if not toPass:
                       #print('      leaving filter!')
                       break

                 if not toPass:
                   #print('  FAILED cuts, leaving the key loop!!')
                   continue
           
           # keep filling/counting otherwise:) 
           if toPass:
              #print('  PASSED cuts, filling;-)')
              # Second loop over filter condition to collect the counts
              for key in keys:
                 if SkipKey(key):
                    continue
                 if key == kTimeStamp:
                    answs = row[key].split(';')
                    for answ in answs:
                       #print(answ)
                       try:
                          tmp = results[key]
                       except:
                          results[key] = OrderedDict()
                       results[key][answ] = answ # kinda lame but works with downstream code;)
                 else:
                    answs = []
                    if not IsCheckListForBarChart(key):
                       answs.append(row[key])
                    else:
                       answs = row[key].split(';')

                    #print('   FILLING!')
                    for answ in answs:
                        #print(answ)
                        try:
                           tmp = results[key]
                        except:
                           results[key] = {} # OrderedDict()
                        try:
                           results[key][answ] = results[key][answ] + 1
                        except:
                           results[key][answ] = 1


              line_count += 1



    print('*** Processed {:} lines.'.format(line_count))
    #print('*** The results and counts are:')
    #print(results)
    return line_count,results
    


##############################################################

def func(pct, allvals):
    absolute = int(pct/100.*np.sum(allvals))
    return "{:.1f}%\n({:d})".format(pct, absolute)

##############################################################

def plotresults(dirname, results, nLines, nReqLines = -1, nmaxSegments = 8):

   pies = []
   dirname = 'png_' + dirname 
   if len(dirname) > 0:
      if dirname[-1] != '/':
         dirname = dirname + '/'
   os.system('mkdir -p {}'.format(dirname))
   pdfdirname = dirname
   pdfdirname = pdfdirname.replace('png','pdf')
   if not '00' in dirname:
      os.system('mkdir -p {}'.format(pdfdirname))
   
   ikey = 0
   for key in results:
      #print('In plotresults...')
      data = []
      answers = []
      #print(key, results[key])
      iansw = 0
      for answ in results[key]:
         respondents_count = results[key][answ] 
         if key != kTimeStamp:
            if iansw < nmaxSegments or IsCheckListForBarChart(key):
               data.append(respondents_count)
               leg_answ = answ
               if leg_answ == '':
                  leg_answ = kNotAnswered
               answers.append(leg_answ)
            else:
               data[-1] = data[-1] + respondents_count
               answers[-1] = 'Jinak'
         else:
            data.append(respondents_count)
         iansw = iansw + 1
      #print('plotting {} {}'.format(key, data))
      if not kNotAnswered in answers and key != kTimeStamp:
         data.append(0)
         answers.append(kNotAnswered)
      if key != kTimeStamp:
         data, answers = zip(*sorted(zip(data, answers), reverse=True))
         data, answers = (list(t) for t in zip(*sorted(zip(data, answers), reverse=True)))
      else:
         mdata = mdates.datestr2num(data)
         data = mdata
      if key == kTimeStamp:
         #print('OK, plotting histogram of timestamps!')
         # make a time histogram
         fig, ax = plt.subplots(1,1)
         #print(data)
         ax.hist(data, bins = 150, color = 'blue')
         #ax.xaxis.set_major_locator(mdates.YearLocator())
         ax.xaxis.set_major_locator(mdates.DayLocator())
         ax.xaxis.set_major_formatter(mdates.DateFormatter('%d %h')) # %d.%m.%y'))
         ax.set_title(key + MakeNtotTitle(nLines))
         itag = str(ikey)
         if ikey < 10:
            itag = '0' + itag
         if ikey < 1:
              itag = '00'
         keytag = MakeKeyTag(itag, '') # MakeKeyTag(itag, key)
         plt.savefig('{}{}.png'.format(dirname, keytag))
         if not '00' in dirname:
            plt.savefig('{}{}.pdf'.format(pdfdirname, keytag))
         ikey = ikey + 1
         pies.append(fig)
      elif not IsCheckListForBarChart(key):
         # pie plot
         plt.tight_layout()
         plt.subplots_adjust(left=0.1,wspace = 0.1)
         fig, ax = plt.subplots(figsize=(7, 9), subplot_kw = dict(aspect = "equal"))
         wedges, texts, autotexts = ax.pie(data, autopct = lambda pct: func(pct, data),
                                           textprops = dict(color = "w"))
         ax.legend(wedges, answers,
                   title = key,
                   loc="center left",
                   bbox_to_anchor=(0, 0., 0.5, -0.2)
         )
         plt.setp(autotexts, size=8, weight="bold")
         ax.set_title(key  + MakeNtotTitle(nLines))
         itag = str(ikey)
         if ikey < 10:
            itag = '0' + itag
         if ikey < 1:
              itag = '00'
         keytag = MakeKeyTag(itag, '') # MakeKeyTag(itag, key)
         plt.savefig('{}{}.png'.format(dirname, keytag))
         if not '00' in dirname:
            plt.savefig('{}{}.pdf'.format(pdfdirname, keytag))
         ikey = ikey + 1
         #plt.show()
         pies.append(fig)
      else:
         #print('OK, request for a ybar chart!;-)')
         # ybar chart
         # plt.rcdefaults()
         fig, ax = plt.subplots()
         #fig, ax = plt.subplots(figsize=(10, 3), subplot_kw = dict(aspect = "equal"))
         figsize = [4,4]
         margins = {  #     vvv margin in inches
            "left"   :     2. / figsize[0],
            "bottom" :     0.8 / figsize[1],
            "right"  : 1 - 0.3 / figsize[0],
            "top"    : 1 - 1   / figsize[1]
         }
         fig.subplots_adjust(**margins)
         y_pos = np.arange(len(data))
         #performance = 3 + 10 * np.random.rand(len(data))
         #error = np.random.rand(len(data))
         itag = str(ikey)
         if ikey < 10:
            itag = '0' + itag
         if ikey < 1:
            itag = '00'
         keytag = MakeKeyTag(itag, '') # MakeKeyTag(itag, key)

         #ax.barh(y_pos, data, xerr=error, align='center')
         fdata = []
         #print(data)
         for val in data:
            fdata.append( val / (1.*nLines)*100 )
         #print(fdata)
         ax.barh(y_pos, fdata, align = 'center')
         ax.set_yticks(y_pos)
         ax.set_yticklabels(answers)
         ax.invert_yaxis()  # labels read top-to-bottom
         ax.set_xlabel('Četnost [%]')
         ax.set_title(key + MakeNtotTitle(nLines))
         #plt.show()
         plt.savefig('{}{}.png'.format(dirname, keytag))
         if not '00' in dirname:
            plt.savefig('{}{}.pdf'.format(pdfdirname, keytag))
         pies.append(fig)
         ikey = ikey + 1

   return pies



##############################################################
##############################################################
##############################################################

def main(argv):

    filename = 'Dotaznik.csv'

    Pies = []
    
    allResults = []
    
    Data, nLines, sumResults = makeQuickSummary(filename)
    allResults.append(sumResults)
    plotdir = 'sumResults'
    pie = plotresults(plotdir, sumResults, nLines)
    Pies.append(pie)
    #fig = PlotData2d(Data, 'png_' + plotdir, 'pdf_' + plotdir )
    #Pies.append(fig)
    
    # and now some Filters;-)
    # structure: key : ['requiredVal', requireNotInvert]
    # if more for one key, then can OR or AND them!
    Filters = { 'All' : {'' : []},
                #'Studenti' :    { 'Jsem pracovník' : [ccondition('student', True, '')] },
                #'nonStudenti' :    { 'Jsem pracovník' : [ccondition('student', False, '')] },
                #'Muzi' :    { 'Jsem' : [ccondition('muž', True, '')] },
                #'NonMuzi' :    { 'Jsem' : [ccondition('muž', False, '')] },
                #'Zeny' :    { 'Jsem' : [ccondition('žena', True, '')] },
                #'PrF' :     { 'Jsem z fakulty / odjinud' : [ ccondition('PřF', True, '') ] },
                #'MuziPrF' : { 'Jsem z fakulty / odjinud' : [ ccondition('PřF', True, '') ], 'Jsem' : [ccondition('muž', True, '')] },
                #'nonMuziPrF' : { 'Jsem z fakulty / odjinud' : [ ccondition('PřF', True, '') ], 'Jsem' : [ccondition('muž', False, '')] },
                #'nonPrF' :  { 'Jsem z fakulty / odjinud' : [ ccondition('PřF', False, '')] },
                #'LForFF' :  { 'Jsem z fakulty / odjinud' : [ ccondition('LF', True, ''), ccondition('FF', True, 'OR') ] },
                #'MuzLForFF' :  { 'Jsem' : [ccondition('muž', True, '')],
                #                 'Jsem z fakulty / odjinud' : [ ccondition('LF', True, ''), ccondition('FF', True, 'OR') ] },
                #'Comments' : { kComment : [ccondition(kEmpty, False, '')] },
                #'noComments' : { kComment : [ccondition(kEmpty, True, '')] },
    }

    # HACK!!
    #Filters = {}
    
    for filtername in Filters:
        print('### Processing filter {}'.format(filtername))
        nLines,results = makeResults(filename, filtername, Filters[filtername])
        allResults.append(results)
        pie = plotresults(filtername, results, nLines)
        Pies.append(pie)
        # HACK
        if FALSE and filtername == 'All':
           #  create many partial results ong for anim gifs
           for nReqLines in range(6, nLines, 10):
              print('### Processing filter {}, iteration {}'.format(filtername, nReqLines))
              nLines2,results2 = makeResults(filename, filtername, Filters[filtername], nReqLines)
              allResults.append(results2)
              pie2 = plotresults(filtername + '_' + MakeDigitStr(nReqLines), results2, nReqLines)
              Pies.append(pie2)
           


###################################
###################################
###################################

if __name__ == "__main__":
    # execute only if run as a script"
    main(sys.argv)
    
###################################
###################################
###################################



