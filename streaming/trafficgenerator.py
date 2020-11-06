import time
import numpy as np
import copy
import random
import pickle
from programsettings import CPU_COUNT
from multiprocessing import Process, Lock, Value, Manager
from itertools import product
from config import Nu_of_TMs_Per_TOPO, PATH_BUDGET, n, period, FIXED_WEIGHT_VALUE
from fnss import *
from utilities import chunks, return_algorithms_names
from routingscheme import RoutingScheme
from algorithms.raeke import Raeke
from config import DEMAND_SOURCE, TOPOLOGY_PATH
import csv
import fnss as fnss


class TrafficGenerator:
    """
        Generates different types of traffic matrices: Gravity, Bimodal ... etc.
    """

    def __init__(self, network_load, topology_obj, tm_type, OutputDirName, topology_file_name, shared_dict,
                 congestions_over_all_tm_dict,
                 latency_and_demand_fraction_dict):
        # self.algo_name = routingscheme.algo_name
        self.topology_file_name = topology_file_name
        self.all_algo = return_algorithms_names()
        self.routingscheme = topology_obj
        # self.trafficgenerator = routingscheme
        self.network_load = network_load
        self.tm_type = tm_type
        # self.q = q
        # self.routing_scheme = routingscheme.routing_scheme
        # print(self.algo_name, "\n", self.routing_scheme)

        self.topo = copy.deepcopy(topology_obj.topo)
        # self.tm = {}
        # for s in self.topo.nodes():
        #     self.tm[s] = {}
        #     for d in self.topo.nodes():
        #         self.tm[s][d] = 0.0

        # a dictionary with values to make scaling for all models the same
        self.scaling = {'nucci_stationary': 4}
        self.matrices_sequence = []

        # calculating number of traffic matrices for the normalization in latency_fraction distribution

        demand_directory = '/'.join(TOPOLOGY_PATH.replace('topologies', 'demands').split('/')[:-1]) + '/'

        demand_file_name = 'demand_' + self.topology_file_name
        if DEMAND_SOURCE == 'file':
            try:
                print("Fetching demands from: ", demand_directory + demand_file_name)
                pickle_in = open(demand_directory + demand_file_name, "rb")
                self.matrices_sequence = pickle.load(pickle_in)

            except FileNotFoundError:
                print("Demand file doesn't exist!")
                exit(0)
        else:
            if self.tm_type == 'random':
                # print("in random")
                tic = time.time()
                temp_matrices_sequence = []
                for i in range(Nu_of_TMs_Per_TOPO):
                    rnd = random.randint(0, 1)
                    if rnd == 0:
                        self.matrices_sequence = []
                        self.generateGravityTM(1)
                        temp_matrices_sequence.append(self.matrices_sequence[0])
                    if rnd == 1:
                        self.matrices_sequence = []
                        self.generateBimodalTM(1)
                        temp_matrices_sequence.append(self.matrices_sequence[0])
                    # if rnd == 2:
                    #     self.matrices_sequence = []
                    #     self.generateNucci_stationary_TM(1)
                    #     temp_matrices_sequence.append(self.matrices_sequence[0])

                self.matrices_sequence = []
                self.matrices_sequence = copy.deepcopy(temp_matrices_sequence)
                # print("Done calculating RANDOM all the traffic matrices after: ", time.time() - tic, " seconds")

            if self.tm_type == 'gravity':
                self.generateGravityTM()
            if self.tm_type == 'bimodal':
                self.generateBimodalTM()
            if self.tm_type == 'nucci':
                self.generateNucciTM()
            if self.tm_type == 'nucci_stationary':
                self.generateNucci_stationary_TM()
            if self.tm_type == 'sin_cyclostationary':
                self.sin_cyclostationary_TM()

            # saving demands to file
            pickle_out = open(demand_directory + demand_file_name, "wb")
            pickle.dump(self.matrices_sequence, pickle_out)
            pickle_out.close()
        # self.matrices_sequence = [
        #     {
        #         0: {0: 0.0, 1: 0.281, 2: 0.704, 3: 0.089},
        #         1: {0: 0.754, 1: 0.0, 2: 0.505, 3: 1.356},
        #         2: {0: 1.140, 1: 0.51, 2: 0.0, 3: 1.044},
        #         3: {0: 0.177, 1: 0.433, 2: 0.642, 3: 0.0},
        #     }
        # ]
        # for tm in self.matrices_sequence:
        #     all_0 = True
        #     for s in tm:
        #         for d in tm[s]:
        #             if s == d:
        #                 continue
        #             if random.random() > 0.6:
        #                 tm[s][d] = 0.0
        #             if tm[s][d] != 0.0:
        #                 all_0 = False
        #     if all_0:
        #         tm[0][1] = 1.0

        # self.matrices_sequence = [
        #     {
        #         0: {0: 0.0, 1: 0.0, 2: 3.7277},
        #         1: {0: 0.0, 1: 0.0, 2: 0.0},
        #         2: {0: 2.9428, 1: 0.0, 2: 0.0},
        #
        #     }
        # ]

        # self.matrices_sequence = self.matrices_sequence * 1
# 0	0	3.727736654	0	0	0	2.942859877	0	0
        print("all algo in traffic generators: ", self.all_algo)

        # topo_inv_cap = self.set_weights('inv_cap', copy.deepcopy(self.topo))
        topo_fixed_weights = self.set_weights('fixed', copy.deepcopy(self.topo))

        procs = []
        for algorithm_name, num_cand_path in product(self.all_algo, PATH_BUDGET):

            if 'RAEKE' in algorithm_name:
                # if 'inv_cap' in algorithm_name:
                #     raeke_routing_scheme = Raeke.calculate_raeke_scheme(copy.deepcopy(topo_inv_cap))
                # if 'fixed' in algorithm_name:
                raeke_routing_scheme = Raeke.calculate_raeke_scheme(copy.deepcopy(topo_fixed_weights))



            else:
                raeke_routing_scheme = None

            proc = Process(target=RoutingScheme, args=(topo_fixed_weights,
                                                       algorithm_name, num_cand_path, raeke_routing_scheme,
                                                       self.matrices_sequence, OutputDirName, self,
                                                       shared_dict, congestions_over_all_tm_dict,
                                                       latency_and_demand_fraction_dict))

            # if 'inv_cap' in algorithm_name:
            #     # print("topo inv cap is: ", topo_inv_cap.edges(data=True))
            #     proc = Process(target=RoutingScheme, args=(topo_inv_cap,
            #                                                algorithm_name, num_cand_path, raeke_routing_scheme,
            #                                                self.matrices_sequence, OutputDirName, self,
            #                                                shared_dict, congestions_over_all_tm_dict,
            #                                                latency_and_demand_fraction_dict))
            # if 'fixed' in algorithm_name:
            #     # print("topo fixed is: ", topo_fixed_weights.edges(data=True))
            #     proc = Process(target=RoutingScheme, args=(topo_fixed_weights,
            #                                                algorithm_name, num_cand_path, raeke_routing_scheme,
            #                                                self.matrices_sequence, OutputDirName, self,
            #                                                shared_dict, congestions_over_all_tm_dict,
            #                                                latency_and_demand_fraction_dict))

            procs.append(proc)

        # TODO: delete this if not needed in the future:
        # saving demands as CSV for analysis:
        try:
            with open('demand.csv', 'w', newline='') as csvfile:
                writer = csv.writer(csvfile, delimiter=',')
                for tm in self.matrices_sequence:
                    row = []
                    for src in tm:
                        for dst in tm:
                            row.append(tm[src][dst])
                    writer.writerow(row)
        except:
            print("couldn't save demands to demand.csv saving to demand_1.csv instead")
            try:
                with open('demand_1.csv', 'w', newline='') as csvfile:
                    writer = csv.writer(csvfile, delimiter=',')
                    for tm in self.matrices_sequence:
                        row = []
                        for src in tm:
                            for dst in tm:
                                row.append(tm[src][dst])
                        writer.writerow(row)
            except:
                print("couldn't save to demand_1.csv either!")

        # print(self.matrices_sequence)
        # if YATES_SCHEME:
        #     proc = Process(target=RoutingScheme, args=(
        #         None, None, num_cand_path, self.matrices_sequence, OutputDirName,
        #         self, shared_dict))
        #     procs.append(proc)

        for i in chunks(procs, len(self.all_algo)):
            # print(len(i))
            for j in i:
                j.start()
            for j in i:
                j.join()

    def set_weights(self, weight_type, topo):
        # if 'fixed' in algorithm_name:
        #     fnss.set_weights_constant(topo, FIXED_WEIGHT_VALUE)
        # if 'inv_cap' in algorithm_name:
        #     fnss.set_weights_inverse_capacity(topo)

        if weight_type is 'inv_cap':
            fnss.set_weights_inverse_capacity(topo)
            # enable if you want to set them manually.
            # for s, d in topo.edges():
            #     cap = topo[s][d]['capacity']
            #     topo[s][d]['weight'] = 1.0 / cap

        if weight_type is 'fixed':
            for s, d in topo.edges():
                topo[s][d]['weight'] = 1.0

        return topo

    def generateNucciTM(self):
        demandVolumes = static_traffic_matrix(self.topo, mean=0.5, stddev=0.5, max_u=self.network_load)
        self.tm = demandVolumes.flow

    def sin_cyclostationary_TM(self):
        demandVolumes = sin_cyclostationary_traffic_matrix(self.topo, mean=0.5, stddev=0.25, gamma=0.9, log_psi=-0.45,
                                                           delta=0.2, n=n, periods=period,
                                                           max_u=self.network_load * 2.5)
        for i in range(n * period):
            self.matrices_sequence.append(demandVolumes.matrix[i].flow)

        # alignment with other tm types
        for tm in self.matrices_sequence:
            for src in range(len(tm)):
                tm[src][src] = 0.0
        # for tm in self.matrices_sequence:
        #     for src in range(len(tm)):
        #         for dst in range(len(tm)):
        #             if src == dst:
        #                 tm[src][dst] = 0.0

    def generateNucci_stationary_TM(self, nu_tm=None):
        # tic = time.time()
        # print(" in nucci stationary")
        if nu_tm is None:
            nu_tm = Nu_of_TMs_Per_TOPO
        traffic_matrix = stationary_traffic_matrix(self.topo, mean=0.5, stddev=0.05, gamma=0.7, log_psi=0.1,
                                                   n=nu_tm,
                                                   max_u=self.network_load * self.scaling['nucci_stationary'])
        # matrices = []
        matrices_obj = traffic_matrix.matrix
        for matrix in matrices_obj:
            self.matrices_sequence.append(matrix.flow)

        for tm in self.matrices_sequence:
            for src in range(len(tm)):
                tm[src][src] = 0.0
        # print("Done calculating all the traffic matrices after: ", time.time() - tic, " seconds")

    # def generateBimodalTM(self, nu_tm=None):
    #     if nu_tm is None:
    #         nu_tm = Nu_of_TMs_Per_TOPO
    #     tm = {}
    #     for s in self.topo.nodes():
    #         tm[s] = {}
    #         for d in self.topo.nodes():
    #             tm[s][d] = 0.0
    #     Cap = {}
    #     totalcap = 0
    #     for src in self.topo:
    #         cap = 0
    #         for dst in self.topo[src]:
    #             cap += self.topo[src][dst]['capacity']
    #         Cap[src] = cap
    #         totalcap += cap
    #     for n in range(nu_tm):
    #         for src in tm:
    #             outgoing = Cap[src]
    #             SIG = 20.0 / (150 * 150)
    #             for dst in tm:
    #                 if src == dst:
    #                     tm[src][dst] = 0
    #                     continue
    #                 if nr.random() < 0.2:
    #                     FRAC = 1.67 * self.network_load
    #                 else:
    #                     FRAC = 0.7 * self.network_load
    #                 tm[src][dst] = (nr.normal(1, SIG) * FRAC * outgoing / (float(len(tm[src])))) / 2.0
    #                 # print(src, dst, tm[src][dst])
    #         temp_tm = copy.deepcopy(tm)
    #         # print("temp_tm: ", temp_tm)
    #         self.matrices_sequence.append(temp_tm)
    #     # print("all matrices: ", self.matrices_sequence)
    #
    def generateBimodalTM(self, nu_tm=None):
        if nu_tm is None:
            nu_tm = Nu_of_TMs_Per_TOPO
        tm = {}
        for s in self.topo.nodes():
            tm[s] = {}
            for d in self.topo.nodes():
                tm[s][d] = 0.0
        Cap = {}
        # for src in self.topo:
        #     cap = 0
        #     for dst in self.topo[src]:
        #         cap += self.topo[src][dst]['capacity']
        #     Cap[src] = cap

        for src in self.topo.nodes():
            cap = 0
            for neighbour in self.topo[src]:
                cap += self.topo[src][neighbour]['capacity']
            Cap[src] = cap
            print("Cap of src ", src, " is ", Cap[src])

        for n in range(nu_tm):
            for src in tm:
                outgoing = Cap[src]
                for dst in tm:
                    if src == dst:
                        tm[src][dst] = 0.0
                        continue
                    if np.random.random() > 0.2:
                        mu = 0.0009 * outgoing
                        std = outgoing / 5.0
                        min_ = mu - (3 * std)
                        max_ = mu + (3 * std)
                        # while True:
                        #     rnd = np.random.normal(mu, std)
                        #     if min_ < rnd < max_:
                        #         break
                        while True:
                            rnd = np.random.normal(mu, std)
                            while rnd < 0.0:
                                rnd = np.random.normal(mu, std)
                            break
                        # tm[src][dst] = ((rnd - min_) / (max_ - min_)) * outgoing * self.network_load
                        tm[src][dst] = rnd * self.network_load
                        assert (tm[src][dst] >= 0.0)
                        # print("current volume ", tm[src][dst])
                    else:
                        mu = 0.001 * outgoing
                        std = outgoing / 5.0
                        min_ = mu - (3 * std)
                        max_ = mu + (3 * std)
                        # while True:
                        #     rnd = np.random.normal(mu, std)
                        #     if min_ < rnd < max_:
                        #         break
                        while True:
                            rnd = np.random.normal(mu, std)
                            while rnd < 0.0:
                                rnd = np.random.normal(mu, std)
                            break

                        # tm[src][dst] = ((rnd - min_) / (max_ - min_)) * outgoing * self.network_load
                        tm[src][dst] = rnd * self.network_load
                        assert (tm[src][dst] >= 0.0)

                    # print(src, dst, tm[src][dst])
            temp_tm = copy.deepcopy(tm)
            # print("temp_tm: ", temp_tm)
            self.matrices_sequence.append(temp_tm)

    def generateGravityTM(self, nu_tm=None):
        if nu_tm is None:
            nu_tm = Nu_of_TMs_Per_TOPO

        tm = {}
        for s in self.topo.nodes():
            tm[s] = {}
            for d in self.topo.nodes():
                tm[s][d] = 0.0

        Cap = {}
        totalcap = 0
        for src in self.topo.nodes():
            cap = 0
            for neighbour in self.topo[src]:
                cap += self.topo[src][neighbour]['capacity']
            Cap[src] = cap
            totalcap += cap

        weight = {}
        for s in self.topo.nodes():
            weight[s] = {}
            for d in self.topo.nodes():
                weight[s][d] = 0.0

        for src in weight:
            outgoing = Cap[src]
            cap = totalcap - Cap[src]
            for dst in weight:
                if dst != src:
                    weight[src][dst] = (self.network_load * outgoing * Cap[dst] / cap)  # * random.gauss(100, 20)
                    # tm[src][dst] = (self.network_load * outgoing * Cap[dst] / cap) / 2.5
                    # tm[src][dst] = tm[src][dst] * random.uniform(0.20, 1.95)
                    # print("tm: ", tm)
        # temp_tm = copy.deepcopy(tm)
        # # print(temp_tm)
        # print("tm is: ", tm)
        for _ in range(nu_tm):
            for src in tm:
                for dst in tm:
                    if dst != src:
                        # tm[src][dst] = random.gauss(weight[src][dst], weight[src][dst] / 10)  # std = tm[src][dst]/10

                        a, m = 4.0, weight[src][dst]  # shape and mode for pareto distribution
                        tm[src][dst] = ((np.random.pareto(a, 1) + 1) * m)[0]  # std = tm[src][dst]/5

            temp_tm = copy.deepcopy(tm)
            # print("temp tm is: ", temp_tm)
            self.matrices_sequence.append(temp_tm)

    def generateGravityTM_backup(self, nu_tm=None):
        if nu_tm is None:
            nu_tm = Nu_of_TMs_Per_TOPO

        tm = {}
        for s in self.topo.nodes():
            tm[s] = {}
            for d in self.topo.nodes():
                tm[s][d] = 0.0

        Cap = {}
        totalcap = 0
        for src in self.topo.nodes():
            cap = 0
            for neighbour in self.topo[src]:
                cap += self.topo[src][neighbour]['capacity']
            Cap[src] = cap
            totalcap += cap

        for _ in range(nu_tm):
            for src in tm:
                outgoing = Cap[src]
                cap = totalcap - Cap[src]
                for dst in tm:
                    if dst != src:
                        tm[src][dst] = (self.network_load * outgoing * Cap[dst] / cap) * random.gauss(100, 20)
                        # tm[src][dst] = (self.network_load * outgoing * Cap[dst] / cap) / 2.5
                        # tm[src][dst] = tm[src][dst] * random.uniform(0.20, 1.95)
                        # print("tm: ", tm)
            temp_tm = copy.deepcopy(tm)
            # print(temp_tm)
            self.matrices_sequence.append(temp_tm)


# todo: UNUSED FUNCTION! WILL BE REVISITED AFTER REACHING THE VISUALIZAITON PHASE.
def generate_demands(g, **kwargs):
    if kwargs['type'] == 'gravity':
        # FRAC_UTIL = 0.15  # Avg utilization of a link to generate TM#
        Cap = {}
        totalcap = 0
        # topo = g.edges(data=True)
        # print("topo: ", type(topo))

        '''for src in topo:
            cap = 0
            for dst in topo[src]:
                #cap += topo[src][dst]['cap']
                cap += g[src][dst]['capacity']
            Cap[src] = cap
            totalcap += cap'''

        for link in g.edges():
            Cap[link[0]] = 0
        for link in g.edges():
            Cap[link[0]] += g[link[0]][link[1]]['capacity']
            totalcap += g[link[0]][link[1]]['capacity']

        # fill tm first with all 0's
        tm = {}
        for src in g.nodes():
            tm[src] = {}
            for dst in g.nodes():
                if src == dst:
                    continue
                tm[src][dst] = 0

        for src in tm:
            outgoing = Cap[src]
            cap = totalcap - Cap[src]
            for dst in tm:
                if dst != src:
                    tm[src][dst] = FRAC_UTIL * outgoing * Cap[dst] / cap

        # print("GRAVITY TRAFFIC MATRIX:")
        return (tm)

    if kwargs['type'] == 'random':
        demandVolumes = {}
        # Building random dictionary of demands:
        # print(g.nodes)
        for s in g.nodes():
            demandVolumes[s] = {}
            for d in g.nodes():
                if s == d:
                    continue
                '''rand01 = np.random.randint(2)
                print(rand01)
                if rand01 == 1:
                    demandVolumes[(s, d)] = 0
                    continue #making some demands as 0'''
                demandVolumes[s][d] = np.random.randint(low=0, high=5)
                # demandVolumes[s][d] = 0
        # demandVolumes[0][2] = 5
        # demandVolumes[2][0] = 3

        # demandVolumes[(s, d)] = 0
        return demandVolumes

    if kwargs['type'] == 'fnss':
        demandVolumes = static_traffic_matrix(g, mean=0.5, stddev=0.09, max_u=kwargs['max_u'],
                                              seed=kwargs['seed'])
        return demandVolumes.flow
    # print("here they are: ", demandVolumes)
    if kwargs['type'] == 'modified_fnss':
        demandVolumes = trafficmatrixGenerator.modified_static_traffic_matrix(g, mean=0.5,
                                                                              stddev=0.09,
                                                                              max_u=kwargs['max_u'],
                                                                              load_percentage=kwargs[
                                                                                  'load_percentage'],
                                                                              seed=kwargs['seed'])
        '''#pair that do not exist, add it, and assign it to 0
        for s in g.nodes():
            for d in g.nodes():
                if s == d:
                    continue
                if s not in demandVolumes.flow.keys() or d not in demandVolumes[s].flow.keys():
                #if demandVolumes.flow[s][d] not in demandVolumes.flow:
                    demandVolumes.flow[s][d] = 0'''

        return demandVolumes.flow
