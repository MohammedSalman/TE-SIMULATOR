import matplotlib.pyplot as plt
import networkx as nx
import ast
import numpy as np
from collections import Counter


def read_graphml_topology_from_file(TOPOLOGY_PATH):
    # g = nx.networkx.drawing.nx_pydot.read_dot(TOPOLOGY_PATH)
    g = nx.read_graphml(TOPOLOGY_PATH)  # node_type=int)
    g = nx.convert_node_labels_to_integers(g, first_label=0, ordering='default', label_attribute=None)
    for source, target in g.edges():
        g[source][target]['weight'] = 1.0

    # setting capacities
    for source, target in g.edges():
        strr = g[source][target]['LinkSpeedRaw']
        # temp = re.findall(r'\d+', strr)
        # res = list(map(int, temp))
        g[source][target]['capacity'] = float(strr) / 1000000000.0

    # removing unneeded properties in the graph
    # 'LinkType': 'Fibre', 'LinkSpeed': '10', 'LinkLabel': 'Lit
    # Fibre (10 Gbps)', 'LinkSpeedRaw': 10000000000.0, 'LinkNote': 'Lit  ( )'
    unneeded_att_list = list(list(g.edges(data=True))[0][2].keys())  # [0][1][2].keys()
    unneeded_att_list.remove('weight')
    unneeded_att_list.remove('capacity')
    # print("this is the unnedded list", unneeded_att_list)
    # print(g.edges(data=True))
    for n1, n2, d in g.edges(data=True):
        for att in unneeded_att_list:
            d.pop(att, None)

    g = nx.Graph(g)
    g = nx.to_directed(g)
    return g


if __name__ == '__main__':
    # path = './streaming/data/topologies/graphml/Geant2009.graphml'
    path = '/\\streaming\\data\\topologies\\graphml\\Geant2009.graphml'
    # path = '/data/topologies/graphml/Geant2009.graphml'
    # topo = read_graphml_topology_from_file(ast.literal_eval(path))
    topo = read_graphml_topology_from_file(path)
    print(type(topo))
    capacities = []
    for edge in topo.edges(data=True):
        capacities.append(edge[2]['capacity'])

    print(Counter(capacities))
    # labels, values = zip(*Counter(['A', 'B', 'A', 'C', 'A', 'A']).items())
    labels, values = zip(*Counter(capacities).items())
    indexes = np.arange(len(labels))
    width = 1
    plt.figure(figsize=(10, 5))
    plt.bar(indexes, values, width, color='#607c8e')
    plt.xticks(indexes, labels)

    plt.xlabel('Capacity (Gb)')
    plt.ylabel('# links')
    ax = plt.subplot()
    ax.grid(color='grey', ls='-.', lw=0.50)

    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.set_yscale('log', basey=2)
    plt.margins(0.02)  # Keeps data off plot edges
    # plt.legend()
    plt.grid(axis='y', alpha=0.75)

    plt.savefig('graphs/' + "_capacities_distribution.pdf")
    plt.show()

    # ax.set_title('Amount Frequency')
    # ax.set_xlabel('Amount ($)')
    # ax.set_ylabel('Frequency')
    # ax.set_xticklabels(capacities)
    #
    # rects = ax.patches
    #
    # # Make some labels.
    # labels = ["label%d" % i for i in range(len(rects))]
    #
    # for rect, label in zip(rects, labels):
    #     height = rect.get_height()
    #     ax.text(rect.get_x() + rect.get_width() / 2, height + 5, label,
    #             ha='center', va='bottom')
    #
    #
    #
    # # commutes = pd.Series(capacities)
    # # print(commutes)
    # # commutes = pd.Series.to_string(commutes)
    # # commutes.plot.hist(grid=True, rwidth=0.9,
    # #                    color='#607c8e')
    # # plt.title('Commute Times for 1,000 Commuters')
    # # plt.xlabel('Capacity (Gbps)')
    # # plt.ylabel('# links')
    # # ax = plt.subplot(111)
    # # ax.grid(color='grey', ls='-.', lw=0.50)
    # #
    # # ax.spines['right'].set_visible(False)
    # # ax.spines['top'].set_visible(False)
    # # plt.margins(0.02)  # Keeps data off plot edges
    # # plt.legend()
    # #
    # #
    # # plt.grid(axis='y', alpha=0.75)
    # plt.show()
