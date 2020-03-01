#!/bin/bash

n1=`cat Dotaznik_full_biased.csv | wc -l`

cat Dotaznik_full_biased.csv  | egrep -v -i "kvíta|kocour" | egrep -v "Dno\"|DNO\"|mc2|nasnežilo|\"\.\.\.\"|toust|Málo možnosti odpovědí|4692|trapní|kvitovat|endenční|ozdravem\!|\"1\"|Hotovo\"|Pěkný den\"|Nashledanou\"|Dotazník\"|Nejsem bot|Únor|Vyplněno\"|POTŔEBNY| jimi pokazit.\"|podvádět!\"" > Dotaznik_unbiased.csv
n2=`cat Dotaznik_unbiased.csv | wc -l`

echo "Cut lines from $n1 to $n2"

