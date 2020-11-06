from itertools import islice, product
import math
import random
import networkx as nx
import fnss as fnss
import matplotlib.pyplot as plt
from dataclasses import dataclass, field
import copy


def shortest_path(topo, source, target):
    return list(islice(nx.shortest_simple_paths(topo, source, target, weight='weight'), 1))


def create_topology():
    def set_capacities(topo):
        fnss.set_capacities_edge_betweenness(topo, [1073741824], 'Gbps')

    def set_weights(topo):
        fnss.set_weights_constant(topo, 1)
    number_of_nodes = 25
    number_of_links = 45
    g = nx.dense_gnm_random_graph(number_of_nodes, number_of_links)

    # g = nx.Graph()
    # g.add_edge(0, 1)
    # g.add_edge(1, 2)
    # g.add_edge(2, 3)
    # g.add_edge(3, 0)

    # g = nx.Graph()
    # g.add_edge(0, 1)
    # g.add_edge(0, 2)
    # g.add_edge(0, 1)
    # g.add_edge(2, 9)
    # g.add_edge(1, 10)
    # g.add_edge(4, 3)
    # g.add_edge(3, 6)
    # g.add_edge(4, 6)
    # g.add_edge(9, 10)
    # g.add_edge(4, 5)
    # g.add_edge(9, 8)
    # g.add_edge(8, 7)
    # g.add_edge(8, 5)
    # g.add_edge(7, 10)
    # g.add_edge(7, 6)

    set_capacities(g)
    set_weights(g)
    if not nx.is_connected(g):
        print("GRAPH IS NOT CONNECTED!")
        exit(0)

    return g.to_directed()


def all_pairs_shortest_paths(topo):
    #  first convert topo to a dict for efficiency
    temp_dict = nx.to_dict_of_dicts(topo)
    alist = []

    all_pairs = list(product(topo.nodes(), topo.nodes))
    for pair in all_pairs:
        v1 = pair[0]
        v2 = pair[1]
        p_temp = shortest_path(topo, v1, v2)[0]
        p = [(p_temp[i], p_temp[i + 1]) for i in range(len(p_temp) - 1)]
        c = sum([temp_dict[p_temp[i]][p_temp[i + 1]]['weight'] for i in range(len(p_temp) - 1)])

        # if len(p) > 1:
        # print("v1 ", v1, "v2 ", v2, "path is: ", p, " c is ", c)
        alist.append((c, v1, v2, p))

    return alist


class Node:
    def __init__(self, v, v_set, list_of_trees):
        self.v = v
        self.v_set = v_set
        self.list_of_trees = list_of_trees

        assert (isinstance(v, int))
        assert (isinstance(v_set, list))
        assert (isinstance(list_of_trees, list))


class Leaf:
    def __init__(self, v, v_set):
        self.v = v
        self.v_set = v_set

        assert (isinstance(v, int))
        assert (isinstance(v_set, list))


class Single:
    def __init__(self, v_set):
        self.v_set = v_set

        assert (isinstance(v_set, list))


def print_tree(tree):
    if isinstance(tree, Node):
        print("Node ", tree.v, " with set: ", tree.v_set, "that has ", len(tree.list_of_trees), " trees")
        for tr in tree.list_of_trees:
            print_tree(tr)
    if isinstance(tree, Leaf):
        print("Leaf ", tree.v, " with set: ", tree.v_set)

    if isinstance(tree, Single):
        print("Single ", " with set: ", tree.v_set)


def make_frt_tree(topo):
    def dist(v1, v2):
        c, _ = vlist_table[(v1, v2)]
        return c

    def find_first_within(radius, v, permutation):
        def search(l, acc):
            if not l:
                raise Exception("find_first_within")
            else:
                (h, set_) = l[0]
                t = l[1:]
                distance = dist(h, v)
                if distance <= radius:
                    new_hd = (h, [v] + set_)  # set_.insert(0, v)
                    temp = t[::-1] + ([new_hd] + acc)
                    return temp
                else:
                    return search(t, [(h, set_)] + acc)

        result = search(permutation, [])
        assert (isinstance(result, list))
        return result[::-1]  # return the result inverted.

    vertices = list(topo.nodes)
    permuted_vs = random.sample(vertices, len(vertices))

    rand_float = random.random()
    beta = math.exp(rand_float * math.log(2))
    paths_list = all_pairs_shortest_paths(topo)  # in the format list of (c, v1, v2, p).
    vlist_table = {(v1, v2): (c, p) for (c, v1, v2, p) in paths_list}
    max_diameter = max([c[0] for c in paths_list])

    def level_decomp(i, cluster):
        if isinstance(cluster, Node):
            raise Exception("shouldn't get here")
        if isinstance(cluster, Leaf):
            center = cluster.v
            cluster_vs = cluster.v_set
            permuted_sets = [(v, []) for v in permuted_vs]
            beta_i = (2 ** (i - 1)) * beta

            # calculating partition
            temp_p = copy.deepcopy(permuted_sets)
            for v in cluster_vs:
                result = find_first_within(beta_i, v, temp_p)
                temp_p = copy.deepcopy(result)
            partition = copy.deepcopy(temp_p)
            # print(partition)
            filtered = list(filter(lambda x: len(x[1]) > 0, partition))
            # print(filtered)
            children = list(map(lambda x: Single(x[1]) if len(x[1]) == 1 else Leaf(x[0], x[1]), filtered))
            mapped_children = list(map(lambda c: level_decomp(i - 1, c), children))
            return Node(center, cluster_vs, mapped_children)

        if isinstance(cluster, Single):
            return Single(cluster.v_set)

    if not permuted_vs:
        raise Exception("no vertices in topology")
    head = permuted_vs[0]
    initial_set = vertices[::-1]  # make sure it is inverted.
    initial_tree = Leaf(head, initial_set)
    initial_i = math.frexp(max_diameter)[1] - 1
    decomp = level_decomp(initial_i, initial_tree)

    return decomp, vlist_table


def visualizeGraph(topo, layout, node_size=150, iterations=100, show_edge_labels=False):
    g = topo
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
