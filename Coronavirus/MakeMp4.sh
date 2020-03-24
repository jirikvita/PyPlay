#!/bin/bash

# https://askubuntu.com/questions/610903/how-can-i-create-a-video-file-from-a-set-of-jpg-images


if [ $# -lt 2 ] ; then
  echo "Usage: $0 dir1 [dir2] [dir3..]"
fi



for i in $* ; do
    echo "*** Making mp4 in $i ***"
    if [ -d $i ] ; then
      cd $i
      rm *.mp4
      ../conv_mp4.sh $i
      cd -
    fi
done

echo "New files:"

for i in $* ; do
    if [ -d $i ] ; then
	ls ${i}/*.mp4
    fi
done
