#!/bin/bash

# OLD: csvfile=time_series_19-covid-Confirmed.cs

csvdir=csse_covid_19_data/csse_covid_19_time_series


for csvfile in time_series_covid19_confirmed_global.csv time_series_covid19_deaths_global.csv time_series_covid19_recovered_global.csv ; do

  echo "Subsituting ${csvfile} ..."
  cat ${csvdir}/${csvfile} | sed "s|\"||g"  \
                           | sed "s|, | |g"  \
      			   > ${csvdir}/${csvfile}2 

  mv ${csvdir}/${csvfile}2 ${csvdir}/${csvfile}

  #echo "Opening to add new CZ data..."
  #emacs ${csvdir}/${csvfile} &
done
