#!/usr/bin/python





infile = open('data.txt')

nToSkip = 4
iline = -1

sum1 = 0
sums = [0., 0., 0.]

for xline in infile.readlines():
    iline = iline + 1
    if iline < nToSkip:
        continue
    line = xline[:-1]
    print(line)
    items = line.split(' ')
    sum1 = sum1 + int(items[1])

    for iN in range(0, len(sums)):
        sums[iN] = sums[iN] + int(items[1+iN])

print('-------------')
print(sum1)
print(sums)

for iN in range(0, len(sums)):
    print('Sum of column {:} is {:}'.format(len(sums), sums[iN]))


