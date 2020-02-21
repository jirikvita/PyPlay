#!/bin/bash

for c in `ls c?.C` ; do
  root -b -q -l $c
done
