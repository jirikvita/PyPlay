#!/bin/bash

# https://askubuntu.com/questions/610903/how-can-i-create-a-video-file-from-a-set-of-jpg-images

for i in run_20200318_OrigPessimistic_AgeDep run_MoreProbableFasterBetter run_StdOrig run_MoreProbable ; do
    echo "Making mp4 in $i ..."
    cd $i
    rm *.mp4
    ../conv_mp4.sh $i
    cd -
done
