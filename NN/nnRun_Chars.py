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
    hexcodes = ['5a', '79']
    
    # Step 1: Define variables

    #Define variables:
    #x = theano.tensor.fvector('x')
    x = T.matrix('x')

    baseDim = 128
    fullDIM = baseDim*baseDim # hack
    cutoffx,cutoffy = 40,40
    DIM = (baseDim - 2*cutoffx)*(baseDim - 2*cutoffy) # hack
    print('Got image dimension {}'.format(DIM))
    # lin dim for linearized img matrix

    # TODO: redesign the neurons structure
    # number of output neurons same as number of classes?
    # or a smooth output with a range?

    learning_rate = 0.01

    # weights, constants, and node outputs
    ws = []
    bs = []
    aas = []

    # Ns = [5, 2, len(hexcodes) ]
    Ns = [24, 24, 1]
    n1 = Ns[0]
    n2 = Ns[1]

    bs.append( theano.shared(1.) )
    ilayer = 0
    ws.append([])
    for i in range(0,n1):
        ws[ilayer].append( theano.shared(np.array([ random() for j in range(0,DIM) ])) )


    # Step 2: Define mathematical expression
    # actiavtion funtion 1/(1+exp())
    aas.append([])
    for i in range(0,n1):
        aas[ilayer].append( 1/(1+T.exp(-T.dot(x,ws[ilayer][i])-bs[ilayer])) )


    stacked_aas = []
    bs.append( theano.shared(1.) )
    aas.append([])
    ilayer = 1
    ws.append([])
    for i in range(0, Ns[-1]):
        # due to algebraic purposes:
        stacked_aas.append(T.stack(aas[0],axis=1))
        # last node combines 2 into one
        ws[ilayer].append( theano.shared(np.array([ random() for j in range(0,n1) ])) )
        aas[ilayer].append ( 1/(1+T.exp(-T.dot(stacked_aas[-1],ws[ilayer][-1])-bs[ilayer])) )

    # Step 3: Define gradient and update rule
    print('Defining gradients...')
    a_hat = T.vector('a_hat') #Actual output
    cost = T.log(1.)
    ng = len(aas[-1])
    print(ng)
    for i in range(0, ng):
        if i % 10 == 0:
            print('{}/{}'.format(i,ng))
        cost = cost + -(a_hat*T.log(aas[-1][i]) + (1.-a_hat)*T.log(1.-aas[-1][i])).sum()

    dws = []

    ng = len(ws)
    print(ng)
    for i in range(0, ng):
        if i % 10 == 0:
            print('{}/{}'.format(i,ng))
        dws.append([])
        for j in range(0, len(ws[i])):
            dws[-1].append( T.grad(cost, ws[i][j]) )
    
    dbs = []
    ng = len(bs)
    print(ng)
    for i in range(0, ng):
        if i % 10 == 0:
            print('{}/{}'.format(i,ng))
        dbs.append( T.grad(cost, bs[i]) )
        
    locupdates = []
    ng = len(ws)
    print(ng)
    for i in range(0, ng):
        if i % 10 == 0:
            print('{}/{}'.format(i,ng))
        for j in range(0, len(ws[i])):
            locupdates.append( [ws[i][j], ws[i][j] - learning_rate*dws[i][j]] )
    for i in range(0, len(bs)):
        locupdates.append( [bs[i], bs[i] - learning_rate*dbs[i]] )

    print('Defining the function')
    train = function(
        inputs = [x,a_hat],
        outputs = [aas[-1][-1],cost],
        updates = locupdates
    )


  
    inputs = []
    outputs = []

    print('Reading images...')
    for hexcode in hexcodes:
        imgs = readImages('data/by_class/', hexcode, i1, i2, cutoffx, cutoffy)
        iimg = -1
        for img in imgs:
            iimg = iimg+1
            #print('...appending input ', img)
            inputs.append(img)
            # need to normalize this to be between 0 and 1;)
            outputs.append(int(hexcode, 16) / 128.)
            print('Set to train over class {} with total of {} images!'.format(hexcode, len(inputs)))
            if iimg == 0:
                PrintImg(img, baseDim, cutoffx, cutoffy)

    #print('Inputs: ', inputs)
    #print('Outputs: ', outputs)
    
    # Step 4: train the model:

    print('Training the model, linearized data dimension is {}'.format(DIM))
    
    #Iterate through all inputs and find outputs:
    print('Training: Iterating through inputs, finding outputs...{} times'.format(i2-i1))
    cost = []
    nIters = 5000 # 30000
    for iteration in range(0, nIters):
        pred, cost_iter = train(inputs, outputs)
        if iteration % 200 == 0:
            print('iteration {}, cost: {}'.format(iteration, cost_iter))
        cost.append(cost_iter)

    #Print the outputs:
    print('The outputs of the NN are:')
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

