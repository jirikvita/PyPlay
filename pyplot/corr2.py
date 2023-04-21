#!/usr/bin/python

# https://chat.openai.com/chat
#



import numpy as np
import matplotlib.pyplot as plt
#!/usr/bin/python

# https://chat.openai.com/chat
# write python code to plot a scatter plot between two random variables and indicate in the plot also the correlation between them

# Generate two random variables

# original:
#x = np.random.normal(size=100)
#y = np.random.normal(size=100)

# JK modified:
x = np.random.normal(0, 10, 100)
d = np.random.normal(0, 5, 100)
y = x + d

# Calculate Pearson correlation coefficient
corr_coef = np.corrcoef(x, y)[0, 1]

# Create scatter plot
fig, ax = plt.subplots()
ax.scatter(x, y)
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_title(f'Scatter plot between X and Y\nCorrelation: {corr_coef:.2f}', fontsize=14)

# Add correlation coefficient to plot
textstr = f'Correlation coefficient: {corr_coef:.2f}'
props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
ax.text(0.05, 0.95, textstr, transform=ax.transAxes, fontsize=12,
        verticalalignment='top', bbox=props)

plt.show()

# In this code, we first generate two random variables, x and y, using the numpy.random.normal() function. Then, we calculate the Pearson correlation coefficient between them using numpy.corrcoef().
# Next, we create a scatter plot using matplotlib.pyplot.subplots(), scatter(), `

