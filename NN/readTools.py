#!/usr/bin/python3

from PIL import Image

import numpy as np
from math import log10

# reading NIST hand written character data
# https://www.nist.gov/itl/products-and-services/emnist-dataset 
# https://www.nist.gov/srd/nist-special-database-19


########################################################################################
def MakeDigitStr(i, digits = 3):
    tag = str(i)
    n = digits
    try: 
        n = int(log10(i))
    except ValueError:
        pass
    if i == 0:
        n = 0
    for i in range(0, digits - n):
        tag = '0' + tag
    return tag


########################################################################################
def PrintImg2DInv(img, thr = 0.25):
    for xline in img:
        line = ''
        for rgb in xline:
            sstr = '\u2588'
            r,g,b = rgb[0], rgb[1], rgb[2]
            if 3. - (r+b+b) < thr:
                sstr = ' '
            line = line + sstr
        print(line)
    return

########################################################################################
def PrintImgFrom1D(img, ndimx, doprint):
    i = -1
    j = -1
    line = ''
    lines = []
    for pix in img:
        i = i+1
        sstr = '\u2588'
        if pix > 0:
            sstr = ' '
        line = line + str(sstr)
        if (i+1) % ndimx == 0:
            j = j+1
            if doprint:
                print(line)
            lines.append(line + '')
            line = ''
    return lines

########################################################################################
def PutLineNextToLine(linesToPrint, imglines, sep = ' '):
    iline = -1
    for imgline in imglines:
        iline = iline+1
        if len(linesToPrint) <= iline:
            linesToPrint.append('' + imgline)
        else:
            linesToPrint[iline] = linesToPrint[iline] + sep + imgline
    return linesToPrint

########################################################################################
def PrettyPrint(arrayToPrint):
    for line in arrayToPrint:
        print(line)
    return
    
########################################################################################
# zoom using a symmetrical cutoff

def readPng(path, hexcode, imgid, cutoffx, cutoffy, rebinx, rebiny, thr = 0.5):

    # example full name: 'data/by_class/6e/train_6e/train_6e_04507.png'
    
    # 128x128 pixels
    image = Image.open('{}/{}/train_{}/train_{}_{}.png'.format(path, hexcode, hexcode, hexcode, imgid))
    image_array_orig = np.array(image)
    image_array = image_array_orig 
    
    if rebinx > 0 and rebiny > 0:
        image_array = Rebin2DRGBArray(image_array_orig , rebinx, rebiny)
    
    nLines = len(image_array)
    
    # bw and inverted image;-)
    image_bw = []  #np.zeros(nLines*nLines)
    
    #print('Lines: {}'.format(nLines))

    iline = -1
    for line in image_array:
        iline = iline + 1
        if iline < cutoffy or iline >= nLines - cutoffy:
            continue
        #print(line)
        icol = -1
        nCols = len(line)
        for x in line:
            icol = icol + 1
            if icol < cutoffx or icol >= nCols - cutoffx:
                continue
            r,g,b = x[0], x[1], x[2]
            #print('r={} g={} b={}'.format(r,g,b))
            if r <= thr and g <= thr and b <= thr:
                #print('...found black dot {} column {}'.format(iline, icol))
                #image_bw[iline*nLines + icol] = 1
                #image_bw.append(3. - r - g - b)
                image_bw.append(1.)
            else:
                image_bw.append(0)

    return image_bw

########################################################################################
def Rebin2DRGBArray(data, rebinx = 2, rebiny = 2, doAver = True):
    newdata = []
    # todo: check dimension on each line and divisibility by rebin factors?
    for i in range(0, int(len(data)/rebinx)):
        line = []
        for j in range(0, int(len(data[0])/rebiny)):
            # loop over rgb:
            vals = []
            ncols = len(data[0][0])
            for icol in range(0,ncols):
                val = 0.
                n = 0
                for ii in range(0,rebinx):
                    for jj in range(0,rebiny):
                        val = val + data[i*rebinx+ii][j*rebiny+jj][icol]
                        n = n+1
                if doAver:
                    vals.append(val/(1.*n))
                else:
                    vals.append(val)
            line.append(vals)
        newdata.append(line)
    return newdata


########################################################################################
def readImages(path, hexcode, i1, i2, cutoffx, cutoffy, rebinx = -1, rebiny = -1):
    imgs = []
    for i in range(i1, i2):
        imgid = MakeDigitStr(i, 4)
        #print('reading img {}'.format(imgid))
        img = readPng(path, hexcode, imgid, cutoffx, cutoffy, rebinx, rebiny)
        imgs.append ( img )
    return imgs


########################################################################################
def ReadData(hexcodes, i1, i2, cutoffx, cutoffy, rebinx, rebiny, baseDimx, toTrain = True, nExampleCharsToPrint = 3): 
    inputs = []
    outputs = []
    nhex = len(hexcodes)
    nnoutmax = 1.
    nnoutmin = 0.
    delta = 0.1 ###!!! was: 0.1
    ihex = -1

    sep = (nnoutmax - nnoutmin) / (nhex)
    print('separation for outputs: {:1.3f}'.format(sep))
    for hexcode in hexcodes:
        ihex = ihex+1
        # need to normalize this to be between 0 and 1;)
        #hexout = int(hexcode, 16) / 128.
        hexout = nnoutmin + ihex*sep + delta
        if hexout > 1.:
            print('ERROR: required output for {} is {}, i.e. above 1!'.format(ihex, hexout))
        imgs = readImages('data/by_class/', hexcode, i1, i2, cutoffx, cutoffy, rebinx, rebiny)
        iimg = -1
        print('will add images for class {} with output {:1.4f}'.format(hexcode, hexout))
        linesToPrint = []
        print('Example images:')
        for img in imgs:
            iimg = iimg+1
            #print('...appending input ', img)
            inputs.append(img)
            outputs.append(hexout)
            if iimg < nExampleCharsToPrint:
                #print(img)
                imglines = PrintImgFrom1D(img, baseDimx, False)
                PutLineNextToLine(linesToPrint, imglines)
        PrettyPrint(linesToPrint)
        if toTrain:
            print('--- Set to train over class {} with total of {} images! ---'.format(hexcode, iimg+1))
        else:
            print('--- Set to test over class {} with total of {} images! ---'.format(hexcode, iimg+1))
    if toTrain:
        print('--- Set to train over total of {} images! ---'.format(hexcode, len(inputs)))
    else:
        print('--- Set to test over total of {} images! ---'.format(hexcode, len(inputs)))

    #print('Inputs: ', inputs)
    #print('Outputs: ', outputs)
    return inputs, outputs

########################################################################################
########################################################################################
########################################################################################
