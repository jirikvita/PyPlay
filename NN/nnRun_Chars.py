#!/usr/bin/python
# jiri kvita
# Tue 12 Oct 14:32:31 CEST 2021
# devel: Nov 2021, Apr 2023
# AI co-devel May 2026

from math import sqrt, pow, log, exp, fabs
import os, sys
import gc
from pathlib import Path
import shutil
import json
import csv
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
from plot_train_vs_onnx_scatter import plot_train_vs_onnx_scatter

stuff = []


def _pack_weights(ws, bs):
    """Pack per-neuron shared weights into dense matrices and scalar biases."""
    w1 = np.column_stack([w.get_value() for w in ws[0]]).astype(np.float32)
    w2 = np.column_stack([w.get_value() for w in ws[1]]).astype(np.float32)
    w3 = np.column_stack([w.get_value() for w in ws[2]]).astype(np.float32)
    b1 = np.array(float(bs[0].get_value()), dtype=np.float32)
    b2 = np.array(float(bs[1].get_value()), dtype=np.float32)
    b3 = np.array(float(bs[2].get_value()), dtype=np.float32)
    return w1, w2, w3, b1, b2, b3


def save_trained_model(ws, bs, setupTag, model_meta):
    """Save trained parameters and metadata with tag-aware filenames."""
    w1, w2, w3, b1, b2, b3 = _pack_weights(ws, bs)
    params_file = Path(f'model_params{setupTag}.npz')
    np.savez(
        params_file,
        w1=w1,
        w2=w2,
        w3=w3,
        b1=b1,
        b2=b2,
        b3=b3,
    )
    meta_file = Path(f'model_meta{setupTag}.json')
    with meta_file.open('w') as out:
        json.dump(model_meta, out, indent=2, sort_keys=True)
    print(f'Saved trained model parameters to {params_file}')
    print(f'Saved trained model metadata to {meta_file}')
    return params_file, meta_file


def export_onnx_model(ws, bs, setupTag, model_meta):
    """Export current MLP to ONNX if onnx package is available."""
    try:
        import onnx
        from onnx import helper, TensorProto, numpy_helper
    except Exception as ex:
        print(f'WARNING: ONNX export skipped (onnx package unavailable): {ex}')
        return None

    w1, w2, w3, b1, b2, b3 = _pack_weights(ws, bs)
    exp_amplif = float(model_meta['expAmplif'])
    use_relu = bool(model_meta['useReLu'])
    input_dim = int(model_meta['n0'])
    output_dim = int(model_meta['n3'])

    shift = np.array([-np.log(exp_amplif)], dtype=np.float32)
    one = np.array([1.0], dtype=np.float32)

    initializers = [
        numpy_helper.from_array(w1, name='W1'),
        numpy_helper.from_array(w2, name='W2'),
        numpy_helper.from_array(w3, name='W3'),
        numpy_helper.from_array(b1, name='b1'),
        numpy_helper.from_array(b2, name='b2'),
        numpy_helper.from_array(b3, name='b3'),
        numpy_helper.from_array(shift, name='sig_shift'),
        numpy_helper.from_array(one, name='one_const'),
    ]

    nodes = []
    nodes.append(helper.make_node('MatMul', ['x', 'W1'], ['z1_mm'], name='matmul_1'))
    if use_relu:
        nodes.append(helper.make_node('Sub', ['z1_mm', 'b1'], ['z1_pre'], name='sub_b1'))
        nodes.append(helper.make_node('Relu', ['z1_pre'], ['h1'], name='relu_1'))
    else:
        nodes.append(helper.make_node('Add', ['z1_mm', 'b1'], ['z1_pre'], name='add_b1'))
        nodes.append(helper.make_node('Add', ['z1_pre', 'sig_shift'], ['z1_shift'], name='sig_shift_1'))
        nodes.append(helper.make_node('Sigmoid', ['z1_shift'], ['h1'], name='sigmoid_1'))

    nodes.append(helper.make_node('MatMul', ['h1', 'W2'], ['z2_mm'], name='matmul_2'))
    if use_relu:
        nodes.append(helper.make_node('Sub', ['z2_mm', 'b2'], ['z2_pre'], name='sub_b2'))
        nodes.append(helper.make_node('Relu', ['z2_pre'], ['h2'], name='relu_2'))
    else:
        nodes.append(helper.make_node('Add', ['z2_mm', 'b2'], ['z2_pre'], name='add_b2'))
        nodes.append(helper.make_node('Add', ['z2_pre', 'sig_shift'], ['z2_shift'], name='sig_shift_2'))
        nodes.append(helper.make_node('Sigmoid', ['z2_shift'], ['h2'], name='sigmoid_2'))

    nodes.append(helper.make_node('MatMul', ['h2', 'W3'], ['z3_mm'], name='matmul_3'))
    # Output layer is always sigmoid in training and uses dot + b inside the exponent.
    nodes.append(helper.make_node('Add', ['z3_mm', 'b3'], ['z3_pre'], name='add_b3'))
    nodes.append(helper.make_node('Add', ['z3_pre', 'sig_shift'], ['z3_shift'], name='sig_shift_3'))
    nodes.append(helper.make_node('Sigmoid', ['z3_shift'], ['y'], name='sigmoid_3'))

    inputs = [helper.make_tensor_value_info('x', TensorProto.FLOAT, ['N', input_dim])]
    outputs = [helper.make_tensor_value_info('y', TensorProto.FLOAT, ['N', output_dim])]

    graph = helper.make_graph(
        nodes,
        f'nn_chars{setupTag}',
        inputs,
        outputs,
        initializer=initializers,
    )
    model = helper.make_model(
        graph,
        producer_name='nnRun_Chars.py',
        opset_imports=[helper.make_operatorsetid('', 13)],
    )

    # Persist preprocessing and label-encoding settings inside the ONNX file
    # so downstream inference can apply exactly the same data preparation.
    onnx_meta = {
        'setupTag': str(model_meta.get('setupTag', '')),
        'dataPath': str(model_meta.get('dataPath', 'data/by_class')),
        'cutoffx': str(model_meta.get('cutoffx', '')),
        'cutoffy': str(model_meta.get('cutoffy', '')),
        'rebinx': str(model_meta.get('rebinx', '')),
        'rebiny': str(model_meta.get('rebiny', '')),
        'baseDimx': str(model_meta.get('baseDimx', '')),
        'baseDimy': str(model_meta.get('baseDimy', '')),
        'preprocessThr': str(model_meta.get('preprocessThr', 0.5)),
        'labelNnoutmin': str(model_meta.get('labelNnoutmin', 0.0)),
        'labelNnoutmax': str(model_meta.get('labelNnoutmax', 1.0)),
        'labelDelta': str(model_meta.get('labelDelta', 0.1)),
    }
    helper.set_model_props(model, onnx_meta)

    onnx.checker.check_model(model)
    onnx_file = Path(f'model{setupTag}.onnx')
    onnx.save(model, str(onnx_file))
    print(f'Exported ONNX model to {onnx_file}')
    return onnx_file


def plot_confusion_matrix_half_sep(true_outputs, pred_outputs, hexcodes, class_values, subset_name, setup_tag):
    """Plot confusion matrix using class boundaries at half-distance between expected outputs."""
    true_arr = np.asarray(true_outputs, dtype=float).reshape(-1)
    pred_arr = np.asarray(pred_outputs, dtype=float).reshape(-1)
    if len(true_arr) == 0 or len(pred_arr) == 0:
        print(f'WARNING: empty arrays for confusion matrix on {subset_name}, skipping plot.')
        return

    n = min(len(true_arr), len(pred_arr))
    true_arr = true_arr[:n]
    pred_arr = pred_arr[:n]

    boundaries = [0.5 * (class_values[i] + class_values[i + 1]) for i in range(len(class_values) - 1)]
    true_idx = np.digitize(true_arr, boundaries)
    pred_idx = np.digitize(pred_arr, boundaries)

    ncls = len(hexcodes)
    cm = np.zeros((ncls, ncls), dtype=int)
    for it, ip in zip(true_idx, pred_idx):
        cm[int(it), int(ip)] = cm[int(it), int(ip)] + 1

    plt.figure(figsize=(8, 7))
    cm_plot = np.log1p(cm.astype(float))
    plt.imshow(cm_plot, interpolation='nearest', cmap='hot_r')
    plt.title(f'confusion_matrix_{subset_name}')
    cbar = plt.colorbar()
    cbar.set_label('log(1+N)')
    ticks = np.arange(ncls)
    plt.xticks(ticks, hexcodes, rotation=45)
    plt.yticks(ticks, hexcodes)
    plt.gca().invert_yaxis()
    plt.xlabel('Predicted class')
    plt.ylabel('True class')
    plt.tight_layout()
    plt.savefig(f'confusion_matrix_{subset_name.lower()}{setup_tag}.png')
    plt.savefig(f'confusion_matrix_{subset_name.lower()}{setup_tag}.pdf')
    plt.close()

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
        'ntested': 25000, #number of images for each category to read and test on (starting from i1)
        'nIters': 100, # numebr of training iterations (epochs)
        'inputn1': 150, # numnber of neurons in the 1st hidden layer
        'inputn2': 150, # numnber of neurons in the 2nd hidden layer
        'batch_size': 64,
        'gBatch': True,
        'runOnnxTrainEval': True,
        'useFullTrainSet': False,
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
    runOnnxTrainEval = settings['runOnnxTrainEval']
    useFullTrainSet = settings['useFullTrainSet']
    gTag = settings['gTag']
    dataPath = settings['dataPath']

    i1 = 0
    i2 = i1 + ntested

    # not controllable from cmd yet
    # Learning STEERING!
    learning_rate = 0.005 # 0.005 # 0.005
  
    print('*** Settings:')
    print('tag={:}, batch={:}'.format(gTag, gBatch))
    hostname = os.environ.get('HOSTNAME', '')
    # Always produce plot files; only interactive display is conditional.
    do_plots = True
    no_plot_show = gBatch or (hostname == 'zubr')
    if gBatch:
        print('Batch mode enabled: plots will be saved, interactive display disabled.')
    elif hostname == 'zubr':
        print('Running on zubr: interactive plot display disabled (saving files only).')
    print('Loading...')
    print('')

    print(f'nIters: {nIters:}')
    print(f'ntested: {ntested:}')
    print(f'inputn1: {inputn1:}')
    print(f'inputn2: {inputn2:}')
    print(f'batch_size: {batch_size:}')
    print(f'runOnnxTrainEval: {runOnnxTrainEval:}')
    print(f'useFullTrainSet: {useFullTrainSet:}')
    print(f'dataPath: {dataPath}')

    # HACK!
    #return
    
    # IDEA:
    # create then layers and neurons in a loop
    # read train data and convert them into linear numpy vectors
    # define the output categories as hex of the corresponding chars
    # train the NN on the train data

    # later try: Ns = [inputn1, inputn2, len(hexcodes) ]
    Ns = [inputn1, inputn2, 1]
    
    # STEERING WHAT CHARACTERS TO TRAIN ON! 
    hexcodes = [ #'30', '62', '41'
        '31', # 1
        '32', # 2
        '33', # 3
        '34', # 4
        '35', # 5
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
    preprocessThr = 0.5
    b0 = 1.
    useReLu = True
    
    # weights, constants, and node outputs
    ws = []
    bs = []
    aas = []
    # list to store stacked neurons a's from each layer
    # later, this can hold just x as initial data on the zeroth position
    stacked_aas = []


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
    setupTag = f'{user_tag}_n1_{n1}_n2_{n2}_i1_{i1}_i2_{i2}_{trainChars}_nImgs_{ntested}_iters_{nIters}_bs_{batch_size}_rate_{learning_rate:1.3f}'
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
    if do_plots:
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

    inputs, outputs = ReadData(hexcodes, i1, i2, cutoffx, cutoffy, rebinx, rebiny, baseDimx, dataPath=dataPath, thr=preprocessThr)
    inputs = np.asarray(inputs, dtype=np.float64)
    outputs = np.asarray(outputs, dtype=np.float64)
    #print('Outputs: ', outputs)
    print('*** Train outputs:')
    PrintUnique(outputs)

    n_loaded = len(inputs)
    if n_loaded == 0:
        print('ERROR: no training data loaded, stopping.')
        return

    if useFullTrainSet:
        train_inputs = inputs
        train_outputs = outputs
        val_inputs = np.asarray([], dtype=np.float64)
        val_outputs = np.asarray([], dtype=np.float64)
        train_abs_ids = np.arange(i1, i1 + n_loaded)
        print('Using full training set: {}/{} train, {}/{} validation'.format(
            len(train_inputs), n_loaded, 0, n_loaded
        ))
    else:
        if n_loaded < 2:
            print('WARNING: less than 2 training samples loaded; cannot create 20% validation split.')
            n_val = 0
        else:
            n_val = int(round(0.2 * n_loaded))
            n_val = max(1, min(n_val, n_loaded - 1))

        split_perm = np.random.permutation(n_loaded)
        val_idx = split_perm[:n_val]
        train_idx = split_perm[n_val:]
        train_inputs = inputs[train_idx]
        train_outputs = outputs[train_idx]
        val_inputs = inputs[val_idx]
        val_outputs = outputs[val_idx]
        train_abs_ids = i1 + train_idx
        print('Training/Validation split: {}/{} train, {}/{} validation'.format(
            len(train_inputs), n_loaded, len(val_inputs), n_loaded
        ))
    
    ##################################################
    #            Step 5: train the model             #
    ##################################################
    
    print('*** Training the model, linearized data dimension is {} ***'.format(DIM))
    
    #Iterate through all inputs and find outputs:
    print('+++ Training: Iterating through inputs, finding outputs...{} times +++'.format(i2-i1))
    # Normalize by the actual number of loaded training samples, not per-class image count.
    n_train = len(train_inputs)
    if n_train == 0:
        print('ERROR: no training samples left after validation split, stopping.')
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
            batch_x = train_inputs[idx]
            batch_y = train_outputs[idx]
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
    # Re-evaluate train subset after mini-batch updates.
    pred = predict(train_inputs)
    classesPrinted = {}
    train_NcorrectDict = {}
    train_NallDict = {}
    train_nAll = 0
    train_nCorrect = 0
    # window half-width to judge correct result on both train and test sets
    correctCut = 0.10
    # Map scalar target values back to class IDs so per-class stats are label-driven.
    nhex = len(hexcodes)
    nnoutmax = 1.
    nnoutmin = 0.
    delta = 0.1
    sep = (nnoutmax - nnoutmin) / nhex
    value_to_hex = {}
    class_values = []
    for ihex, hexcode in enumerate(hexcodes):
        class_value = nnoutmin + ihex*sep + delta
        class_values.append(class_value)
        value_to_hex[class_value] = hexcode

    for i in range(len(train_inputs)):
        # print('The output for x1={} | stacked_aas={} is {:.2f}'.format(train_inputs[i][0],train_inputs[i][1],pred[i]))
        if not train_outputs[i] in classesPrinted:
            classesPrinted[train_outputs[i]] = pred[i]
            print('The Asimov output for true class {} is {:.2f}'.format(train_outputs[i],pred[i]))
        if not train_outputs[i] in  Asimov_resultsDict:
            Asimov_resultsDict[train_outputs[i]] = []
        Asimov_results.append(pred[i])
        Asimov_resultsDict[train_outputs[i]].append(pred[i])
        diff = train_outputs[i] - pred[i]
        key = min(value_to_hex.items(), key=lambda kv: abs(kv[0] - train_outputs[i]))[1]
        if not key in train_NallDict:
            train_NallDict[key] = 1
            train_NcorrectDict[key] = 0
        else:
            train_NallDict[key] = train_NallDict[key] + 1
        train_nAll = train_nAll + 1
        if abs(diff) < correctCut:
            train_NcorrectDict[key] = train_NcorrectDict[key] + 1
            train_nCorrect = train_nCorrect + 1

    # Save per-event training predictions for the first Ndetailes events in each class.
    Ndetailes = 100
    train_detail_rows = []
    train_detail_count = {hexcode: 0 for hexcode in hexcodes}
    for i in range(len(train_inputs)):
        key = min(value_to_hex.items(), key=lambda kv: abs(kv[0] - train_outputs[i]))[1]
        if train_detail_count[key] >= Ndetailes:
            continue
        train_detail_rows.append([
            int(train_abs_ids[i]),
            key,
            float(train_outputs[i]),
            float(pred[i]),
            float(train_outputs[i] - pred[i]),
        ])
        train_detail_count[key] = train_detail_count[key] + 1

    train_details_csv = Path(f'train_event_details_N{Ndetailes}{setupTag}.csv')
    with train_details_csv.open('w', newline='') as out:
        writer = csv.writer(out)
        writer.writerow(['event_abs_i', 'true_hex_class', 'target_value', 'classifier_output', 'diff_target_minus_output'])
        writer.writerows(train_detail_rows)
    print(f'Saved training event details to {train_details_csv}')

    train_fracDict = {}
    train_frac = []
    for hexcode in hexcodes:
        train_all = train_NallDict.get(hexcode, 0)
        train_ok = train_NcorrectDict.get(hexcode, 0)
        train_acc = (1.*train_ok / train_all) if train_all else 0.
        train_fracDict[hexcode] = train_acc
        train_frac.append(train_acc)
        print('Fraction of correct TRAIN classification for class {} is {}'.format(hexcode, train_acc))
    train_total_frac = (train_nCorrect / float(train_nAll)) if train_nAll else 0.
    print('Total TRAIN correct fraction: {}/{} = {}'.format(train_nCorrect, train_nAll, train_total_frac))

    val_results = []
    val_resultsDict = {}
    val_fracDict = {hexcode: 0. for hexcode in hexcodes}
    val_frac = [0. for _ in hexcodes]
    val_nAll = 0
    val_nCorrect = 0
    val_total_frac = 0.
    if len(val_inputs):
        print('+++ Evaluating held-out VALIDATION subset (20% of original train pool) +++')
        val_pred, val_cost = evaluate(val_inputs, val_outputs)
        val_NallDict = {}
        val_NcorrectDict = {}
        for i in range(len(val_inputs)):
            diff = val_outputs[i] - val_pred[i]
            key = min(value_to_hex.items(), key=lambda kv: abs(kv[0] - val_outputs[i]))[1]
            val_nAll = val_nAll + 1
            if not key in val_NallDict:
                val_NallDict[key] = 1
                val_NcorrectDict[key] = 0
            else:
                val_NallDict[key] = val_NallDict[key] + 1
            if not key in val_resultsDict:
                val_resultsDict[key] = []
            if abs(diff) < correctCut:
                val_NcorrectDict[key] = val_NcorrectDict[key] + 1
                val_nCorrect = val_nCorrect + 1
            val_resultsDict[key].append(val_pred[i])
            val_results.append(val_pred[i])

        for hexcode in hexcodes:
            nall = val_NallDict.get(hexcode, 0)
            ncorrect = val_NcorrectDict.get(hexcode, 0)
            val_fracDict[hexcode] = (1.*ncorrect / nall) if nall else 0.
            val_frac[hexcodes.index(hexcode)] = val_fracDict[hexcode]
            print('Fraction of correct VALIDATION classification for class {} is {}'.format(hexcode, val_fracDict[hexcode]))
        val_total_frac = (val_nCorrect / float(val_nAll)) if val_nAll else 0.
        print('Total VALIDATION correct fraction: {}/{} = {}'.format(val_nCorrect, val_nAll, val_total_frac))
        print('Validation cost: {}'.format(float(val_cost)))

    #print(Asimov_resultsDict)
    if do_plots:
        PlotCost(normcost, setupTag, 'Cost Evolution', 'red', 'dotted')
        PlotDataAsHisto(Asimov_results, 'Asimov_results', setupTag)
        PlotIndivDataAsHisto(Asimov_resultsDict, 'Asimov_results', setupTag)
        PlotCost(train_frac, setupTag, 'train_accuracies', 'blue', 'solid', 'Char ID', 'Accuracy')
        plot_confusion_matrix_half_sep(train_outputs, pred, hexcodes, class_values, 'train', setupTag)
        if len(val_inputs):
            PlotDataAsHisto(val_results, 'validation_results', setupTag)
            PlotIndivDataAsHisto(val_resultsDict, 'validation_results', setupTag)
            PlotCost(val_frac, setupTag, 'validation_accuracies', 'green', 'solid', 'Char ID', 'Accuracy')
    
    # print the final weights
    print('*** printing the final weights ***')
    #PrintWs(ws)
    #PrintBs(bs)
    if do_plots:
        PlotWs(ws, '_post' + setupTag)

    model_meta = {
        'setupTag': setupTag,
        'n0': n0,
        'n1': n1,
        'n2': n2,
        'n3': n3,
        'learning_rate': learning_rate,
        'expAmplif': expAmplif,
        'useReLu': useReLu,
        'useFullTrainSet': useFullTrainSet,
        'hexcodes': hexcodes,
        'cutoffx': cutoffx,
        'cutoffy': cutoffy,
        'rebinx': rebinx,
        'rebiny': rebiny,
        'baseDimx': baseDimx,
        'baseDimy': baseDimy,
        'preprocessThr': preprocessThr,
        'labelNnoutmin': nnoutmin,
        'labelNnoutmax': nnoutmax,
        'labelDelta': delta,
        'dataPath': dataPath,
    }
    _, meta_file = save_trained_model(ws, bs, setupTag, model_meta)
    onnx_file = export_onnx_model(ws, bs, setupTag, model_meta)
    results_dir = Path('results') / f'results{setupTag}'
    results_dir.mkdir(parents=True, exist_ok=True)

    if runOnnxTrainEval and onnx_file is not None:
        try:
            from run_onnx_same_dataset import run_onnx_on_same_dataset

            print('+++ running optional ONNX evaluation on TRAIN dataset +++')
            run_onnx_on_same_dataset(
                results_dir=results_dir,
                data_path=dataPath,
                i1=i1,
                i2=i2,
                batch_size=batch_size,
                correct_cut=correctCut,
                meta_file=meta_file,
                onnx_file=onnx_file,
                n_details=100,
                make_plots=do_plots,
            )
        except Exception as ex:
            print(f'WARNING: optional ONNX train-dataset evaluation failed: {ex}')

    # Free large training-phase containers before loading test data.
    del inputs, outputs, pred, Asimov_results, Asimov_resultsDict, classesPrinted, cost, normcost
    gc.collect()

    
    ##################################################
    #           Step 7: test on new inputs!          #
    ##################################################

    i1 = 1*i2
    i2 = i1 + ntested # 500+i2
    test_inputs, test_outputs = ReadData(hexcodes, i1, i2, cutoffx, cutoffy, rebinx, rebiny, baseDimx, False, -1, dataPath, thr=preprocessThr)
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
    for hexcode in hexcodes:
        nall = NallDict.get(hexcode, 0)
        ncorrect = NcorrectDict.get(hexcode, 0)
        fracDict[hexcode] = (1.*ncorrect / nall) if nall else 0.
        frac.append(fracDict[hexcode])
        print('Fraction of correct TEST classification for class {} is {}'.format(hexcode, fracDict[hexcode]))
    print(fracDict)
    # Guard against empty test input to avoid division by zero.
    total_frac = (nCorrect / float(nAll)) if nAll else 0.
    print('Total correct fraction: {}/{} = {}'.format(nCorrect, nAll, total_frac ))

    if do_plots:
        PlotDataAsHisto(test_results, 'test_results', setupTag)
        PlotIndivDataAsHisto(test_resultsDict, 'test_results', setupTag)
        plot_confusion_matrix_half_sep(test_outputs, test_pred, hexcodes, class_values, 'test', setupTag)

        # plot the accuracies:
        PlotCost(frac, setupTag, 'test_accuracies', 'black', 'solid', 'Char ID', 'Accuracy')
        plt.figure()
        xvals = range(1, len(hexcodes)+1)
        plt.plot(xvals, train_frac, 'o', color='blue', linewidth=1, markersize=4, linestyle='solid', label='train')
        if len(val_inputs):
            plt.plot(xvals, val_frac, 'o', color='green', linewidth=1, markersize=4, linestyle='solid', label='validation')
        plt.plot(xvals, frac, 'o', color='black', linewidth=1, markersize=4, linestyle='solid', label='test')
        plt.xticks(list(xvals), hexcodes)
        plt.xlabel('Char ID')
        plt.ylabel('Accuracy')
        plt.title('train_vs_validation_vs_test_accuracies')
        plt.ylim(0., 1.)
        plt.legend()
        plt.savefig(f'train_vs_validation_vs_test_accuracies{setupTag}.png')
        plt.savefig(f'train_vs_validation_vs_test_accuracies{setupTag}.pdf')

    # print to ascii
    sumfrac = sum(frac)
    outfile = open(f'accuracies{setupTag}_sum_{sumfrac:1.3f}.txt', 'w')
    outfile.write('CharHexID : accuracy\n')
    for key,frac in fracDict.items():
        outfile.write(f'{key} : {frac:1.3f}\n')
    outfile.write(f'Sum : {sumfrac:1.3f}\n')
    outfile.write('Total correct fraction: {}/{} = {:1.3f}'.format(nCorrect, nAll, total_frac ) + '\n')
    if len(val_inputs):
        outfile.write('Validation total correct fraction: {}/{} = {:1.3f}'.format(val_nCorrect, val_nAll, val_total_frac) + '\n')
    outfile.close()
    
    if do_plots and not no_plot_show:
        plt.show()

    # Move generated artifacts safely with Python APIs instead of shell commands.
    for artifact in Path('.').glob(f'*{setupTag}*.*'):
        if artifact.is_file():
            shutil.move(str(artifact), str(results_dir / artifact.name))
    for pattern in (f'ws_*_pre{setupTag}.png', f'ws_*_pre{setupTag}.pdf'):
        for artifact in Path('.').glob(pattern):
            if artifact.is_file():
                shutil.move(str(artifact), str(results_dir / artifact.name))

    if do_plots:
        try:
            plot_train_vs_onnx_scatter(
                results_dir=results_dir,
                show=(not no_plot_show),
            )
        except Exception as ex:
            print(f'WARNING: train-vs-onnx scatter plotting failed: {ex}')
    
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

