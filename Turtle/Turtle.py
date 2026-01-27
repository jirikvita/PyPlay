#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 21 09:18:26 2025

@author: qitek
"""

from turtle import *

#screen = turtle.Screen()



def square(l):
    for i in range(0,4):
        forward(l)
        right(90)

delta = 10
N = int(360 / delta)


r1, g1, b1 = 0, 0.5, 0.5
dr = 0.
dg = (1. - g1)/N
db = (1. - b1)/N

#clear()
right(5)
Ls = [25*i for i in range(1,11)]
hideturtle()


shape("turtle")

for L in Ls:
    for i in range(0,N):
        #pencolor(r1 + dr*i, g1 + dg*i, b1 + db*i)
        pencolor(0, 0.4, 0.8)
        #pencolor(0, 0.8, 0.4)
        square(L)
        right(delta)

# showturtle()    