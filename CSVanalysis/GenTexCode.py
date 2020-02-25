#!/usr/bin/python3

import os, sys

dtag = 'All'

outfilename = 'results_{}.tex'.format(dtag)
outfile = open(outfilename, 'w')

pdfpairs = []

pdfpair = []
for pdf in os.popen('ls pdf_{}/*.pdf | grep -v Comme'.format(dtag)).readlines():
    # outfile.write(r'\clearpage' + '\n')
    print(pdf)
    pdfname = pdf[:-1]
    pdfpairs.append( pdfname )

    
    #if len(pdfpair) < 2:
    #    pdfpair.append(pdfname)
    #if len(pdfpair) == 2:
    #    pdfpairs.append( [pdfpair[0], pdfpair[1]])
    #    pdfpair = []

for pdfname in pdfpairs:    
    #tag = pdfname[0]
    #tag = tag.replace('figs/', '').replace('_','')
    outfile.write(r'% _____________________________________________________________________ %' + '\n')
    outfile.write(r'{  \centerline{\includegraphics[width=0.99\textwidth]{' + pdfname + '}  } }\n')
    #name0 = pdfname[0]
    #name1 = pdfname[1]
    #outfile.write(r'{  \includegraphics[width=0.45\textwidth]{' + name0 + '}  }\n')
    #outfile.write(r'{  \includegraphics[width=0.45\textwidth]{' + name1 + '}  }\n')
    outfile.write('\n\n')




outfile.close()
    
