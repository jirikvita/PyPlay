#!/usr/bin/python3

import random
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# generate some random data (approximately over 5 years)
data = [float(random.randint(1271517521, 1429197513)) for _ in range(1000)]
# convert the epoch format to matplotlib date format 
#mpl_data = mdates.epoch2num(data)

data = [ '2020/02/22 10:13:55 AM GMT+1', '2020/02/22 10:15:17 AM GMT+1', '2020/02/22 10:15:44 AM GMT+1', '2020/02/22 10:16:27 AM GMT+1', '2020/02/22 10:16:41 AM GMT+1', '2020/02/22 10:20:42 AM GMT+1', '2020/02/22 10:27:23 AM GMT+1', '2020/02/22 10:30:14 AM GMT+1', '2020/02/22 10:38:47 AM GMT+1', '2020/02/22 10:39:10 AM GMT+1', '2020/02/22 10:39:13 AM GMT+1', '2020/02/22 10:41:51 AM GMT+1', '2020/02/22 10:42:48 AM GMT+1', '2020/02/22 10:43:45 AM GMT+1', '2020/02/22 10:49:02 AM GMT+1', '2020/02/22 11:00:23 AM GMT+1', '2020/02/22 11:07:47 AM GMT+1', '2020/02/22 11:08:48 AM GMT+1', '2020/02/22 11:12:25 AM GMT+1', '2020/02/22 11:34:31 AM GMT+1', '2020/02/22 11:35:52 AM GMT+1', '2020/02/22 11:37:02 AM GMT+1', '2020/02/22 11:43:48 AM GMT+1', '2020/02/22 11:46:33 AM GMT+1', '2020/02/22 11:48:00 AM GMT+1', '2020/02/22 11:50:57 AM GMT+1', '2020/02/22 11:56:46 AM GMT+1', '2020/02/22 11:57:11 AM GMT+1', '2020/02/22 11:59:31 AM GMT+1', '2020/02/22 11:59:48 AM GMT+1', '2020/02/22 12:00:01 PM GMT+1', '2020/02/22 12:11:17 PM GMT+1', '2020/02/22 12:17:04 PM GMT+1', '2020/02/22 12:22:11 PM GMT+1', '2020/02/22 12:26:18 PM GMT+1', '2020/02/22 12:27:02 PM GMT+1', '2020/02/22 12:31:46 PM GMT+1', '2020/02/22 12:32:27 PM GMT+1', '2020/02/22 12:37:17 PM GMT+1', '2020/02/22 12:38:12 PM GMT+1', '2020/02/22 12:51:23 PM GMT+1', '2020/02/22 1:03:35 PM GMT+1', '2020/02/22 1:05:36 PM GMT+1', '2020/02/22 1:08:45 PM GMT+1', '2020/02/22 1:30:56 PM GMT+1', '2020/02/22 1:35:18 PM GMT+1', '2020/02/22 1:52:48 PM GMT+1', '2020/02/22 1:52:54 PM GMT+1', '2020/02/22 1:53:03 PM GMT+1', '2020/02/22 2:03:52 PM GMT+1', '2020/02/22 2:05:28 PM GMT+1', '2020/02/22 2:06:43 PM GMT+1', '2020/02/22 2:06:58 PM GMT+1', '2020/02/22 2:09:27 PM GMT+1', '2020/02/22 2:11:10 PM GMT+1', '2020/02/22 2:15:45 PM GMT+1', '2020/02/22 2:16:08 PM GMT+1', '2020/02/22 2:17:04 PM GMT+1', '2020/02/22 2:18:20 PM GMT+1', '2020/02/22 2:21:49 PM GMT+1', '2020/02/22 2:22:51 PM GMT+1', '2020/02/22 2:25:15 PM GMT+1', '2020/02/22 2:28:44 PM GMT+1', '2020/02/22 2:40:22 PM GMT+1', '2020/02/22 2:47:40 PM GMT+1', '2020/02/22 2:48:55 PM GMT+1'         ]


mpl_data = mdates.datestr2num(data)
data = mpl_data

print(mpl_data)

# plot it
fig, ax = plt.subplots(1,1)
ax.hist(data, bins=12, color='lightblue')
ax.xaxis.set_major_locator(mdates.YearLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%d.%m.%y'))
plt.show()


