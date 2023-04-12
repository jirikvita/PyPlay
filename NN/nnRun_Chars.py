#!/usr/bin/python3
# jiri kvita
# Tue 12 Oct 14:32:31 CEST 2021
# devel: Nov 2021, Apr 2023


#from __future__ import print_function

# python
#import ROOT
from math import sqrt, pow, log, exp, fabs
import os, sys, getopt

# theano
# https://www.analyticsvidhya.com/blog/2016/04/neural-networks-python-theano/
import theano
import theano.tensor as T
from theano.ifelse import ifelse
from theano import function
from random import random
from random import uniform

# JK
from readTools import *

from printAndPlotTools import *

stuff = []

########################################################################################
########################################################################################
########################################################################################

def main(argv):

    # https://www.tutorialspoint.com/python/python_command_line_arguments.htm
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
    # images range ids i1..i2
    # DEFAULT:
    #i1, i2 = 70, 460
    i1, i2 = 200, 1800

    
    #i1, i2 = 70, 360
    #i1, i2 = 70, 210
    #i1, i2 = 70, 80
    #i1, i2 = 10, 10
    hexcodes = ['30', # 0 
                '31', # 1
                '32', # 2
                '33', # 3
                #'34', # 4
                #'35', # 5
                #'36', # 6
                #'37', # 7
                #'38', # 8
                #'39', # 9
                
                #'5a', # z
    ]

    ##################################################
    #           Step 1: Define variables             #
    ##################################################
    #x = theano.tensor.fvector('x')
    x = T.matrix('x')

    # crop cutoff factor rebinned data:
    # todo: seems it does not work for different x,y cutoffs?
    cutoffx,cutoffy = 16,20
    rebinx = 2
    rebiny = 2
    baseDimx = int(128  / rebinx) - 2*cutoffx
    baseDimy = int(128  / rebiny) - 2*cutoffy
    #fullDIM = baseDimx*baseDimy # hack
    DIM = baseDimx*baseDimy # hack
    print('Got image dimension {}'.format(DIM))
    # lin dim for linearized img matrix

    # TODO: redesign the neurons structure so that the number of output neurons same as number of classes?
    # So far a smooth output with a range.

    # Learning STEERING!
    learning_rate = 0.005 # 0.005
    expAmplif = 1. # 1.
    randDamp = 1. # 1.
    b0 = 1.
    nIters = 3000 # DEFAULT: 5000 # 8000
    useReLu = True
    
    # weights, constants, and node outputs
    ws = []
    bs = []
    aas = []
    # list to store stacked neurons a's from each layer
    # later, this can hold just x as initial data on the zeroth position
    stacked_aas = []
    
    # Ns = [5, 2, len(hexcodes) ]
    Ns = [16, 16, 1]
    n0 = DIM
    n1 = Ns[0]
    n2 = Ns[1]
    n3 = Ns[2]
    
    print('*** defining first NN layer ***')
    ilayer = 0
    bs.append( theano.shared(1.*b0) )
    ws.append([])
    aas.append([])
    for i in range(0,n1):
        # was: random()
        ws[ilayer].append( theano.shared(np.array([ randDamp*uniform(-1., 1.) for j in range(0,n0) ])) )

    ##################################################
    # Step 2: Define mathematical expression         #
    # activation funtion sigmoif 1/(1+exp()) or ReLu #
    ##################################################
    for i in range(0,n1):
        # sigmoid:
        if not useReLu:
            aas[ilayer].append( 1/(1+expAmplif*T.exp(-T.dot(x,ws[-1][i])-bs[-1])) )
        else:
            # ReLu:
            aas[ilayer].append( T.nnet.relu(T.dot(x,ws[-1][i])-bs[-1]) )
    # due to algebraic purposes, T.stack needs a list as input
    stacked_aas.append(T.stack(aas[-1],axis=1))
    print('*** defined first NN layer of {} neurons ***'.format(len(aas[-1])))
    #print(aas[-1])

    print('*** defining second NN layer ***')
    ilayer = 1
    bs.append( theano.shared(1.*b0) )
    ws.append([])
    aas.append([])
    for i in range(0, n2):
        ws[ilayer].append( theano.shared(np.array([ randDamp*uniform(-1., 1.) for j in range(0,n1) ])) )
    for i in range(0,n2):
        if not useReLu:
            # sigmoid
            aas[ilayer].append ( 1/(1+expAmplif*T.exp(-T.dot(stacked_aas[-1],ws[-1][i])-bs[-1])) )
        else:
            # ReLu:
            aas[ilayer].append ( T.nnet.relu(T.dot(stacked_aas[-1],ws[-1][i])-bs[-1]) )
    stacked_aas.append(T.stack(aas[-1],axis=1))
    print('*** defined second layer of {} neurons ***'.format(len(aas[-1])))
    #print(aas[-1])

    print('*** defining last single layer ***')
    ilayer = 2
    bs.append( theano.shared(1.*b0) )
    ws.append([])
    aas.append([])
    for i in range(0, n3):
        ws[ilayer].append( theano.shared(np.array([ randDamp*uniform(-1., 1.) for j in range(0,n2) ])) )
    for i in range(0, n3):
        # if not useReLu:
        # LAST MUST BE SIGMOID!
        # sigmoid:
        aas[ilayer].append( 1/(1+expAmplif*T.exp(-T.dot(stacked_aas[-1],ws[-1][i])-bs[-1])) )
        # else:
        # ReLu:
        #    aas[ilayer].append( T.nnet.relu(T.dot(stacked_aas[-1],ws[-1][i])-bs[-1]) )
    print('*** defined last layer of {} neurons ***'.format(len(aas[-1])))
    # no need to stack;)

    # print random weights
    print('*** printing the random initial weights ***')
    #PrintWs(ws)
    #PrintBs(bs)
    PlotWs(ws, '_pre')

    ##################################################
    #    Step 3: Define gradient and update rule     #
    ##################################################
    print('+++ defining gradients +++')
    a_hat = T.vector('a_hat') #Actual output
    # some tries:
    #cost = T.log(1.)
    #ng = len(aas[-1])
    #print('Last number of neurons: {}'.format(ng))
    #for i in range(0, ng):
    #    if i % 10 == 0:
    #        print('{}/{}'.format(i,ng))
    #    cost = cost + -(a_hat*T.log(aas[-1][i]) + (1.-a_hat)*T.log(1.-aas[-1][i])).sum()

    # original entropy cost function
    # Also known as Bernoulli negative log-likelihood and Binary Cross-Entropy
    # c.f. https://stats.stackexchange.com/questions/154879/a-list-of-cost-functions-used-in-neural-networks-alongside-applications
    #cost = -(a_hat*T.log(aas[-1][-1]) + (1.-a_hat)*T.log(1.-aas[-1][-1])).sum()
    # JK's chi2-like expression:
    cost = T.power(a_hat - aas[-1][-1], 2).sum()

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
        
    locupdates = [] # for training
    ng = len(ws)
    print('# of updates\'s to go through: {}'.format(ng))
    for i in range(0, ng):
        print('  {}/{}'.format(i,ng))
        for j in range(0, len(ws[i])):
            #print('    {}/{}'.format(j,len(ws[i])))
            locupdates.append( [ws[i][j], ws[i][j] - learning_rate*dws[i][j]] )
    for i in range(0, len(bs)):
        locupdates.append( [bs[i], bs[i] - learning_rate*dbs[i]] )
        # no learning nor updates anymore, will be used for testing on unlearned data;)

    print('+++ defining the training function +++')
    train = function(
        inputs = [x,a_hat],
        outputs = [aas[-1][-1],cost],
        updates = locupdates
    )
    print('+++ defining the testing function +++')
    predict = function(
        inputs = [x,a_hat],
        outputs = [aas[-1][-1],cost]
    )


    ##################################################
    #      Step 4: read the input data (images)      #
    ##################################################
    print('+++ reading images +++')
    inputs, outputs = ReadData(hexcodes, i1, i2, cutoffx, cutoffy, rebinx, rebiny, baseDimx)
   
    ##################################################
    #            Step 5: train the model             #
    ##################################################
    
    print('*** Training the model, linearized data dimension is {} ***'.format(DIM))
    
    #Iterate through all inputs and find outputs:
    print('+++ Training: Iterating through inputs, finding outputs...{} times +++'.format(i2-i1))
    cost = []

    for iteration in range(0, nIters):
        pred, cost_iter = train(inputs, outputs)
        if iteration % 200 == 0:
            print('Trainig iteration {}/{}, cost: {}'.format(iteration, nIters, cost_iter))
        cost.append(cost_iter)

    # Print the outputs on the training set:
    train_results = []
    print('+++ The training outputs of the NN are: +++')
    # printing last prediction pred
    classesPrinted = {}
    for i in range(len(inputs)):
        # print('The output for x1={} | stacked_aas={} is {:.2f}'.format(inputs[i][0],inputs[i][1],pred[i]))
        if not outputs[i] in classesPrinted:
            classesPrinted[outputs[i]] = pred[i]
            print('The training output for true class {} is {:.2f}'.format(outputs[i],pred[i]))
        train_results.append(pred[i])
        
    #Plot the flow of cost:
    print('\nThe flow of cost during model run is as following:')
    # matplotlib inline
    plt.plot(cost)
    plt.show()
    plt.savefig('NNout_n1_{}_n2_{}_imgRanges_i1_{}_i2_{}_rate_{:1.3f}.png'.format(n1, n2, i1, i2, learning_rate))

    PlotDataAsHisto(train_results, 'train_results')
    
    # print the final weights
    print('*** printing the final weights ***')
    #PrintWs(ws)
    #PrintBs(bs)
    PlotWs(ws, '_post')

    ##################################################
    #           Step 5: test on new inputs!          #
    ##################################################

    i1 =   1+i2
    i2 = 200+i2
    test_inputs, test_outputs = ReadData(hexcodes, i1, i2, cutoffx, cutoffy, rebinx, rebiny, baseDimx, False, -1)
    test_results = []

    # create also NN output histograms for individual characters
    test_resultsDict = {}
    
    test_pred, test_cost = predict(test_inputs, test_outputs)
    NcorrectDict = {}
    NallDict = {}
    nAll = 0
    nCorrect = 0
    correctCut = 0.10


    
    for i in range(len(test_inputs)):
        # print('The output for x1={} | stacked_aas={} is {:.2f}'.format(inputs[i][0],inputs[i][1],pred[i]))
        print('The output for true class {} is predicted as {:.2f}'.format(test_outputs[i],test_pred[i]))
        diff = test_outputs[i] - test_pred[i]
        #print(NallDict)
        nAll = nAll + 1
        if not test_outputs[i] in NallDict:
            NallDict[test_outputs[i]] = 1
            NcorrectDict[test_outputs[i]] = 0
        else:
            NallDict[test_outputs[i]] = NallDict[test_outputs[i]] + 1
        if not test_outputs[i] in  test_resultsDict:
            test_resultsDict[test_outputs[i]] = []
        if abs(diff) < correctCut:
            NcorrectDict[test_outputs[i]] = NcorrectDict[test_outputs[i]] + 1
            nCorrect = nCorrect + 1
            
        test_resultsDict[test_outputs[i]].append(test_pred[i])
        test_results.append(test_pred[i])


    frac = {}
    print(NallDict)
    print(NcorrectDict)
    for key in NallDict:
        frac[key] = (1.*NcorrectDict[key]) / (1.*NallDict[key])
        print('Fraction of correct classification for class {} is {}'.format(key, frac[key]))
    print(frac)
    print('Total correct fraction: {}/{} = {}'.format(nCorrect, nAll, nCorrect / (1.* nAll) ))

    PlotDataAsHisto(test_results, 'test_results')

    cols = ['yellow', 'green', 'blue', 'red', 'cyan', 'magenta', 'orange', 'pink', 'teal', 'grey']
    nb = 100
    x1 = 0.
    x2 = 1.
    icol = -1
    newFig = True
    for key,indiv_res in test_resultsDict.items():
        icol = icol + 1
        print('plottig individual {} of length {}'.format(key, len(indiv_res)))
        PlotDataAsHisto(indiv_res, 'test_results_split', newFig, nb, x1, x2, cols[icol])
        #PlotDataAsHisto(indiv_res, 'test_results' + str(key), nweFig, nb, x1, x2, cols[icol])
        newFig = False
        

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

