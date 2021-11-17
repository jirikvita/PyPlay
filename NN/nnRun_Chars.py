#!/usr/bin/python3
# Tue 12 Oct 14:32:31 CEST 2021

#from __future__ import print_function

# python
#import ROOT
from math import sqrt, pow, log, exp
import os, sys, getopt

# theano
# https://www.analyticsvidhya.com/blog/2016/04/neural-networks-python-theano/
import theano
import theano.tensor as T
from theano.ifelse import ifelse
from theano import function
from random import random

# numpy and plotting
import matplotlib.pyplot as plt
import numpy as np

# JK
from readTools import *

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

  
    print('*** Settings:')
    print('tag={:}, batch={:}'.format(gTag, gBatch))


    print('Loading...')


    # IDEA:
    # create then layers and neurons in a loop
    # read train data and convert them into linear numpy vectors
    # define the output categories as hex of the corresponding chars
    # train the NN on the train data


    # for reading test data 
    # imgs ids i1..i2
    i1, i2 = 70, 260
    #i1, i2 = 10, 10
    hexcodes = ['30', '31']
    
    # Step 1: Define variables

    #Define variables:
    #x = theano.tensor.fvector('x')
    x = T.matrix('x')

    # crop cutoff factor rebinned data:
    # todo: seems it does not work for different x,y cutoffs?
    cutoffx,cutoffy = 22, 22
    rebinx = 2
    rebiny = 2
    baseDimx = int(128  / rebinx) - 2*cutoffx
    baseDimy = int(128  / rebiny) - 2*cutoffy
    fullDIM = baseDimx*baseDimy # hack
    DIM = baseDimx*baseDimy # hack
    print('Got image dimension {}'.format(DIM))
    # lin dim for linearized img matrix

    # TODO: redesign the neurons structure
    # number of output neurons same as number of classes?
    # or a smooth output with a range?

    learning_rate = 0.002 # 0.01

    # weights, constants, and node outputs
    ws = []
    bs = []
    aas = []
    # list to store stacked neurons a's from each layer
    stacked_aas = []
    
    # Ns = [5, 2, len(hexcodes) ]
    Ns = [26, 22, 1]
    n0 = DIM
    n1 = Ns[0]
    n2 = Ns[1]
    n3 = Ns[2]
    
    print('*** defining first NN layer ***')
    ilayer = 0
    bs.append( theano.shared(1.) )
    ws.append([])
    aas.append([])
    for i in range(0,n1):
        ws[ilayer].append( theano.shared(np.array([ random() for j in range(0,n0) ])) )
    # Step 2: Define mathematical expression
    # activation funtion 1/(1+exp())
    for i in range(0,n1):
        aas[ilayer].append( 1/(1+T.exp(-T.dot(x,ws[-1][i])-bs[-1])) )
    # due to algebraic purposes, T.stack needs a list as input
    stacked_aas.append(T.stack(aas[-1],axis=1))
    print('*** defined first NN layer of {} neurons ***'.format(len(aas[-1])))
    #print(aas[-1])

    print('*** defining second NN layer ***')
    ilayer = 1
    bs.append( theano.shared(1.) )
    ws.append([])
    aas.append([])
    for i in range(0, n2):
        ws[ilayer].append( theano.shared(np.array([ random() for j in range(0,n1) ])) )
    for i in range(0,n2):
        aas[ilayer].append ( 1/(1+T.exp(-T.dot(stacked_aas[-1],ws[-1][i])-bs[-1])) )
    stacked_aas.append(T.stack(aas[-1],axis=1))
    print('*** defined second layer of {} neurons ***'.format(len(aas[-1])))
    #print(aas[-1])

    print('*** defining last single layer ***')
    ilayer = 2
    bs.append( theano.shared(1.) )
    ws.append([])
    aas.append([])
    for i in range(0, n3):
        ws[ilayer].append( theano.shared(np.array([ random() for j in range(0,n2) ])) )
    for i in range(0, n3):
        aas[ilayer].append( 1/(1+T.exp(-T.dot(stacked_aas[-1],ws[-1][i])-bs[-1])) )
    print('*** defined last layer of {} neurons ***'.format(len(aas[-1])))
    # no need to stack;)
    
    # Step 3: Define gradient and update rule
    print('+++ defining gradients +++')
    a_hat = T.vector('a_hat') #Actual output
    #cost = T.log(1.)
    #ng = len(aas[-1])
    #print('Last number of neurons: {}'.format(ng))
    #for i in range(0, ng):
    #    if i % 10 == 0:
    #        print('{}/{}'.format(i,ng))
    #    cost = cost + -(a_hat*T.log(aas[-1][i]) + (1.-a_hat)*T.log(1.-aas[-1][i])).sum()
    cost = -(a_hat*T.log(aas[-1][-1]) + (1.-a_hat)*T.log(1.-aas[-1][-1])).sum()

    # gradiends of weights:
    print('--- weight gradients ---')
    dws = []
    ng = len(ws)
    print('# of w\'s to go through: {}'.format(ng))
    for i in range(0, ng):
        print('  {}/{}'.format(i,ng))
        dws.append([])
        for j in range(0, len(ws[i])):
            dws[-1].append( T.grad(cost, ws[i][j]) )

    # gradiends of constant terms:
    print('--- const. terms gradients ---')
    dbs = []
    ng = len(bs)
    print('# of b\'s to go through: {}'.format(ng))
    for i in range(0, ng):
        print('  {}/{}'.format(i,ng))
        dbs.append( T.grad(cost, bs[i]) )
        
    locupdates = []
    ng = len(ws)
    print(ng)
    print('# of updates\'s to go through: {}'.format(ng))
    for i in range(0, ng):
        print('  {}/{}'.format(i,ng))
        for j in range(0, len(ws[i])):
            print('  {}/{}'.format(j,len(ws[i])))
            locupdates.append( [ws[i][j], ws[i][j] - learning_rate*dws[i][j]] )
    for i in range(0, len(bs)):
        locupdates.append( [bs[i], bs[i] - learning_rate*dbs[i]] )

    print('+++ defining the function +++')
    train = function(
        inputs = [x,a_hat],
        outputs = [aas[-1][-1],cost],
        updates = locupdates
    )
  
    inputs = []
    outputs = []

    print('+++ reading images +++')
    ihex = -1
    nhex = len(hexcodes)
    nnoutmax = 1.
    nnoutmin = 0.
    delta = 0.1
    sep = (nnoutmax - nnoutmin) / (nhex)
    print('separation for outputs: {}'.format(sep))
    for hexcode in hexcodes:
        ihex = ihex+1
        # need to normalize this to be between 0 and 1;)
        #hexout = int(hexcode, 16) / 128.
        hexout = nnoutmin + ihex*sep + delta
        imgs = readImages('data/by_class/', hexcode, i1, i2, cutoffx, cutoffy, rebinx, rebiny)
        iimg = -1
        print('will add images for class {} with output {}'.format(hexcode, hexout))
        for img in imgs:
            iimg = iimg+1
            #print('...appending input ', img)
            inputs.append(img)
            outputs.append(hexout)
            if iimg == 0:
                PrintImgFrom1D(img, baseDimx)
        print('--- Set to train over class {} with total of {} images! ---'.format(hexcode, len(inputs)))

    #print('Inputs: ', inputs)
    #print('Outputs: ', outputs)
    
    # Step 4: train the model:

    print('Training the model, linearized data dimension is {}'.format(DIM))
    
    #Iterate through all inputs and find outputs:
    print('+++ Training: Iterating through inputs, finding outputs...{} times +++'.format(i2-i1))
    cost = []
    nIters = 1000 # 30000
    for iteration in range(0, nIters):
        pred, cost_iter = train(inputs, outputs)
        if iteration % 200 == 0:
            print('iteration {}, cost: {}'.format(iteration, cost_iter))
        cost.append(cost_iter)

    #Print the outputs:
    print('+++ The outputs of the NN are: +++')
    for i in range(len(inputs)):
        # print('The output for x1={} | stacked_aas={} is {:.2f}'.format(inputs[i][0],inputs[i][1],pred[i]))
        print('The output for true class {} is {:.2f}'.format(outputs[i],pred[i]))
        
    #Plot the flow of cost:
    print('\nThe flow of cost during model run is as following:')
    # matplotlib inline
    plt.plot(cost)
    plt.show()

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

