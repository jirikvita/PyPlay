#!/usr/bin/python3

# numpy and plotting
import matplotlib.pyplot as plt
import numpy as np


########################################################################################
def PlotDataAsHisto(data, title='', nbs = 200, xmin = 0., xmax = 1.):
    # https://www.tutorialspoint.com/numpy/numpy_histogram_using_matplotlib.htm
    #np.histogram(data, bins = [0,20,40,60,80,100]) 
    #hist,bins = np.histogram(data,bins = [0,20,40,60,80,100]) 
    #print(hist)
    #print(bins)
    dx = (xmax - xmin) / nbs
    plt.hist(data, bins = [dx * r for r in range(0,nbs+1)]) 
    plt.title(title) 
    plt.show()
    plt.savefig('{}.png'.format(title))

########################################################################################
def PrintWs(ws):
    print('...printing w\'s...')
    print('len(ws): {}'.format(len(ws)))
    iw = -1
    for w in ws:
        iw = iw+1
        print('len(w): {}'.format(len(w)))
        iww = -1
        for ww in w:
            iww = iww+1
            #print('len(ww): {}'.format(len(ww)))
            vals = ww.get_value()
            dim = len(vals)
            print('* Dim of ww{}{}: {}, data: '.format(iw, iww, dim), end='')
            #print(T.shape(ww))
            for i in range(0,dim):
                # slow:
                #print(ww[i].eval(), ' ', end='')
                # fast:
                print('{:1.2f} '.format(vals[i]), end='')
            print()
    return

########################################################################################
def PrintBs(bs):
    print('...printing b\'s...')
    print('len(bs): {}'.format(len(bs)))
    ib = -1
    for bb in bs:
        ib = ib+1
        #print('len(bb): {}'.format(len(bb)))
        vals = bb.get_value()
        print(vals)
    return

########################################################################################
def PlotWs(ws, tag=''):
    print('...plotting w\'s...')
    iw = -1

    figs = []
    for w in ws:
        ws_array = []
        iw = iw+1
        iww = -1
        for ww in w:
            iww = iww+1
            #print('len(ww): {}'.format(len(ww)))
            vals = ww.get_value()
            dim = len(vals)
            line = []
            #print(T.shape(ww))
            for i in range(0,dim):
                line.append(vals[i])
            ws_array.append(line)

        # https://stackoverflow.com/questions/16492830/colorplot-of-2d-array-matplotlib/16492880
        # inches:
        #fig = plt.figure(figsize=(6, 3.2))
        fig = plt.figure(figsize=(0.5 + 0.1*len(ws_array[0]), 0.5 + 0.1*len(ws_array)))
            
        ax = fig.add_subplot(111)
        ax.set_title('colorMap')
        #print(ws_array)
        plt.imshow(ws_array)
        ax.set_aspect('equal')
        
        #cax = fig.add_axes([0.12, 0.1, 0.78, 0.8])
        #cax.get_xaxis().set_visible(False)
        #cax.get_yaxis().set_visible(False)
        #cax.patch.set_alpha(0)
        #cax.set_frame_on(False)
        plt.colorbar(orientation='vertical')
        #plt.show()
        plt.savefig('ws_{}{}.png'.format(iw, tag))

        figs.append(plt)
    return
