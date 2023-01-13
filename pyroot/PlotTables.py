import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

#Table 1
d1 = {'File \#': [1, 2, 3, 4, 5], 'Number of jets': [797363,446838,781675,449606,388593], 
    'Number of events': [317338,236406,325029,273762,212983]}

df1 = pd.DataFrame(d1)
print()
print("---------------------Table 1-----------------------")
print(df1)
print()

columns2=['Files/Jets', 't', 'w', 'l']
d2 = np.array([[1,11.83, 13.20, 74.97],
               [2,0.86 , 8.88 , 90.27],
               [3,5.06 , 10.45, 84.49],
               [4,15.76, 14.49, 69.75],
               [5,23.77, 11.78, 64.45]])

df2 = pd.DataFrame(d2, columns=columns2)
print("---------------------Table 2-----------------------")
print(df2)
print()

columns3 = ['Files/Number of Jets','1','2','3','4','5','6','7','8','9']
d3 = np.array([[1 , 4.68 , 41.85 , 37.82 , 13.05 , 2.33 , 0.25 , 0.02 , 0 , 0],
               [2 , 26.97 , 45.22 , 22.65 , 4.65 , 0.48 , 0.03 , 0 , 0, 0],
               [3 , 8.34 , 42.61 , 34.88 , 11.97 , 2.00 , 0.20 , 0.01 , 0 , 0],
               [4 , 17.66 , 56.07 , 21.30 , 4.39 , 0.54 , 0.05 , 0 , 0 ,0],
               [5 , 14.51 , 57.81 , 22.45 , 4.54 , 0.62 , 0.06 , 0.01 , 0 ,0]])

df3 = pd.DataFrame(d3, columns=columns3)
print("---------------------Table 3-----------------------")
print(df3)
print()

columns5 = ['File','tt','tl', 'lt','tw','wt','wl','lw','ll']
d5 = np.array([[1, 10.36,38.40,19.25,8.41,3.86,1.57,2.67,15.48],
               [2, 7.16,48.55,11.48,7.58,1.42,0.53,2.83,20.45],
               [3, 6.21,39.97,17.44,7.64,3.43,1.38,2.63,21.30],
               [4, 14.53,42.01,15.62,10.12,5.62,1.24,1.59,9.28],
               [5, 19.91,40.16,17.18,8.24,4.69,0.98,1.26,7.59]])

df5 = pd.DataFrame(d5, columns=columns5)
print("---------------------Table 5-----------------------")
print(df5)
print()

columns6 = ['File','ww','wl','lw','wt','tw','tl','lt','ll']
d6 = np.array([[1, 7.98,28.59,21.23,3.04,6.63,4.96,2.15,25.42],
               [2, 3.56,32.89,10.38,0.09,0.49,1.09,0.20,51.30],
               [3, 4.00,23.84,16.52,1.17,2.61,3.33,1.24,47.29],
               [4, 5.15,24.11,14.42,4.42,7.97,8.38,2.65,32.89],
               [5, 4.12,22.44,14.46,6.53,11.47,9.26,3.45,28.26]])

df6 = pd.DataFrame(d6, columns=columns6)
print("---------------------Table 6-----------------------")
print(df6)
print()

columns7 = ['File','t','w','l']
d7 = np.array([[1, 74.56 ,0,25.44],
               ['' , 0,49.94,50.06],
               [2,73.89,0,26.11],
               ['' ,0,38.64,61.36],
               [3,69.3,0,30.70],
               ['' ,0,35.41,64.59],
               [4,84.44,0,15.56],
               ['' ,0,46.94,53.06],
               [5,86.63,0,13.37],
               ['' ,0,48.65,51.35]])

df7 = pd.DataFrame(d7, columns=columns7)
print("---------------------Table 7-----------------------")
print(df7)
print()


columns8 = ['File', 'Set','Accuracy','Precision','Recall','False positive rate']
d8 = np.array([[1, 'train',75.51,75.84,98.57,92.15],
               ['' , 'test',75.15,75.60,98.39,92.68],
               [2, 'train',76.30,75.81,99.93,91.55],
               ['' , 'test',72.90,73.30,98.95,97.71],
               [3, 'train',70.44,98.21,70.60,33.84],
               ['' , 'test',70.11,70.57,97.73,92.79],
               [4, 'train',84.64,84.64,99.96,98.96],
               ['' , 'test',84.26,84.32,99.89,99.30],
               [5, 'train',84.74,86.77,99.94,98.82],
               ['' , 'test',84.64,86.68,99.93,99.30]])

df8 = pd.DataFrame(d8, columns=columns8)
print("---------------------Table 8-----------------------")
print(df8)
print()

# here was mistake ??? 32.30.97
columns9 = ['File', 'Set','Accuracy','Precision','Recall','False positive rate']
d9 = np.array([[1, 'train',63.75,62.33,69.53,42.03],
               ['', 'test',63.19,61.61,68.91,42.48],
               [2, 'train',64.83,58.21,32.13,14.54],
               ['', 'test',64.72,57.52,32.30,14.96],
               [3, 'train',66.40,57.60,19.62,7.92],
               ['', 'test',66.17,56.28,18.99,8.06],
               [4, 'train',61.73,59.65,57.11,34.18],
               ['', 'test',61.49,59.35,57.08,34.60],
               [5, 'train',62.95,61.42,64.69,38.70],
               ['', 'test',62.44,60.53,63.67,38.71]])

df9 = pd.DataFrame(d9, columns=columns9)
print("---------------------Table 9-----------------------")
print(df9)
print()

columns10 = ['File', 'Accuracy', 'Precision', 'Recall', 'False positive rate']
d10 = np.array([[1 , 75.46 , 75.89 , 98.32 , 91.54],
                [2 , 72.56 , 75.18 , 93.85 , 87.68],
                [3 , 69.79 , 71.01 , 95.33 , 87.85],
                [4 , 83.34 , 85.07 , 97.36 , 92.77],
                [5 , 86.21 , 87.07 , 98.75 , 95.02]])

df10 = pd.DataFrame(d10, columns=columns10)
print("---------------------Table 10-----------------------")
print(df10)
print()

columns11 = ['File', 'Accuracy','Precision','Recall','False positive rate']

d11 = np.array([[1 , 63.56 , 62.14 , 69.16 , 42.03 ],
                [2 , 61.09 , 49.10 , 19.39 , 12.66 ],
                [3 , 61.04 , 45.51 , 50.75 , 33.31 ],
                [4 , 58.94 , 55.29 , 65.48 , 46.84 ],
                [5 , 58.16 , 56.09 , 64.49 , 47.84 ]])
df11 = pd.DataFrame(d11, columns=columns11)
print("---------------------Table 11-----------------------")
print(df11)
print()


#d12
columns12 = ['File X?', 't','w','l']
d12 = np.array([['2 jets per event, t prediction', 53.28 , 8.36 , 38.36],
                ['2 jets per event, W prediction', 7.62 , 47.25 , 45.12],
                ['3 jets per event, t prediction', 34.16 , 6.19 , 59.65],
                ['3 jets per event, W prediction', 7.22 , 28.10 , 64.68],
                ['4 jets per event, t prediction', 23.67 , 4.58 , 71.76],
                ['4 jets per event, W prediction', 6.17 , 19.67 , 74.17]])
df12 = pd.DataFrame(d12, columns=columns12)
print("---------------------Table 12-----------------------")
print(df12)
print()

#d13

columns13 = ['Jets in an event', 'Fraction']
d13 = np.array([['tl', 41.01],
                ['tt', 17.43],
                ['tw', 9.11],
                ['lt', 16.46],
                ['ll', 8.37],
                ['lw', 1.41],
                ['wt', 5.12],
                ['wl', 1.10]])
df13 = pd.DataFrame(d13, columns=columns13)
print("---------------------Table 13-----------------------")
print(df13)
print()

# d14

columns14 = ['Jets in an event', 'Fraction']
d14 = np.array([['wl', 43.71],
                ['ll', 6.45],
                ['ww', 8.29],
                ['lw', 26.29],
                ['tw', 5.47],
                ['wt', 2.44],
                ['tl', 5.28],
                ['lt', 2.05]])
df14 = pd.DataFrame(d14, columns=columns14)
print("---------------------Table 14-----------------------")
print(df14)
print()

#d15

columns15 = ['File','Set','Accuracy','Precision','Recall','False positive rate']
d15 = np.array([['2 jets per event', 'train', 91.4 , 86.1 , 100 , 18.4],
                ['', 'test', 91.1 , 85.8 , 99.9 , 18.8], 
                ['3 jets per event', 'train', 94.8 , 86.9 , 99.7 , 7.7],
                ['', 'test', 94.2 , 86.3 , 98.9 , 8.2],
                ['4 jets per event', 'train', 97.1 , 89.1 , 99.8 , 3.8],
                ['', 'test', 93.8 , 81.8 , 95.2 , 6.7]])
df15 = pd.DataFrame(d15, columns=columns15)
print("---------------------Table 15-----------------------")
print(df15)
print()

#d16

columns16 = ['File','Set','Accuracy','Precision','Recall','False positive rate']
d16 = np.array([['2 jets per event', 'train', 84 , 81.6 , 85.4 , 17.2],
                ['' , 'test', 82.9 , 80.8 , 83.9 , 18], 
                ['3 jets per event', 'train', 87.6 , 79.6 , 75.2 , 7.6],
                ['' , 'test', 86.9 , 78.3 , 73.5 , 7.9],
                ['4 jets per event', 'train', 91.6 , 79.2 , 77.1 , 4.9],
                ['' , 'test', 89.6 , 75.2 , 71.1 , 5.8]])
df16 = pd.DataFrame(d16, columns=columns16)
print("---------------------Table 16-----------------------")
print(df16)
print()


#df1.plot()
#df2.plot()
#df3.plot()
##df4.plot()
#df5.plot()
#df6.plot()
#df7.plot()
#df8.plot()
#df9.plot()
#df10.plot()
#df11.plot()
#df12.plot()
#df13.plot()
#df14.plot()
#df15.plot()
#df16.plot()


df1.plot(x = df1.columns[0])
df2.plot(x = df2.columns[0])
df3.plot(x = df3.columns[0])
##df4.plot(x = #df4.columns[0])
df5.plot(x = df5.columns[0])
df6.plot(x = df6.columns[0])
#df7.plot(x = df7.columns[0])
#df8.plot(x = df8.columns[0])
#df9.plot(x = df9.columns[0])
#df10.plot(x = df10.columns[0])
#df11.plot(x = df11.columns[0])
#df12.plot(x = df12.columns[0])
#df13.plot(x = df13.columns[0])
#df14.plot(x = df14.columns[0])
#df15.plot(x = df15.columns[0])
#df16.plot(x = df16.columns[0])
plt.show()
