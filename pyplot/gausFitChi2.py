#!/usr/bin/python

# thanks! how do I obtain the chisquare and number of degrees of freedom of the above fit?

# In this updated code, we calculate the residuals as the difference between the normalized histogram data and the fitted Gaussian function evaluated at the bin centers. We then calculate the chi-square value as the sum of the squared residuals divided by the normalized histogram data. Finally, we calculate the degrees of freedom as the number of data points minus the number of fitting parameters. These values are printed to the console after the fit is performed.


#Thanks, but unfortunatelly for the printd chisq I get 'inf', so something is wrong, could you please correct your code?

#I apologize for the error in my previous response. The issue is that the calculation of the chi-square value is incorrect, and it's resulting in a value of "inf".
#To fix this issue, we need to use the squared residuals instead of the normalized histogram data in the chi-square calculation. Here's the updated code:

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

###################################################################

# Define the Gaussian function to fit the histogram
def gauss(x, a, mu, sigma):
    return a * np.exp(-(x - mu)**2 / (2 * sigma**2))

###################################################################

# Generate some random data from a Gaussian distribution
data = np.random.normal(0, 1, 10000)

# Create the histogram
n, bins, patches = plt.hist(data, bins=30, density=True, alpha=0.5)

# Get the bin centers and normalize the histogram
bin_centers = (bins[1:] + bins[:-1]) / 2
#bin_widths = (bins[1:] - bins[:-1])
#n = n / np.sum(n * bin_widths)

print(n)

# Fit the histogram with the Gaussian function
popt, pcov = curve_fit(gauss, bin_centers, n, p0=[1, 0, 1])

# Calculate the chi-square and degrees of freedom
residuals = n - gauss(bin_centers, *popt)
print(residuals)

# JK: correction was needed: keep only nonzero values;)
safe_residuals = []
safe_n = []
for res,binc in zip(residuals, n):
    if binc > 0:
        safe_n.append(binc)
        safe_residuals.append(res)

# convert to np array:
np_safe_residuals = np.array(safe_residuals)
np_safe_n = np.array(safe_n)

# sum of [n - fit]^2 / (sqrt(n))^2
chisq = np.sum(np_safe_residuals**2 / (np_safe_n )) #* bin_widths))
dof = len(np_safe_n) - len(popt)

print(f"Chi-square value: {chisq:.3f}")
print(f"Degrees of freedom: {dof}")

# Plot the histogram and the fitted Gaussian function
plt.plot(bin_centers, gauss(bin_centers, *popt), 'r-', label='fit')
plt.title('Gauss random data and fit')
plt.legend()


plt.show()
