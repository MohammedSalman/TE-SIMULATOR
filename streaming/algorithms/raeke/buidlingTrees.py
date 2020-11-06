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


def level_decomp(cluster):
    if isinstance(cluster, Node):
        [Single([sett]) for sett in cluster.v_set if len(cluster.v_set) == 1]
        #print(cluster.list_of_trees[0].v)


def print_tree(tree):
    if isinstance(tree, Node):
        print("Node ", tree.v, " with set: ", tree.v_set, "that has ", len(tree.list_of_trees), " trees")
        for tr in tree.list_of_trees:
            print_tree(tr)
    if isinstance(tree, Leaf):
        print("Leaf ", tree.v, " with set: ", tree.v_set)

    if isinstance(tree, Single):
        print("Single ", " with set: ", tree.v_set)

# if __name__ == "__main__":
#     x = Node(5, [6], [Node(1, [2], [])])
#     level_decomp(x)
#     print_tree(x)

    # print(x.list_of_trees)
    # y = NumNode(4)
    # p = PlusNode(x, y)
    # t = TimesNode(p, NumNode(6))
    # root = PlusNode(t, NumNode(3))
