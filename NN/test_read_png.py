#!/usr/bin/python3

from PIL import Image

import numpy as np


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
    for x in line:
        icol = icol + 1
        r,g,b = x[0], x[1], x[2]
        #print('r={} g={} b={}'.format(r,g,b))
        if r == 0 and g == 0 and b == 0:
            print('...found black dot {} column {}'.format(iline, icol))

