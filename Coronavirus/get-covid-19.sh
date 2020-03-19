#!/bin/bash

git clone https://github.com/CSSEGISandData/COVID-19 COVID-19
cd COVID-19
ln -s ../UpdateIfSure.sh ./
ln -s ../FixOnly.sh ./
