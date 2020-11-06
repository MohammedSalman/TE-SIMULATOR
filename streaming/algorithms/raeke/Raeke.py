import ast
from itertools import chain
import copy
import math
import networkx as nx
from algorithms.raeke.make_frt_tree import make_frt_tree, create_topology
from algorithms.raeke.generate_rt import generate_rt, RTNode
from itertools import permutations
import time


def measure_time(f):
    def timed(*args, **kw):
        ts = time.time()
        result = f(*args, **kw)
        te = time.time()

        # print ('%r (%r, %r) %2.2f sec' % (f.__name__, args, kw, te-ts))
        print('%r  %2.2f sec' % (f.__name__, te - ts))
        return result

    return timed


def add_or_increment_path(fd, p, r):  # (flow_decomp, path, probability): flow_decomp
    # print(p)
    # key = tuple(p)
    key = repr(p)
    # print(key)
    if key not in fd:
        fd[key] = r
    else:
        fd[key] += r
    return fd


def edge_to_physical(routing_tree, edge):
    tbl = routing_tree[1]
    return tbl[edge]


def path_to_physical(routing_tree, path):
    path_segments = list(map(lambda e: edge_to_physical(routing_tree, e), path))
    # print("===================> ", list(chain.from_iterable(path_segments)))
    return list(chain.from_iterable(path_segments))


def construct_path_down(tree, dst):
    center = tree.v
    children = tree.list_of_trees

    if not children:
        if center == dst:
            return []
        else:
            raise Exception("get_path: dst not in tree")
    else:
        child = None
        for c in children:
            if dst in c.v_set:
                child = c
                break
        child_center = child.v
        tail = construct_path_down(child, dst)
        return [(center, child_center)] + tail


def construct_path_up(tree, src):
    path_down = construct_path_down(tree, src)
    tups_reversed = list(map(lambda x: (x[1], x[0]), path_down))
    return tups_reversed


def get_path_halves(routing_tree, src, dst):
    # print("routing tree: ", routing_tree)
    # u, tbl, tree = routing_tree
    u = routing_tree[0]
    tbl = routing_tree[1]
    tree = routing_tree[2]

    cs = tree.list_of_trees
    src_subtree_opt = None
    for sub in cs:
        if src in sub.v_set:
            src_subtree_opt = sub

    if src_subtree_opt is None:
        raise Exception("get_path: src not in tree")
    src_subtree = copy.deepcopy(src_subtree_opt)

    src_set = src_subtree.v_set
    if dst in src_set:
        return get_path_halves((u, tbl, src_subtree), src, dst)
    else:
        path_up = construct_path_up(tree, src)
        path_down = construct_path_down(tree, dst)
        return path_up, path_down


def get_path(routing_tree, src, dst):
    path_up, path_down = get_path_halves(routing_tree, src, dst)
    return path_up + path_down  # concatination


def exp_weight(epsilon, usage):
    return math.exp(epsilon * usage)


def usage_of_tree(tree):
    lst, _, _ = tree
    return lst


def usage_of_structure(tree):
    return usage_of_tree(tree)


def select_structure(topo, nodes):
    tree = make_frt_tree(topo)
    node_list = list(copy.deepcopy(nodes))
    return generate_rt(topo, tree, node_list), 1.0


def hedge(epsilon, delta, topo, d, nodes, usage_table):
    struct, c_min = select_structure(topo, nodes)
    usage_vec = usage_of_structure(struct)

    max_usage = max([a[1] for a in usage_vec])
    # Scale usages s.t. max is 1 (width reduction)
    scaled_usage = list(map(lambda x: (x[0], x[1] / max_usage), usage_vec))

    # Add cumulative usage
    for (edge, usage) in scaled_usage:
        usage_table[edge] = usage_table[edge] + usage

    sum_weights = sum(list(map(lambda usag: exp_weight(epsilon, usag), list(usage_table.values()))))

    # Reweight edges in graph
    temp_topo_dict = nx.to_dict_of_dicts(topo)
    edges = topo.edges()
    for edge in edges:
        usage = usage_table[edge]
        temp_topo_dict[edge[0]][edge[1]]['weight'] = exp_weight(epsilon, usage) / sum_weights
    reweighted = nx.Graph(temp_topo_dict)

    return struct, 1 / max_usage, reweighted, usage_table


def hedge_iterations(epsilon, topo, d, nodes):
    # This uses the functions defined in the above input
    # module to run the multiplicative weights algorithm.
    # The outputs are, in this order:
    # 1. The number of iterations the algorithm ran for.
    # 2. A list of structures (e.g., paths or trees) with associated
    #   weights. The intended use is that when something needs to be routed,
    #   one should normalize and use the weights as a
    #   probability distribution, select a structure accordingly, and
    #   route using that structure.
    # 3. The original topology, but with weights modified to reflect the final
    #    state of the algorithm.
    #

    num_edges = len(nodes)
    delta = (epsilon ** 2.0) / math.log(num_edges)

    def loop(n, trees, topo, acc_usage, table):
        new_tree, w, new_topo, new_tb = hedge(epsilon, delta, topo, d, nodes, table)
        if w + acc_usage >= 1:
            final_weight = 1 - acc_usage
            return n + 1, [(new_tree, final_weight)] + trees, new_topo
        else:
            return loop(n + 1, ([(new_tree, w)] + trees), new_topo, (w + acc_usage), new_tb)

    init_table = dict()
    for e in topo.edges():
        init_table[e] = 0.0

    return loop(0, [], topo, 0.0, init_table)


def remove_cycles(path, src, dst):
    # seen = []
    # g = nx.DiGraph(path)
    # #print(nx.recursive_simple_cycles(g))
    # # [[0], [2], [0, 1, 2], [0, 2], [1, 2]]
    # cycles_to_be_removed = nx.recursive_simple_cycles(g)
    # for cycle in cycles_to_be_removed:
    #     edges_to_be_removed = [(cycle[i], cycle[(i+1)% len(cycle)] ) for i in range(len(cycle))]
    #     for e in edges_to_be_removed:
    #         if e in seen or (e[1], e[0]) in seen:
    #             continue
    #         path.remove(e)
    #         seen.append(e)
    #         seen.append((e[1], e[0]))
    # return path
    g = nx.Graph(path)
    assert (nx.is_connected(g))
    path = list(nx.shortest_simple_paths(g, src, dst))[0]
    return path


def calculate_PathMap(mw_solution, src, dst):
    acc = {}
    for mw_item in mw_solution:
        def anonymous(acc, mw_item):
            rt = mw_item[0]
            p = mw_item[1]

            routing_path = get_path(rt, src, dst)
            # print(routing_path)
            physical_path = path_to_physical(rt, routing_path)
            # print(physical_path)
            physical_path = remove_cycles(physical_path, src, dst)
            return add_or_increment_path(acc, physical_path, p)

        acc = anonymous(acc, mw_item)
    # print(acc)
    return acc


def solve(topo, d):
    hosts = topo.nodes()
    t = topo
    end_points = hosts
    epsilon = 0.1
    _, mw_solution, _ = hedge_iterations(epsilon, t, d, end_points)

    #  @measure_time
    def paths(src, dst):
        return calculate_PathMap(mw_solution, src, dst)

    # print(paths(0, 1))
    # print(paths(1, 0))
    # TODO: calculate routes from S to D only once,
    #  to calculate routes from D to S,
    #  just reverse routes.
    #  Assuming both links are symmetric.

    # for src in range(len(hosts)): # not needed code
    #     for dst in range(len(hosts)):
    #         if src == dst:
    #             continue
    #         else:
    #             print("from ", src, " to ", dst, " -> ", paths(src, dst))
    #             paths(src, dst)

    routing_scheme = {}
    all_pairs = list(permutations(topo.nodes(), 2))  # ingress, egress pairs
    # print("all pairs in raeke: ", all_pairs)
    for pair in all_pairs:
        routing_scheme[pair] = {}
        s = pair[0]
        d = pair[1]
        routes = paths(s, d)
        for path_n, item in enumerate(routes):
            path = item
            ratio = routes[item]
            variableName = 'x' + "_Index_" + str(path_n) + '_s' + str(s) + '_d' + str(d)
            routing_scheme[pair][variableName] = {}
            routing_scheme[pair][variableName]['path'] = ast.literal_eval(path)
            routing_scheme[pair][variableName]['ratio'] = ratio
    return routing_scheme
    # print("final routing scheme: ", routing_scheme)
        # for pair in self.all_pairs:
    #     rs[pair] = {}
    #     s = pair[0]
    #     d = pair[1]
    #
    #     for path_n, path in enumerate(list(self.k_shortest_paths(s, d))):
    #         if path_n == self.numCandPath:
    #             break
    #         # routing scheme example:
    #         # test = {'pair1': {'paths': {'var1': [1, 2, 3]}, 'ratio': 0.5}, 'pair2': 'test'}
    #         variableName = 'x' + "_Index_" + str(path_n) + '_s' + str(s) + '_d' + str(d)
    #         rs[pair][variableName] = {}
    #         rs[pair][variableName]['path'] = path
    #         rs[pair][variableName]['ratio'] = 0.0


# if __name__ == '__main__':
#     import time
#
#     topo_ = create_topology()
#     nodes = list(topo_.nodes())
#     d = None
#     tic = time.time()
#     solve(topo_, d)
#     print("time taken: ", time.time() - tic)

def calculate_raeke_scheme(topo):
    # print(routing_scheme)
    nodes = list(topo.nodes())
    d = None
    # tic = time.time()
    routing_scheme = solve(topo, d)
    # print("routing scheme is : \n")
    # print(routing_scheme)
    return routing_scheme
    # print("time taken: ", time.time() - tic)
