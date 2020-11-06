import re
import networkx as nx
import matplotlib.pyplot as plt


# import pygraphviz


def visualizeGraph(g, layout, node_size=150, iterations=100, show_edge_labels=False):
    # g = self.topo
    if layout == 'circular':
        pos = nx.circular_layout(g)
    elif layout == 'shell':
        pos = nx.shell_layout(g)
    elif layout == 'spring':
        pos = nx.spring_layout(g, iterations=iterations)
    elif layout == 'fruchterman':
        pos = nx.fruchterman_reingold_layout(g, iterations=iterations)
    elif layout == 'kamada':
        pos = nx.kamada_kawai_layout(g)
    elif layout == 'spectral':
        pos = nx.spectral_layout(g)
    elif layout == 'rescale':
        pass
        # pos = nx.rescale_layout(g)  # it needs a shape
    elif layout == 'included_in_graph':
        pos = nx.get_node_attributes(g, 'pos')
    elif layout == 'grid':
        pos = dict(zip(g, g))  # nice idea of drawing a grid
    else:
        pos = nx.random_layout(g)

    # nx.draw_networkx_nodes(g, pos, cmap=plt.get_cmap('jet'), node_size=node_size)
    # nx.draw_networkx_labels(g, pos)
    # nx.draw_networkx_edges(g, pos, arrows=True)
    # nx.draw_networkx_edges(g, pos, arrows=False)

    plt.figure(figsize=(8, 8))
    # plt.subplot(111)
    nx.draw_networkx_edges(g, pos, alpha=0.5, arrows=False, width=3)
    nx.draw_networkx_nodes(g, pos,
                           node_size=700,
                           cmap=plt.cm.Reds_r)

    # plt.xlim(-0.05, 1.05)
    # plt.ylim(-0.05, 1.05)
    plt.axis('off')
    nx.draw_networkx_labels(g, pos)
    if show_edge_labels == True:
        nx.draw_networkx_edge_labels(g, pos, font_size=7)
    '''draw_networkx_edge_labels(g, pos,
                              edge_labels=None,
                              label_pos=0.5,
                              font_size=10,
                              font_color='k',
                              font_family='sans-serif',
                              font_weight='normal',
                              alpha=1.0,
                              bbox=None,
                              ax=None,
                              rotate=True,
                              **kwds):'''

    # filename = time.strftime("%Y%m%d-%H%M%S") + '_NetGraph' + ImageFileExtention
    # plt.savefig('svg/' + filename)

    plt.show()


# g = nx.drawing.nx_agraph.read_dot('/streaming/topologies/abilene.dot')
g = nx.networkx.drawing.nx_pydot.read_dot(
    '/data/topologies/Abilene.dot')
print(g.edges(data=True))

nodes_to_delete = []
for tuple in g.edges(data=True):
    if 'h' in tuple[0]:
        nodes_to_delete.append(tuple[0])
    if 'h' in tuple[1]:
        nodes_to_delete.append(tuple[1])
for node in set(nodes_to_delete):
    g.remove_node(node)

# visualizeGraph(g, 'spring', show_edge_labels=False)
g = nx.convert_node_labels_to_integers(g, first_label=0, ordering='default', label_attribute=None)
# adding 'weight' attribute
for source, target in g.edges():
    g[source][target][0]['weight'] = int(g[source][target][0]['cost'])
#removing unneeded properties in the graph
unneeded_att_list = ['dst_port', 'src_port', 'cost']
for n1, n2, d in g.edges(data=True):
    for att in unneeded_att_list:
        d.pop(att, None)
# cleaning capacities
for source, target in g.edges():
    strr = g[source][target][0]['capacity']
    temp = re.findall(r'\d+', strr)
    res = list(map(int, temp))
    g[source][target][0]['capacity'] = res[0]
visualizeGraph(g, 'spring', show_edge_labels=False)
print(g.edges(data=True))
