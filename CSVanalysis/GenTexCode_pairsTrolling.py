#!/usr/bin/python3

import os, sys

dirname1='ResultsNonTrolled/'
dirname2='ResultsFullTrolled/'
ftag = 'Trolling'
dtag = 'All'

outfilename = 'results_{}.tex'.format(ftag)
outfile = open(outfilename, 'w')

pdfpairs = []


for pdf in os.popen('ls {}pdf_{}/*.pdf | grep -v 29_Comment'.format(dirname1,dtag)).readlines():
    # outfile.write(r'\clearpage' + '\n')
    print(pdf)
    cmntpdfname = pdf[:-1]
    nocmntpdfname = cmntpdfname
    nocmntpdfname = nocmntpdfname.replace('Comments', 'noComments')
    pdfpairs.append([cmntpdfname, nocmntpdfname])

for pdfname in pdfpairs:    
    print(pdfname)
    outfile.write(r'\begin{tabular}{cc}')
    outfile.write(r'% _____________________________________________________________________ %' + '\n')
    name0 = pdfname[0]
    name1 = pdfname[1].replace(dirname1, dirname2)
    outfile.write(r'{  \includegraphics[width=0.49\textwidth]{' + name0 + '} } & \n')
    outfile.write(r'{  \includegraphics[width=0.49\textwidth]{' + name1 + '}' + r'} \\' + '\n')
    outfile.write(r' non-Trolled & Trolled \\' + '\n')
    outfile.write(r'\end{tabular}')
    outfile.write('\n\n')


outfile.close()
    
