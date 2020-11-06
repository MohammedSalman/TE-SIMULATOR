import matplotlib.pyplot as plt
import csv
from collections import defaultdict
import numpy as np
from config import RECORDED_INFORMATION
import sys

ax = []
linestyles = ['-', '--', '-.', ':', 'solid', 'dashed', 'dashdot', 'dotted']
for i, metric in enumerate(RECORDED_INFORMATION):
    filename = metric + '.csv'

    dict_of_lists = defaultdict(list)
    for record in csv.DictReader(open(sys.argv[1] + filename)):
        for key, val in record.items():  # or iteritems in Python 2
            dict_of_lists[key].append(val)

    arbitrary_algo_name = list(dict_of_lists.keys())[0]
    num_data_points = len(dict_of_lists[arbitrary_algo_name])
    x = np.arange(0.0, num_data_points, 1.0)
    ax.append(plt.subplot(111))
    for ii, algo in enumerate(dict_of_lists.keys()):
        # print(dict_of_lists[algo])
        dict_of_lists[algo] = [float(item) for item in dict_of_lists[algo]]

        col_name = algo
        splitted_col_name = col_name.split('+')
        if splitted_col_name[0] == 'ALL':
            col_name = 'OPTIMAL ' + '(' + splitted_col_name[1] + ')'
        if splitted_col_name[0] == 'RAEKE' and splitted_col_name[1] == 'LB':
            col_name = col_name + ' (SMORE)'
        if splitted_col_name[0] == 'KSP' and splitted_col_name[1] == 'LB':
            col_name = col_name + ' (SWAN)'

        ax[i].plot(x, dict_of_lists[algo], label=col_name, linewidth=1.25,
                   linestyle=linestyles[ii % len(linestyles)])  # linewidth=1.5

    # ax = plt.subplot(111)
    # ax.plot(x, y)
    #
    # # Hide the right and top spines
    ax[i].spines['right'].set_visible(False)
    ax[i].spines['top'].set_visible(False)
    ax[i].grid(color='grey', ls='-.', lw=0.50)
    plt.xlabel('Time')
    if metric is 'throughput':
        plt.ylabel('Throughput(%)')
    else:
        plt.ylabel('Max Congestion')
    plt.title('Performance')
    plt.legend()
    plt.savefig('graphs/' + sys.argv[1].split('/')[2] + "_" + metric + "_performance.pdf")
    plt.show()
