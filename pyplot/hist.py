#!/usr/bin/python

# code generated by https://chat.openai.com/chat
# how to plot a histogram in matplotlib?

import matplotlib.pyplot as plt

# Generate some data to use for the histogram
data = [2, 2, 1, 2, 2, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5, 5, 5,2, 2, 4, 4, 4, 4,3, 3, ]

# Use the hist() function to create the histogram
plt.hist(data, bins=5)

# Add a title and label the axes
plt.title("Sample Histogram")
plt.xlabel("Data")
plt.ylabel("Frequency")

# Display the plot
plt.show()
