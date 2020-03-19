#!/bin/bash

echo "Cleaning..."
rm -rf csse_covid_19_data/
echo "Pulling..."
git pull

./FixOnly.sh

