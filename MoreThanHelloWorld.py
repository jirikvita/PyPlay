#!/usr/bin/python3
# ...tohle nahore rika, v jakem jazyce piseme a jaky jazyk ma tento skript interpertovat;-)

import os, sys

# a toto je nejaky dalsi dulezity komentar;-)
# (c) jiri kvita, 17.9.2019

print("S pythonem se nejlepe naucime i zaklady programovani:)")

#for cyklus, aneb k cemu nam jest;)

n = 10
for i in range(0,n):
    print(i*i)
    if i == 5:
       print('Found {:}, not {:}!'.format(i, i-1))
       pass # neni nutne
    pass # zase jen prazdny prikaz, co nic nedela, a ze se jde dale, neni nutne;-)

# nejake values;)
vals = [4., 5.4, 2.1, 9.2, 0.8]
print(vals)

print('We have {:} members!'.format(len(vals)))
print('First member: {:}'.format(vals[0]))
print('Second member: {:}'.format(vals[1]))
print('Last member: {:}'.format(vals[len(vals)-1]))
print('Last member: {:}'.format(vals[-1])) # zaporne indexy cisluji odzadu;)


# projdeme si a vypiseme polozky vals:
# a spocitame si, kolik prvku je mensich nez 3.
cut = 3.
ncut = 0
for i in range(0, len(vals)):
    print('Item #{:}, value: {:}'.format(i, vals[i]))
    if vals[i] < cut:
        ncut = ncut+1
print('Nasli jsme {:} prvku mensich nez {:}!'.format(ncut, cut))
print('Spravne sklonovani ted resit nebudeme:) \nAle muzete si to zkusit spravne vypsat za domaci ukol;-)\nAtaky vidime, jak psat na novy radek\tnebo\tjak pouzit tabelator!')

# A ted uloha: jak najdeme nejvetsi prvek?
# v teto promenne si budeme pamatovat dosavadni nejvyssi hodnotu
maxval = -999 # nastavime na neco hodne maleho
# a v teto promenne si budeme pamatovat, ktera to byla polozka v seznamu;-)
imax = -1
print("Now, let's check the maximum...")

# a ted si projdeme seznam;-)
# lze take cyklovat takto:-)
for val in vals:
    print('...working on {:}'.format(val,))
    if val > maxval:
       # dokoncete;)
       # sem tedy prijde nejaky kod;-)
       print('Ha, nasli jsme prvek {:}, ktery je vetsi nez dosavadni maximum {:}!'.format(val, maxval))
       pass
print('Maxval jest {:} a jde o {:}-ty prvek v seznamu!'.format(maxval, imax))

# Domaci uloha: jak najdeme druhy nejvetsi prvek?;)

# time for a little evaluation:
odpo = ''
#print()
while odpo != 'yes' and odpo != 'no':
    odpo = input('Did you have fun? yes/no:')
    #print(odpo)
    
print('DONE! And: have fun! ;-)')




