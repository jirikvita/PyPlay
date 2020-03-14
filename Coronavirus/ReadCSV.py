#!/usr/bin/python
# Thu 12 Mar 12:20:43 CET 2020
# using data from https://github.com/CSSEGISandData/COVID-19


from __future__ import print_function

from math import sqrt, pow, log, exp
import os, sys, getopt

cans = []
stuff = []

kThr = 4

kAcceptProvinces = ['', 'Hubei' ,'UK' ,'British Columbia' ,'Washington' ,'France']


##########################################
def MakeGraphs(fname):
    csvfile = open(fname, 'r')
    graphs = {}
    iline = -1
    dates = []
    
    for xline in csvfile.readlines():
        iline = iline + 1
        line = xline[:-1]
        items = line.split(',')
        if iline == 0:
            dates = items[4:]
            continue
        graph = []
        vals = items[4:]
        province,state = items[0], items[1]

        # skip provinces for the moment
        if province not in kAcceptProvinces:
            continue
        print(items)
        gname = '{}{}'.format(province,state)
        if province != '':
            gname = '{} {}'.format(province,state)
        ip = 0
        id = 0
        for date,sval in zip(dates,vals):
            if sval[-1] == '\r':
                sval = sval[:-1]
            val = int(sval)
            if val > kThr:
                err = sqrt(val)
                graph.append( [id, date, val, err] )
                ip = ip + 1
            id = id + 1
        graphs[gname] = graph
    return graphs

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

    filename = 'time_series_19-covid-Confirmed.csv'
    graphs = MakeGraphs(filename)

    CountriesToPlot = { 'Hubei China',     
                        'Italy'       ,  
                        'Germany'      , 
                        'France France' ,
                        'Spain'         ,
                        'Belgium'       ,
                        'Sweden'        ,
                        'Czechia'       ,
                        'Austria'       ,
                        #'Hungary'      ,
                        #'Slovakia'     ,
                        'Japan'         ,
                        'Korea South'   ,
                        'UK United Kingdom',
                        'Iran'             ,
                        'Thailand'         ,
                        'British Columbia Canada',
    }

    AllCountries = []
    for gname in graphs:
        AllCountries.append(gname)
    print(AllCountries)
    
    for country in graphs:
        if country not in CountriesToPlot:
            continue
        graph = graphs[country]
        print(country)
        print(graph)
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

