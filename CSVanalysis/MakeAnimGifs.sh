#!/bin/bash

anim=anim
mkdir -p $anim
for i in `cd png_All ; ls` ; do
  j=`basename $i .png`.gif
  echo "Making $j ..."
  convert png_All_0*/$i ${anim}/$j
done
