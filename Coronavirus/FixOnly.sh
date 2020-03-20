#!/bin/bash

echo "Subsituting..."
cat csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Confirmed.csv       | sed "s|\"||g"  \
											  | sed "s|, | |g"  \
											  > csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Confirmed.csv2 
mv csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Confirmed.csv2 csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Confirmed.csv

echo "Opening to add new CZ data..."
emacs csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Confirmed.csv &

