import networkx as nx
import time
import pickle
import fnss as fnss
import matplotlib.pyplot as plt
import random
from programsettings import VISUALIZE_TOPOLOGY, WAITING_TIME
from multiprocessing import Process
from gurobipy import *
from config import CAPACITY_SET, CAPACITY_TYPE, TOPOLOGY_SEED
from itertools import product
from config import NETWORK_LOAD, TM_TYPE, TOPOLOGY_SOURCE, TOPOLOGY_PATH
from trafficgenerator import TrafficGenerator


class Topology:
    """
    Stores network topology graph, configures capacities, visualize graph.
    """

    def __init__(self, num_nodes, num_links, OutputDirName, shared_dict, congestions_over_all_tm_dict,
                 latency_and_demand_fraction_dict):
        # self.q = q
        self.num_nodes = num_nodes
        self.num_links = num_links
        self.topo_id = random.random()

        if TOPOLOGY_SOURCE == 'random':
            self.topo = self.create_random_topology(num_nodes, num_links, TOPOLOGY_SEED)
            if self.topo is not None:
                self.cap_type = CAPACITY_TYPE
                self.cap_set = CAPACITY_SET
                if self.cap_type == 'edge_betweenness':
                    self.set_capacities()
                    # self.set_weights()

            # save the topology:
            random_file_name = "random_topo" + time.strftime("%Y-%m-%d-H%H-M%M-S%S") + ".pickle"
            pickle_out = open("streaming/data/topologies/random/" + random_file_name, "wb")
            pickle.dump(self.topo, pickle_out)
            pickle_out.close()
            self.topology_file_name = random_file_name
        if TOPOLOGY_SOURCE == 'file':
            if TOPOLOGY_PATH.endswith('dot'):
                self.topo = self.read_dot_topology_from_file()
            if TOPOLOGY_PATH.endswith('graphml'):
                self.topo = self.read_graphml_topology_from_file()
            if TOPOLOGY_PATH.endswith('pickle'):
                pickle_in = open(TOPOLOGY_PATH, "rb")
                self.topo = pickle.load(pickle_in)
            self.topology_file_name = TOPOLOGY_PATH.split('/')[-1]
        if self.topo is not None:
            # capacity_unit may not exist if topology source is 'file'. capacity_unit is needed for fnss.
            if 'capacity_unit' not in self.topo.graph:
                self.topo.graph['capacity_unit'] = 'Gbps'
                # build a unique id (hash code) for this topology to track the sequence of TM.
            # beware that this hash code is different at each runtime.
            topo_string = nx.to_dict_of_dicts(self.topo)

            self.topo_hash_code = hash(str(topo_string))

            if VISUALIZE_TOPOLOGY:
                self.visualizeGraph('spring', node_size=175, show_edge_labels=True)

            if isinstance(NETWORK_LOAD, str):
                LOAD = [float(NETWORK_LOAD)]
            elif isinstance(NETWORK_LOAD, list):
                LOAD = NETWORK_LOAD
            else:
                raise ValueError('UNKNOWN Traffic Matrix load')

            if isinstance(TM_TYPE, str):
                TM_TYPES_ = [float(NETWORK_LOAD)]
            elif isinstance(TM_TYPE, list):
                TM_TYPES_ = TM_TYPE
            else:
                raise ValueError('UNKNOWN Traffic Matrix type')

            # print(self.topo.edges(data=True))

            procs = []

            for network_load, tm_type in product(LOAD, TM_TYPES_):
                proc = Process(target=TrafficGenerator,
                               args=(
                                   network_load, self, tm_type, OutputDirName, self.topology_file_name, shared_dict,
                                   congestions_over_all_tm_dict, latency_and_demand_fraction_dict))
                procs.append(proc)
            for proc in procs:
                proc.start()
                print("started at time: ", time.time())
            for proc in procs:
                proc.join()
                print("joined at time: ", time.time())

                # for i in self.chunks(procs, CPU_COUNT):
                #     for j in i:
                #         j.start()
                #     for j in i:
                #         j.join()
                #         print("how many chunks", "at time: ", time.time())

            # else:
            #     objects = [RoutingScheme(network_load, self, TM_TYPES_, OutputDirName) for network_load, R in
            #                product(LOAD, range(Nu_of_TMs_Per_TOPO))]

    @staticmethod
    def chunks(ll, nn):
        for index in range(0, len(ll), nn):
            yield ll[index:index + nn]

    def set_capacities(self):
        fnss.set_capacities_edge_betweenness(self.topo, self.cap_set, 'Gbps')
        # set_capacities_betweenness_gravity(g, capacity_set, 'Gbps')
        # set_capacities_communicability_gravity(g, capacity_set, 'Gbps')

    # def set_weights(self):
    #     if WEIGHT_SETTING == 'fixed':
    #         fnss.set_weights_constant(self.topo, FIXED_WEIGHT_VALUE)
    #     if WEIGHT_SETTING == 'inv_cap':
    #         fnss.set_weights_inverse_capacity(self.topo)

    @staticmethod
    def create_random_topology(n, l, TOPOLOGY_SEED):
        printed = False

        if l <= n > 10:
            return None
        if l > ((n * (n - 1)) / 2):
            return None
        tic = time.time()
        while True:
            g = nx.dense_gnm_random_graph(n, l, seed=TOPOLOGY_SEED)
            if nx.is_connected(g):
                if printed is True:
                    logging.warning('Found a connected graph n = %d, l = %d', n, l)
                return g.to_directed()
            if printed is False:
                logging.warning('Disconnected graph, trying another graph! n = %d, l = %d', n, l)
                printed = True
            if time.time() - tic > WAITING_TIME:
                logging.warning('Could not find a connected graph n = %d, l = %d', n, l)
                exit(0)
                # return None

    def visualizeGraph(self, layout, node_size=150, iterations=100, show_edge_labels=False):
        g = self.topo
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

    def read_dot_topology_from_file(self):
        g = nx.networkx.drawing.nx_pydot.read_dot(TOPOLOGY_PATH)
        # g = nx.read_graphml(TOPOLOGY_PATH) # node_type=int)
        # print(g.edges(data=True))

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
            cost = int(g[source][target][0]['cost'])
            if cost == 0:
                cost = 1
            g[source][target][0]['weight'] = cost
        # removing unneeded properties in the graph
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
        # visualizeGraph(g, 'spring', show_edge_labels=False)
        # converting graph from multigraph to single graph

        g = nx.Graph(g)
        g = nx.to_directed(g)
        # print(g.edges(data=True))
        return g

    def read_graphml_topology_from_file(self):
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
