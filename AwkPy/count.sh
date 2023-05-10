#!/bin/bash


Nhead=4
N=`cat data.txt | wc -l`
Nlines=`expr $N - $Nhead`

cat data.txt | tail -n $Nlines | awk 'BEGIN{sum1 = 0};{sum1 = sum1 + $2;};END{print(sum1)};'


