import netgraph
import matplotlib.pyplot as plt
import pandas as pd

import numpy as np

import sys
import ast

if __name__ == '__main__':
    # print('Number of arguments:', len(sys.argv), 'arguments.')
    # print('Argument List:', str(sys.argv))
    # print('name is: ', sys.argv[1])
    ax = plt.subplot(111)
    linestyles = ['-', '--', '-.', ':', 'solid', 'dashed', 'dashdot', 'dotted']
    from matplotlib.lines import Line2D

    markers = list(Line2D.markers)

    data = pd.read_csv(ast.literal_eval(sys.argv[1]))
    for i, col_name in enumerate(data.columns):
        x = np.sort(data[col_name])
        y = (np.arange(1, len(x) + 1) / len(x))

        splitted_col_name = col_name.split('+')
        if splitted_col_name[0] == 'ALL':
            col_name = 'OPTIMAL ' + '(' + splitted_col_name[1] + ')'
        if splitted_col_name[0] == 'RAEKE' and splitted_col_name[1] == 'LB':
            col_name = col_name + ' (SMORE)'

        if splitted_col_name[0] == 'KSP' and splitted_col_name[1] == 'LB':
            col_name = col_name + ' (SWAN)'

        # ax.plot(x, y, label=col_name, linestyle=linestyles[i % len(linestyles)], lw=2.5)
        ax.plot(x, y, label=col_name, marker=markers[i % len(markers)], markevery=4)
        plt.xlabel('Throughput(%)')
        plt.ylabel('CDF \n (fraction of TMs')
    ax.grid(color='grey', ls='-.', lw=0.50)

    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    plt.margins(0.02)  # Keeps data off plot edges
    plt.legend()
    plt.savefig('graphs/' + sys.argv[1].split('/')[2] + "_throughput_distribution.pdf")
    plt.show()
