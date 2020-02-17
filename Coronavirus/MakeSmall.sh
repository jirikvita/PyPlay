#!/bin/bash


mkdir -p small

for i in `ls *.png` ; do

    echo $i
    j=`basename $i .png`
    convert -scale 400 $i small/${j}.gif
    
done
