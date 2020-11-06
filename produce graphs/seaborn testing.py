import matplotlib.pyplot as plt
from pandas.plotting import register_matplotlib_converters

register_matplotlib_converters()

import numpy as np
import pandas as pd
import seaborn as sns
import ast

sns.set(style="whitegrid")
path = '../output/AttMpls.dot/throughput.csv'
data = pd.read_csv(path)
print(type(data))
print(data.columns)
for column in data.columns:
    x = np.sort(data[column])
    y = np.cumsum(data[column])
    _ = plt.plot(x, y, marker='x', linestyle='none')

plt.show()
# for i, col_name in enumerate(data.columns):
#     x = np.sort(data[col_name])
#     y = (np.arange(1, len(x) + 1) / len(x))

# rs = np.random.RandomState(365)
# values = rs.randn(365, 4).cumsum(axis=0)
# dates = pd.date_range("1 1 2016", periods=365, freq="D")
# data = pd.DataFrame(values, dates, columns=["A", "B", "C", "D"])
# data = data.rolling(7).mean()

# sns.lineplot(data=data, palette="tab10", linewidth=2.5)

plt.show()

# import matplotlib.pyplot as plt
# import pandas as pd
#
# import numpy as np
#
# import sys
# import ast
#
# if __name__ == '__main__':
#     # print('Number of arguments:', len(sys.argv), 'arguments.')
#     # print('Argument List:', str(sys.argv))
#     # print('name is: ', sys.argv[1])
#     ax = plt.subplot(111)
#     linestyles = ['-', '--', '-.', ':', 'solid', 'dashed', 'dashdot', 'dotted']
#     data = pd.read_csv(ast.literal_eval(sys.argv[1]))
#     for i, col_name in enumerate(data.columns):
#         x = np.sort(data[col_name])
#         y = (np.arange(1, len(x) + 1) / len(x))
#
#         splitted_col_name = col_name.split('+')
#         if splitted_col_name[0] == 'ALL':
#             col_name = 'OPTIMAL ' + '(' + splitted_col_name[1] + ')'
#         if splitted_col_name[0] == 'RAEKE' and splitted_col_name[1] == 'LB':
#             col_name = col_name + ' (SMORE)'
#         ax.plot(x, y, label=col_name, linestyle=linestyles[i % len(linestyles)], lw=2.5)
#         plt.xlabel('Throughput(%)')
#         plt.ylabel('CDF \n (fraction of TMs')
#     ax.grid(color='grey', ls='-.', lw=0.50)
#
#     ax.spines['right'].set_visible(False)
#     ax.spines['top'].set_visible(False)
#     plt.margins(0.02)  # Keeps data off plot edges
#     plt.legend()
#     plt.savefig('graphs/' + sys.argv[1].split('/')[2] + "_throughput_distribution.pdf")
#     plt.show()
