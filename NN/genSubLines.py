#!/usr/bin/python

Iters = [500]
nImgs = [300, 600, 900]
ks = [ 8, 12, 16, 20, 25, 30]
ms = [ 8, 12, 16, 20, 25, 30]

for iters in Iters:
             for nimgs in nImgs:
                          for k in ks:
                                       for m in ms:
                                                    cmd='./nnRun_Chars.py -b --iters={} --nimgs={} --klayers={} --mlayers={}'.format(iters, nimgs, k, m)
                                                    print(cmd)
