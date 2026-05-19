#!/usr/bin/python3
# jiri kvita
# Tue 12 Oct 14:32:31 CEST 2021
# devel: Nov 2021, Apr 2023
# AI co-devel May 2026

from math import sqrt, pow, log, exp, fabs
import os, sys
import gc
from pathlib import Path
import shutil
import numpy as np
import matplotlib.pyplot as plt

# Keep Aesara import robust on systems without configured BLAS linker flags.
os.environ.setdefault('AESARA_FLAGS', 'blas__ldflags=')

# Aesara (Theano successor)
import aesara
import aesara.tensor as T
import aesara.tensor.nnet as nnet
from aesara import function, shared
from random import random
from random import uniform

# JK
from argvTools import parse_argv
from readTools import ReadData
from printAndPlotTools import PrintUnique, PlotWs, PlotCost, PlotDataAsHisto, PlotIndivDataAsHisto

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

    # for reading test data
    # STEERING: 
    # test set size!
    # images range ids i1..i2
    

    default_settings = {
        'ntested': 4000,
        'nIters': 200,
        'inputn1': 80,
        'inputn2': 40,
        'batch_size': 64,
        'gBatch': False,
        'gTag': '',
        'dataPath': os.environ.get('NN_DATA_PATH', 'data/by_class'),
    }

    settings = parse_argv(argv, default_settings)
    ntested = settings['ntested']
    nIters = settings['nIters']
    inputn1 = settings['inputn1']
    inputn2 = settings['inputn2']
    batch_size = settings['batch_size']
    gBatch = settings['gBatch']
    gTag = settings['gTag']
    dataPath = settings['dataPath']

    i1 = 0
    i2 = i1 + ntested

    # not controllable from cmd yet
    # Learning STEERING!
    learning_rate = 0.005 # 0.005 # 0.005
  
    print('*** Settings:')
    print('tag={:}, batch={:}'.format(gTag, gBatch))
    print('Loading...')
    print('')

    print(f'nIters: {nIters:}')
    print(f'ntested: {ntested:}')
    print(f'inputn1: {inputn1:}')
    print(f'inputn2: {inputn2:}')
    print(f'batch_size: {batch_size:}')
    print(f'dataPath: {dataPath}')

    # HACK!
    #return
    
    # IDEA:
    # create then layers and neurons in a loop
    # read train data and convert them into linear numpy vectors
    # define the output categories as hex of the corresponding chars
    # train the NN on the train data

    Ns = [inputn1, inputn2, 1]
    
    # STEERING WHAT CHARACTERS TO TRAIN ON! 
    hexcodes = [ #'30', '62', '41'
        
        
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
    print('Will train on characters with hex codes: {}'.format(hexcodes))
    
    ##################################################
    #           Step 1: Define variables             #
    ##################################################
    #x = aesara.tensor.fvector('x')
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
    print('*** Got image dimension base {}x{} = {}'.format(baseDimx, baseDimy, DIM))
    # lin dim for linearized img matrix

    # TODO: redesign the neurons structure so that the number of output neurons same as number of classes?
    # So far a smooth output within a range.

    expAmplif = 2. # 1.
    b0 = 1.
    useReLu = True
    
    # weights, constants, and node outputs
    ws = []
    bs = []
    aas = []
    # list to store stacked neurons a's from each layer
    # later, this can hold just x as initial data on the zeroth position
    stacked_aas = []

    # Ns = [5, 2, len(hexcodes) ]
    # DEFAULT:
    #Ns = [16, 16, 1]
    n0 = DIM
    n1 = Ns[0]
    n2 = Ns[1]
    n3 = Ns[2]
    print(f'*** Will train on a NN with {n0} input neurons, {n1} neurons in 1st hidden layer, {n2} neurons in 2nd hidden layer, and {n3} output neurons.')
    nTotal = n0*n1 + n1*n2 + n2*n3
    print(f'*** Total number of weights (parameters) in the model: {nTotal}')
    trainChars = 'train_'
    for code in hexcodes:
        trainChars =  trainChars + code
        if code != hexcodes[-1]:
            trainChars = trainChars + '_'
    
    # Include optional user tag in output naming so CLI tags affect produced artifacts.
    user_tag = f'_tag_{gTag}' if gTag else ''
    setupTag = f'{user_tag}_n1_{n1}_n2_{n2}_i1_{i1}_i2_{i2}_{trainChars}_nImgs_{ntested}_rate_{learning_rate:1.3f}'
    print(f'Train tag: {setupTag}')
    
    print('...defining first NN layer...')
    ilayer = 0
    bs.append( shared(1.*b0) )
    ws.append([])
    aas.append([])

    # initial random weigths limits:
    wmin = -1.
    wmax = +1.
    randDamp = 0.8 # 1.
    
    for i in range(0,n1):
        # was: random()
        ws[ilayer].append( shared(np.array([ randDamp*uniform(wmin, wmax) for j in range(0,n0) ])) )

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
            aas[ilayer].append( nnet.relu(T.dot(x,ws[-1][i])-bs[-1]) )
    # due to algebraic purposes, T.stack needs a list as input
    stacked_aas.append(T.stack(aas[-1],axis=1))
    print('   ...defined first NN layer of {} neurons...'.format(len(aas[-1])))
    #print(aas[-1])

    print('...defining second NN layer...')
    ilayer = 1
    bs.append( shared(1.*b0) )
    ws.append([])
    aas.append([])
    for i in range(0, n2):
        ws[ilayer].append( shared(np.array([ randDamp*uniform(-1., 1.) for j in range(0,n1) ])) )
    for i in range(0,n2):
        if not useReLu:
            # sigmoid
            aas[ilayer].append ( 1/(1+expAmplif*T.exp(-T.dot(stacked_aas[-1],ws[-1][i])-bs[-1])) )
        else:
            # ReLu:
            aas[ilayer].append ( nnet.relu(T.dot(stacked_aas[-1],ws[-1][i])-bs[-1]) )
    stacked_aas.append(T.stack(aas[-1],axis=1))
    print('   ...defined second layer of {} neurons...'.format(len(aas[-1])))
    #print(aas[-1])

    print('...defining last single layer...')
    ilayer = 2
    bs.append( shared(1.*b0) )
    ws.append([])
    aas.append([])
    for i in range(0, n3):
        ws[ilayer].append( shared(np.array([ randDamp*uniform(-1., 1.) for j in range(0,n2) ])) )
    for i in range(0, n3):
        # if not useReLu:
        # LAST MUST BE SIGMOID!
        # sigmoid:
        aas[ilayer].append( 1/(1+expAmplif*T.exp(-T.dot(stacked_aas[-1],ws[-1][i])-bs[-1])) )
        # else:
        # ReLu:
        #    aas[ilayer].append( nnet.relu(T.dot(stacked_aas[-1],ws[-1][i])-bs[-1]) )
    print('   ...defined last layer of {} neurons...'.format(len(aas[-1])))
    # no need to stack;)

    # print random weights
    print('...printing the random initial weights...')
    #PrintWs(ws)
    #PrintBs(bs)
    PlotWs(ws, '_pre' + setupTag)

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
    # JK's chi2-like expression with finite guards to prevent NaN propagation.
    eps = 1e-8
    y_raw = aas[-1][-1]
    y_safe = T.switch(T.isnan(y_raw) | T.isinf(y_raw), 0.5, y_raw)
    y_safe = T.clip(y_safe, eps, 1. - eps)
    a_hat_safe = T.switch(T.isnan(a_hat) | T.isinf(a_hat), 0.5, a_hat)
    a_hat_safe = T.clip(a_hat_safe, eps, 1. - eps)
    cost = T.power(a_hat_safe - y_safe, 2).sum()

    # gradiends of weights:
    print('--- weight gradients ---')
    dws = []
    ng = len(ws)
    print('# of w\'s to go through: {}'.format(ng))
    for i in range(0, ng):
        print('  {}/{}'.format(i,ng))
        dws.append([])
        for j in range(0, len(ws[i])):
            grad_w = T.grad(cost, ws[i][j])
            # Replace non-finite gradients with zeros to avoid corrupting weights.
            grad_w = T.switch(T.isnan(grad_w) | T.isinf(grad_w), T.zeros_like(grad_w), grad_w)
            dws[-1].append(grad_w)

    # gradiends of constant terms:
    print('--- const. terms gradients ---')
    dbs = []
    ng = len(bs)
    print('# of b\'s to go through: {}'.format(ng))
    for i in range(0, ng):
        print('  {}/{}'.format(i,ng))
        grad_b = T.grad(cost, bs[i])
        grad_b = T.switch(T.isnan(grad_b) | T.isinf(grad_b), T.zeros_like(grad_b), grad_b)
        dbs.append(grad_b)
        
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
    print('+++ defining the testing function  +++')
    predict = function(
        inputs = [x],
        outputs = aas[-1][-1]
    )
    # Keep a separate evaluator to compute loss on test sets when labels are available.
    evaluate = function(
        inputs = [x,a_hat],
        outputs = [aas[-1][-1],cost]
    )


    ##################################################
    #      Step 4: read the input data (images)      #
    ##################################################
    print('+++ reading images +++')
    # Preflight check to fail early with actionable guidance when dataset is missing.
    if not Path(dataPath).exists():
        print('ERROR: dataset path does not exist: {}'.format(dataPath))
        print('Hint: set --datapath=/path/to/by_class or export NN_DATA_PATH=/path/to/by_class')
        print('Expected layout: <dataPath>/<hex>/train_<hex>/train_<hex>_0000.png')
        return

    missing_classes = [hexcode for hexcode in hexcodes if not Path(dataPath, hexcode).exists()]
    if missing_classes:
        print('ERROR: dataset path is missing class directories: {}'.format(missing_classes))
        print('Hint: verify that your by_class dataset contains all requested hex class IDs.')
        return

    inputs, outputs = ReadData(hexcodes, i1, i2, cutoffx, cutoffy, rebinx, rebiny, baseDimx, dataPath=dataPath)
    inputs = np.asarray(inputs, dtype=np.float64)
    outputs = np.asarray(outputs, dtype=np.float64)
    #print('Outputs: ', outputs)
    print('*** Train outputs:')
    PrintUnique(outputs)
    
    ##################################################
    #            Step 5: train the model             #
    ##################################################
    
    print('*** Training the model, linearized data dimension is {} ***'.format(DIM))
    
    #Iterate through all inputs and find outputs:
    print('+++ Training: Iterating through inputs, finding outputs...{} times +++'.format(i2-i1))
    # Normalize by the actual number of loaded training samples, not per-class image count.
    n_train = len(inputs)
    if n_train == 0:
        print('ERROR: no training data loaded, stopping.')
        return
    if batch_size <= 0:
        print('ERROR: batch_size must be > 0, stopping.')
        return
    batch_size = min(batch_size, n_train)
    cost = []
    normcost = []
    
    for iteration in range(0, nIters):
        ###################################################
        #                   TRAINING                      #
        ###################################################
        perm = np.random.permutation(n_train)
        cost_iter = 0.
        pred = None
        for ibeg in range(0, n_train, batch_size):
            iend = min(ibeg + batch_size, n_train)
            idx = perm[ibeg:iend]
            batch_x = inputs[idx]
            batch_y = outputs[idx]
            pred, cost_batch = train(batch_x, batch_y)
            # Stop immediately when non-finite values appear to prevent NaN feedback loops.
            if (not np.isfinite(cost_batch)) or (not np.all(np.isfinite(pred))):
                print(f'ERROR: non-finite value detected at iteration {iteration}. Stopping training early.')
                return
            cost_iter = cost_iter + float(cost_batch)
        normcost_iter = cost_iter / float(n_train)
        if iteration % 10 == 0 or iteration <= 10:
            print('Trainig iteration {}/{}, cost: {:4.2f} cost/Nimgs: {:1.4f}'.format(iteration, nIters, cost_iter, normcost_iter))
        cost.append(cost_iter)
        normcost.append(normcost_iter)

    ####################################################################################################
    #           Step 6: test trained classifier on the initial inputs, aka Asimov;)
    ####################################################################################################


    # Print the outputs on the Asimov set:
    Asimov_results = []
    Asimov_resultsDict = {}
    print('+++ The Asimov outputs of the NN are: +++')
    # Re-evaluate full training set after mini-batch updates.
    pred = predict(inputs)
    classesPrinted = {}
    for i in range(len(inputs)):
        # print('The output for x1={} | stacked_aas={} is {:.2f}'.format(inputs[i][0],inputs[i][1],pred[i]))
        if not outputs[i] in classesPrinted:
            classesPrinted[outputs[i]] = pred[i]
            print('The Asimov output for true class {} is {:.2f}'.format(outputs[i],pred[i]))
        if not outputs[i] in  Asimov_resultsDict:
            Asimov_resultsDict[outputs[i]] = []
        Asimov_results.append(pred[i])
        Asimov_resultsDict[outputs[i]].append(pred[i])

    #print(Asimov_resultsDict)
    PlotCost(normcost, setupTag, 'Cost Evolution', 'red', 'dotted')
    PlotDataAsHisto(Asimov_results, 'Asimov_results', setupTag)
    PlotIndivDataAsHisto(Asimov_resultsDict, 'Asimov_results', setupTag)
    
    # print the final weights
    print('*** printing the final weights ***')
    #PrintWs(ws)
    #PrintBs(bs)
    PlotWs(ws, '_post' + setupTag)   

    # Free large training-phase containers before loading test data.
    del inputs, outputs, pred, Asimov_results, Asimov_resultsDict, classesPrinted, cost, normcost
    gc.collect()

    
    ##################################################
    #           Step 7: test on new inputs!          #
    ##################################################

    i1 = 1*i2
    i2 = i1 + ntested # 500+i2
    test_inputs, test_outputs = ReadData(hexcodes, i1, i2, cutoffx, cutoffy, rebinx, rebiny, baseDimx, False, -1, dataPath)
    print('*** Test outputs:')
    PrintUnique(test_outputs)
    test_results = []

    # create also NN output histograms for individual characters
    test_resultsDict = {}
    
    test_pred, test_cost = evaluate(test_inputs, test_outputs)
    NcorrectDict = {}
    NallDict = {}
    nAll = 0
    nCorrect = 0
    # window half-width to judge correct result on the train set
    correctCut = 0.10

    # Map scalar target values back to class IDs so per-class stats are label-driven.
    nhex = len(hexcodes)
    nnoutmax = 1.
    nnoutmin = 0.
    delta = 0.1
    sep = (nnoutmax - nnoutmin) / nhex
    value_to_hex = {}
    for ihex, hexcode in enumerate(hexcodes):
        class_value = nnoutmin + ihex*sep + delta
        value_to_hex[class_value] = hexcode
    
    for i in range(len(test_inputs)):
        # print('The output for x1={} | stacked_aas={} is {:.2f}'.format(inputs[i][0],inputs[i][1],pred[i]))
        # print('The output for true class {} is predicted as {:.2f}'.format(test_outputs[i],test_pred[i]))
        diff = test_outputs[i] - test_pred[i]
        # print(NallDict)
        nAll = nAll + 1
        # Use the nearest encoded target value to avoid fragile assumptions about sample ordering.
        key = min(value_to_hex.items(), key=lambda kv: abs(kv[0] - test_outputs[i]))[1]
        if not key in NallDict:
            NallDict[key] = 1
            NcorrectDict[key] = 0
        else:
            NallDict[key] = NallDict[key] + 1
        if not key in  test_resultsDict:
            test_resultsDict[key] = []
        if abs(diff) < correctCut:
            NcorrectDict[key] = NcorrectDict[key] + 1
            nCorrect = nCorrect + 1
            
        test_resultsDict[key].append(test_pred[i])
        test_results.append(test_pred[i])


    fracDict = {}
    frac = []
    print(NallDict)
    print(NcorrectDict)
    for key in NallDict:
        fracDict[key] = (1.*NcorrectDict[key]) / (1.*NallDict[key])
        frac.append(fracDict[key])
        print('Fraction of correct classification for class {} is {}'.format(key, fracDict[key]))
    print(fracDict)
    # Guard against empty test input to avoid division by zero.
    total_frac = (nCorrect / float(nAll)) if nAll else 0.
    print('Total correct fraction: {}/{} = {}'.format(nCorrect, nAll, total_frac ))

    PlotDataAsHisto(test_results, 'test_results', setupTag)
    PlotIndivDataAsHisto(test_resultsDict, 'test_results', setupTag)

    # plot the accuracies:
    PlotCost(frac, setupTag, 'accuracies', 'black', 'solid', 'Char ID', 'Accuracy')

    # print to ascii
    sumfrac = sum(frac)
    outfile = open(f'accuracies{setupTag}_sum_{sumfrac:1.3f}.txt', 'w')
    outfile.write('CharHexID : accuracy\n')
    for key,frac in fracDict.items():
        outfile.write(f'{key} : {frac:1.3f}\n')
    outfile.write(f'Sum : {sumfrac:1.3f}\n')
    outfile.write('Total correct fraction: {}/{} = {:1.3f}'.format(nCorrect, nAll, total_frac ) + '\n')
    outfile.close()
    
    if not gBatch:
        plt.show()

    # Move generated artifacts safely with Python APIs instead of shell commands.
    results_dir = Path(f'results{setupTag}')
    results_dir.mkdir(exist_ok=True)
    for artifact in Path('.').glob(f'*{setupTag}*.*'):
        if artifact.is_file():
            shutil.move(str(artifact), str(results_dir / artifact.name))
    
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

