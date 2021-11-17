#!/usr/bin/python3

from PIL import Image

import numpy as np

from readTools import *

# reading NIST hand written character data
# https://www.nist.gov/itl/products-and-services/emnist-dataset 
# https://www.nist.gov/srd/nist-special-database-19



# 128x128 pixels
image = Image.open('data/by_class/6e/train_6e/train_6e_04507.png')
image_array = np.array(image)
#print(image_array)
iline = -1

nLines = len(image_array)
print('Lines: {}'.format(nLines))


for line in image_array:
    iline = iline + 1
    #print(line)
    icol = -1
    for pix in line:
        icol = icol + 1
        r,g,b = pix[0], pix[1], pix[2]
        #print('r={} g={} b={}'.format(r,g,b))
        if r == 0 and g == 0 and b == 0:
            print('...found black dot {} column {}'.format(iline, icol))

rebinx = 2
rebiny = 2
baseDimx = 128 / rebinx
baseDimy = 128 / rebiny
fullDIM = baseDimx*baseDimy # hack
# zoom crop cutoff factor for original, non-reinned data:
cutoffx,cutoffy = 40, 40
DIM = int( (baseDimx - 2*cutoffx/rebinx)*(baseDimy - 2*cutoffy/rebiny) ) # hack

#print(image_array)
PrintImg2DInv(image_array)
image_array_rebinned = Rebin2DRGBArray(image_array, 2,2)
PrintImg2DInv(image_array_rebinned)
