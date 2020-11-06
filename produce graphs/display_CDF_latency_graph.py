import netgraph
import matplotlib.pyplot as plt
import pandas as pd

import numpy as np

import os
import ast
import sys
import ast

directory = '../output/' + str(sys.argv[1]) + '/latency/'
filenames = os.listdir(directory)
print(directory)

ax = plt.subplot(111)

linestyles = ['-', '--', '-.', ':', 'solid', 'dashed', 'dashdot', 'dotted']
curve_num = 0
for filename in filenames:
    ax = plt.subplot(111)
    data = pd.read_csv(directory + '/' + filename)
    data.sort_values(by=[data.columns[0]], inplace=True)
    print(data.columns)
    x = data[data.columns[0]]  # sorted delay
    y = np.cumsum(data[data.columns[1]])
    # y = y / np.linalg.norm(y)
    label = filename.split('.')[0]
    splitted_col_name = label.split('+')
    if splitted_col_name[0] == 'ALL':
        label = 'OPTIMAL ' + '(' + splitted_col_name[1] + ')'
    if splitted_col_name[0] == 'RAEKE' and splitted_col_name[1] == 'LB':
        label = label + ' (SMORE)'

    if splitted_col_name[0] == 'KSP' and splitted_col_name[1] == 'LB':
        label = label + ' (SWAN)'

    ax.plot(x, y, label=label, linestyle=linestyles[curve_num % len(linestyles)], lw=2.5)  #
    curve_num += 1
    plt.xlabel('Delay (ms)')
    plt.ylabel('CDF \n Fraction of traffic delivered')
ax.set_xlim(0, 150)
ax.grid(color='grey', ls='-.', lw=0.50)
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
plt.margins(0.02)  # Keeps data off plot edges
plt.legend()
plt.savefig('graphs/' + sys.argv[1] + "_delay_distribution.pdf")
plt.show()

#   exit(0)
# for i, col_name in enumerate(data.columns):
#     x = np.sort(data[col_name])
#     y = 1 - (np.arange(1, len(x) + 1) / len(x))
#     ax.plot(x, y, label=col_name, linestyle=linestyles[i], lw=2.5)
#     plt.xlabel('Congestion')
#     plt.ylabel('Complementary CDF \n (fraction of edges)')
# ax.grid(color='grey', ls='-.', lw=0.50)
#
# ax.spines['right'].set_visible(False)
# ax.spines['top'].set_visible(False)
# plt.margins(0.02)  # Keeps data off plot edges
# plt.legend()
# plt.show()
