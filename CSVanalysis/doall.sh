#! /bin/sh


for file in DotaznikSummary DotaznikSummary_En ; do
  pdflatex ${file}.tex
  #cslatex ${file}.tex
  #dvips ${file}.dvi -o ${file}.ps
  #dvipdf ${file}
done
