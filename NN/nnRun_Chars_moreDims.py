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
   
    
    # Step 1: Define variables

    #Define variables:
    #x = theano.tensor.fvector('x')
    x = T.matrix('x')

    DIM = 4096 # hack
    print('Got image dimension {}'.format(DIM))
    # lin dim for linearized img matrix

    # TODO: redesign the neurons structure
    # number of output neurons same as number of classes?
    # or a smooth output with a range?

    ws = []
    bs = []

    n1 = 3
    n2 = 2

    bs.append( theano.shared(1.) )
    for i in range(0,n1):
        ws.append( theano.shared(np.array([ random() for j in range(0,DIM) ])) )

    # last node combines 2 into one
    ws.append( theano.shared(np.array([ random() for j in range(0,n1) ])) )

    learning_rate = 0.01

    # Step 2: Define mathematical expression
    aas = []
    for i in range(0,n1):
        aas.append( 1/(1+T.exp(-T.dot(x,ws[i])-bs[0])) )

    # due to algebraic purposes:
    # TO GENERALIZE!
    x2 = T.stack(aas,axis=1)
    bs.append( theano.shared(1.) )
    aas.append ( 1/(1+T.exp(-T.dot(x2,ws[-1])-bs[1])) )

    # Step 3: Define gradient and update rule
    print('Defining gradients...')
    a_hat = T.vector('a_hat') #Actual output
    cost = -(a_hat*T.log(aas[-1]) + (1-a_hat)*T.log(1-aas[-1])).sum()

    dws = []
    for i in range(0, len(ws)):
        dws.append( T.grad(cost, ws[i]) ) 
    dbs = []
    for i in range(0, len(bs)):
        dbs.append( T.grad(cost, bs[i]) ) 
    locupdates = []
    for i in range(0, len(ws)):
        locupdates.append( [ws[i], ws[i] - learning_rate*dws[i]] )
    for i in range(0, len(bs)):
        locupdates.append( [bs[i], bs[i] - learning_rate*dbs[i]] )
    
    train = function(
        inputs = [x,a_hat],
        outputs = [aas[-1],cost],
        updates = locupdates
    )


    # read test data and measure the performace
    # inputs
    # indices range
    i1, i2 = 100, 110
    hexcodes = ['5a', '79']
    inputs = []
    outputs = []
    for hexcode in hexcodes:
        imgs = readImages('data/by_class/', hexcode, i1, i2)
        for img in imgs:
            #print('...appending input ', img)
            inputs.append(img)
            outputs.append(int(hexcode, 16) / 128.) # need to nprmalize this to be between 0 and 1;)
            print('Set to train over class {} with total of {} images!'.format(hexcode, len(inputs)))

    #print('Inputs: ', inputs)
    #print('Outputs: ', outputs)
    
    # Step 4: train the model:
  
    #Iterate through all inputs and find outputs:
    print('Training: Iterating through inputs, finding outputs...{} times'.format(i2-i1))
    cost = []
    nIters = 1000 # 30000
    for iteration in range(0, nIters):
        pred, cost_iter = train(inputs, outputs)
        print('iteration {}, cost: {}'.format(iteration, cost_iter))
        cost.append(cost_iter)

    #Print the outputs:
    print('The outputs of the NN are:')
    for i in range(len(inputs)):
        # print('The output for x1={} | x2={} is {:.2f}'.format(inputs[i][0],inputs[i][1],pred[i]))
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

