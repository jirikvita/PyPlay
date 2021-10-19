#!/usr/bin/python3
# Tue 12 Oct 14:32:31 CEST 2021

#from __future__ import print_function

# OLD:
# https://www.journaldev.com/17840/theano-python-tutorial
#import theano
#from theano import tensor
#import numpy

# NEW:
# https://www.analyticsvidhya.com/blog/2016/04/neural-networks-python-theano/
import theano
import theano.tensor as T
from theano.ifelse import ifelse
import numpy as np

# jk:
from theano import function
from random import random

import matplotlib.pyplot as plt

#import ROOT
from math import sqrt, pow, log, exp
import os, sys, getopt

cans = []
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
    
    # Step 1: Define variables

    #Define variables:
    x = T.matrix('x')
    w1 = theano.shared(np.array([random(),random()]))
    w2 = theano.shared(np.array([random(),random()]))
    w3 = theano.shared(np.array([random(),random()]))
    b1 = theano.shared(1.)
    b2 = theano.shared(1.)
    learning_rate = 0.01

    # Step 2: Define mathematical expression
    a1 = 1/(1+T.exp(-T.dot(x,w1)-b1))
    a2 = 1/(1+T.exp(-T.dot(x,w2)-b1))
    x2 = T.stack([a1,a2],axis=1)
    a3 = 1/(1+T.exp(-T.dot(x2,w3)-b2))

    # Step 3: Define gradient and update rule
    print('Defining gradients...')
    a_hat = T.vector('a_hat') #Actual output
    cost = -(a_hat*T.log(a3) + (1-a_hat)*T.log(1-a3)).sum()
    dw1,dw2,dw3,db1,db2 = T.grad(cost,[w1,w2,w3,b1,b2])

    train = function(
        inputs = [x,a_hat],
        outputs = [a3,cost],
        updates = [
            [w1, w1-learning_rate*dw1],
            [w2, w2-learning_rate*dw2],
            [w3, w3-learning_rate*dw3],
            [b1, b1-learning_rate*db1],
            [b2, b2-learning_rate*db2]
        ]
    )

    # Step 4: train the model:
    inputs = [
        [0, 0],
        [0, 1],
        [1, 0],
        [1, 1]
    ]
    outputs = [1,0,0,1]

    #Iterate through all inputs and find outputs:
    nIter = 30000
    print('Training: Iterating through inputs, finding outputs...{} times'.format(nIter))
    cost = []
    for iteration in range(nIter):
        pred, cost_iter = train(inputs, outputs)
        cost.append(cost_iter)

    #Print the outputs:
    print('The outputs of the NN are:')
    for i in range(len(inputs)):
        print('The output for x1={} | x2={} is {:.2f}'.format(inputs[i][0],inputs[i][1],pred[i]))

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

