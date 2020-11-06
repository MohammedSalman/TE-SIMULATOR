import copy
import networkx as nx

from algorithms.raeke.make_frt_tree import create_topology, \
    make_frt_tree, Single, Leaf, Node, print_tree


def print_rt_tree(tree):
    if isinstance(tree, TreeRTNode):
        print("TreeRTNode ", tree.v, " with set: ", tree.v_set, "that has ", len(tree.list_of_trees), " trees")
        for tr in tree.list_of_trees:
            print_rt_tree(tr)


def print_rt_with_paths_tree(tree):
    if isinstance(tree, RTNode):
        print("RTNode ", tree.v, " with set: ", tree.v_set, "that has ", len(tree.list_of_trees), " trees")
        for tr in tree.list_of_trees:
            print_rt_with_paths_tree(tr)

class TreeRTNode:
    def __init__(self, v, v_set, list_of_trees):
        self.v = v
        self.v_set = v_set
        self.list_of_trees = list_of_trees

        assert (isinstance(v, int))
        assert (isinstance(v_set, list))
        assert (isinstance(list_of_trees, list))


class RTNode:
    def __init__(self, v, v_set, list_of_trees):
        self.v = v
        self.v_set = v_set
        self.list_of_trees = list_of_trees

        assert (isinstance(v, int))
        assert (isinstance(v_set, list))
        assert (isinstance(list_of_trees, list))


def generate_rt(orig_topo, tree, endpoints):
    tree_metric = tree[0]
    vlist_table = tree[1]

    tree_table = dict()

    def add_path(src, dst):
        _, path = vlist_table[(src, dst)]
        tree_table[(src, dst)] = path

    def shortest_path(src, dst):
        return tree_table[(src, dst)]

    def get_cluster(tre):
        if isinstance(tre, Single):
            sett = tre.v_set
        if isinstance(tre, Leaf):
            sett = tre.v_set
        if isinstance(tre, Node):
            sett = tre.v_set
        return sett

    def intersection(lst1, lst2):

        # Use of hybrid method
        temp = set(lst2)
        lst3 = [value for value in lst1 if value in temp]
        return lst3

    # Make a tree with the root of the current decomposition as root,
    # with paths to all endpoints.
    def make_tree_downward(tree, endpts):

        def calculate_new_children(children):
            acc = []
            for subtree in children:
                def anonymous(acc, subtree):
                    sub_cluster = get_cluster(subtree)
                    new_endpts = intersection(endpts, sub_cluster)
                    if not new_endpts:
                        return acc
                    else:
                        child = make_tree_downward(subtree, new_endpts)
                        return [child] + acc

                acc = anonymous(acc, subtree)
            return acc

        if isinstance(tree, Single):
            sett = tree.v_set
            elt = sett[0]  # it only has one item because it is Single
            return TreeRTNode(elt, sett, [])
        if isinstance(tree, Leaf):
            raise Exception("generate_rrt: no leaves allowed in frt_tree")
        if isinstance(tree, Node):
            center = tree.v
            sett = tree.v_set
            children = tree.list_of_trees

            # for tr in children:
            #     print_tree(tr)

            new_children = calculate_new_children(children)

            # for tr in new_children:
            #     print_rt_tree(tr)
            # print("********************************")
            return TreeRTNode(center, endpts, new_children)

    endpt_set = copy.deepcopy(endpoints)
    rt_no_paths = make_tree_downward(tree_metric, endpt_set)
    usage_table = dict()

    # Returns the set of all edges that have exactly one endpoint
    # in the given vertex set.
    def edges_in_boundary(vertex_set):
        b_edges = nx.edge_boundary(orig_topo, vertex_set)
        return b_edges

    def map_and_compute_usage(tree):
        center = tree.v
        sett = tree.v_set
        children = tree.list_of_trees

        def calculate_root_children(children):
            acc = []
            for next in children:
                def anonymous(acc, next):
                    c_center = next.v
                    c_set = next.v_set
                    add_path(c_center, center)
                    add_path(center, c_center)
                    path_up = shortest_path(c_center, center)
                    boundary_edges = edges_in_boundary(c_set)

                    temp_topo_dict = nx.to_dict_of_dicts(orig_topo)
                    total = 0
                    for edge in boundary_edges:
                        total += temp_topo_dict[edge[0]][edge[1]]['capacity']
                    usage = total

                    # Adds a given amount of usage to both directions
                    def add_usage(amount, edge):
                        def add_to(edge):
                            if edge in usage_table:
                                old_usage = usage_table[edge]
                            else:
                                old_usage = 0
                            usage_table[edge] = old_usage + amount

                        add_to(edge)

                        inv_edge = (edge[1], edge[0])

                        add_to(inv_edge)

                    # update usages for all edges on the path
                    # map(lambda x: add_usage(usage, x), path_up)
                    for x in path_up:
                        add_usage(usage, x)

                    # Recursively convert the rest of the tree
                    subtree = map_and_compute_usage(next)
                    return [subtree] + acc

                acc = anonymous(acc, next)
            return acc

        root_children = calculate_root_children(children)

        if root_children == []:
            init = sett
        else:
            init = []

        def make_reduced_set(root_children):
            acc = init
            for child in root_children:
                def anonymous(acc, child):
                    c_set = child.v_set
                    return list(set(c_set) | set(acc))  # Union

                acc = anonymous(acc, child)
            return acc

        reduced_set = make_reduced_set(root_children)
        return RTNode(center, reduced_set, root_children)

    routing_tree = map_and_compute_usage(rt_no_paths)
    # usage_vec =
    temp_topo_dict = nx.to_dict_of_dicts(orig_topo)
    # for edge in usage_table:
    #     print("cap is ", temp_topo_dict[edge[0]][edge[1]]['capacity'])
    usage_vec = [(edge, usage_table[edge] / temp_topo_dict[edge[0]][edge[1]]['capacity']) for edge in usage_table]
    # print_rt_with_paths_tree(routing_tree)
    # print(usage_vec)
    return usage_vec, tree_table, routing_tree


# if __name__ == '__main__':
#     topo = create_topology()
#     # topo_dict = nx.to_dict_of_dicts(topo)
#     # print(topo_dict)
#     # visualizeGraph('spring', node_size=175, show_edge_labels=False)
#
#     # print(nx.to_dict_of_dicts(topo))
#     tree = make_frt_tree(topo)
#     endpoints = list(topo.nodes())
#     struct = generate_rt(topo, (tree[0], tree[1]), endpoints)
