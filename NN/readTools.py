#!/usr/bin/python3

from PIL import Image
import os
import sys

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
    image_path = os.path.join(path, hexcode, f'train_{hexcode}', f'train_{hexcode}_{imgid}.png')
    try:
        image = Image.open(image_path)
    except Exception:
        return None
    image_array_orig = np.asarray(image)
    image_array = image_array_orig
    
    if rebinx > 0 and rebiny > 0:
        image_array = Rebin2DRGBArray(image_array_orig , rebinx, rebiny)
    
    nLines = image_array.shape[0]
    nCols = image_array.shape[1]

    # Fast vectorized crop + threshold + flatten to 1D list.
    cropped = image_array[cutoffy:nLines-cutoffy, cutoffx:nCols-cutoffx]
    if cropped.size == 0:
        return []

    if cropped.ndim == 2:
        mask = cropped <= thr
    else:
        mask = np.logical_and.reduce((cropped[:, :, 0] <= thr, cropped[:, :, 1] <= thr, cropped[:, :, 2] <= thr))

    return mask.astype(np.float64).ravel().tolist()

########################################################################################
def Rebin2DRGBArray(data, rebinx = 2, rebiny = 2, doAver = True):
    arr = np.asarray(data)
    if rebinx <= 0 or rebiny <= 0:
        return arr

    h = (arr.shape[0] // rebinx) * rebinx
    w = (arr.shape[1] // rebiny) * rebiny
    if h == 0 or w == 0:
        return arr

    arr = arr[:h, :w]
    if arr.ndim == 2:
        reshaped = arr.reshape(h // rebinx, rebinx, w // rebiny, rebiny)
        if doAver:
            return reshaped.mean(axis=(1, 3))
        return reshaped.sum(axis=(1, 3))

    reshaped = arr.reshape(h // rebinx, rebinx, w // rebiny, rebiny, arr.shape[2])
    if doAver:
        return reshaped.mean(axis=(1, 3))
    return reshaped.sum(axis=(1, 3))


########################################################################################
def readImages(path, hexcode, i1, i2, cutoffx, cutoffy, rebinx = -1, rebiny = -1, thr = 0.5):
    imgs = []
    n_missing = 0
    n_bad = 0
    total = max(0, i2 - i1)
    bar_width = 30
    update_every = max(1, total // 50)
    for i in range(i1, i2):
        imgid = MakeDigitStr(i, 4)
        image_path = os.path.join(path, hexcode, f'train_{hexcode}', f'train_{hexcode}_{imgid}.png')
        if not os.path.isfile(image_path):
            n_missing += 1
            continue

        #print('reading img {}'.format(imgid))
        img = readPng(path, hexcode, imgid, cutoffx, cutoffy, rebinx, rebiny, thr=thr)
        if img is None:
            n_bad += 1
            continue
        imgs.append ( img )

        # In-place terminal progress bar for image loading per class.
        done = (i - i1 + 1)
        if total > 0 and (done == total or (done % update_every == 0)):
            frac = done / float(total)
            filled = int(bar_width * frac)
            bar = '#' * filled + '-' * (bar_width - filled)
            sys.stdout.write(f'\rReading class {hexcode}: [{bar}] {done}/{total}')
            sys.stdout.flush()

    if total > 0:
        sys.stdout.write('\n')
        sys.stdout.flush()

    if n_missing > 0 or n_bad > 0:
        print('WARNING: class {} skipped {} missing and {} unreadable images in requested index range [{}, {}).'.format(hexcode, n_missing, n_bad, i1, i2))

    return imgs


########################################################################################
def ReadData(
    hexcodes,
    i1,
    i2,
    cutoffx,
    cutoffy,
    rebinx,
    rebiny,
    baseDimx,
    toTrain = True,
    nExampleCharsToPrint = 5,
    dataPath = 'data/by_class',
    thr = 0.5,
):
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
        imgs = readImages(dataPath, hexcode, i1, i2, cutoffx, cutoffy, rebinx, rebiny, thr=thr)
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
        print('--- Set to train over total of {} images! ---'.format(len(inputs)))
    else:
        print('--- Set to test over total of {} images! ---'.format(len(inputs)))

    #print('Inputs: ', inputs)
    #print('Outputs: ', outputs)
    return inputs, outputs

########################################################################################
########################################################################################
########################################################################################
