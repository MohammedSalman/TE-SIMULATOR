# from gurobipy import *
from itertools import islice, combinations
import networkx as nx
import time


class Shortest_Path:

    def __init__(self, topo, routing_scheme, algorithm_type, num_cand_path):
        self.topo = topo
        self.numCandPath = num_cand_path
        self.all_pairs = list(combinations(self.topo.nodes(), 2))  # ingress, egress pairs

        self.demandsToRoutes = {}
        self.pathsCost = {}
        self.linksToRoutes = {}  # Mapping a link to all routes passing that link

        self.algorithm_type = algorithm_type
        if self.algorithm_type == 'ecmp':
            return self.calculate_ecmp_paths(routing_scheme)
        if self.algorithm_type == 'ksp':
            return self.calculate_ksp_paths(routing_scheme)

    def k_shortest_paths(self, source, target):
        return (islice(nx.shortest_simple_paths(self.topo, source, target, weight='weight'), self.numCandPath))

    def calculate_ksp_paths(self, rs):
        global pathCost
        for pair in self.all_pairs:
            rs[pair] = {}
            s = pair[0]
            d = pair[1]

            for path_n, path in enumerate(list(self.k_shortest_paths(s, d))):
                if path_n == self.numCandPath:
                    break
                # routing scheme example:
                # test = {'pair1': {'paths': {'var1': [1, 2, 3]}, 'ratio': 0.5}, 'pair2': 'test'}
                variableName = 'x' + "_Index_" + str(path_n) + '_s' + str(s) + '_d' + str(d)
                rs[pair][variableName] = {}
                rs[pair][variableName]['path'] = path
                rs[pair][variableName]['ratio'] = 0.0


    def calculate_ecmp_paths(self, rs):
        # print("routing scheme is: ", rs)
        global pathCost
        for pair in self.all_pairs:
            rs[pair] = {}
            s = pair[0]
            d = pair[1]
            previous_path_cost = 0
            for path_n, path in enumerate(list(self.k_shortest_paths(s, d))):
                pathCost = 0
                for vi in range(len(path) - 1):
                    pathCost += self.topo[path[vi]][path[vi + 1]]['weight']

                if pathCost != previous_path_cost and path_n != 0:
                    break
                previous_path_cost = pathCost

                # routing scheme example:
                # test = {'pair1': {'paths': {'var1': [1, 2, 3]}, 'ratio': 0.5}, 'pair2': 'test'}
                variableName = 'x' + "_Index_" + str(path_n) + '_s' + str(s) + '_d' + str(d)
                rs[pair][variableName] = {}
                rs[pair][variableName]['path'] = path
                rs[pair][variableName]['ratio'] = 0.0
                # print(rs)
                # print(path)
                # for index in range(len(path) - 1):
                #     self.linksToRoutes[(path[index], path[index + 1])].append(variableName)
                # self.demandsToRoutes[(s, d)].append(variableName)

                # s, d = d, s  # Swapping
        # re calculate the other symmetric half of the routing scheme:
        # for i in range(2):  # len(pair)
        #   if i == 1:
        #     path = path[::-1]  # Reverse path, so we don't need to run k_shortest_path again!
