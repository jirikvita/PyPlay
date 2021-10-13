#!/usr/bin/python3

from PIL import Image

import numpy as np
from math import log10

# reading NIST hand written character data
# https://www.nist.gov/itl/products-and-services/emnist-dataset 
# https://www.nist.gov/srd/nist-special-database-19


########################################################################################
def MakeDigitStr(i, digits = 3):
    # from /home/qitek/Dropbox/work/Vyuka/SFVE/Poznamky_Cz/Toys/PeakSim/PeakSim.py
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


########################################################################################
# zoom using a symmetrical cutoff

def readPng(path, hexcode, imgid, cutoff = 32):

    # example full name: 'data/by_class/6e/train_6e/train_6e_04507.png'
    
    # 128x128 pixels
    image = Image.open('{}/{}/train_{}/train_{}_{}.png'.format(path, hexcode, hexcode, hexcode, imgid))
    image_array = np.array(image)

    nLines = len(image_array)
    
    # bw and inverted image;-)
    image_bw = []  #np.zeros(nLines*nLines)
    
    #print('Lines: {}'.format(nLines))

    iline = -1
    for line in image_array:
        iline = iline + 1
        if iline < cutoff or iline >= nLines - cutoff:
            continue
        #print(line)
        icol = -1
        for x in line:
            icol = icol + 1
            if icol < cutoff or icol >= nLines - cutoff:
                continue
            r,g,b = x[0], x[1], x[2]
            #print('r={} g={} b={}'.format(r,g,b))
            if r == 0 and g == 0 and b == 0:
                #print('...found black dot {} column {}'.format(iline, icol))
                #image_bw[iline*nLines + icol] = 1
                image_bw.append(1)
            else:
                image_bw.append(0)

    return image_bw

########################################################################################

def readImages(path, hexcode, i1, i2):
    imgs = []
    for i in range(i1, i2):
        imgid = MakeDigitStr(i, 4)
        print('reading img {}'.format(imgid))
        imgs.append (  readPng(path, hexcode, imgid) )
    return imgs

########################################################################################
########################################################################################
########################################################################################
