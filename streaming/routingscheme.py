from utilities import chunks
import time
from solve import Solve
from algorithms.ecmp import Ecmp
from algorithms.ksp import Ksp
from algorithms.raeke import Raeke
from algorithms.mcf.mcf import Mcf
from itertools import combinations
import copy
import re
from config import YATES_SCHEME_FILE_PATH, FIXED_WEIGHT_VALUE
from config import YATES_SCHEME
from programsettings import CPU_COUNT
from multiprocessing import Process, Manager
from itertools import product
import fnss as fnss


class RoutingScheme:
    """
        two steps:
        1- Select set of routes for each SD pair.
        2- Calculate the split ratio (adaptation rate).
    """

    def __init__(self, topo, algo, num_cand_path, raeke_routing_scheme, matrices_sequence,
                 OutputDirName, topology, shared_dict, congestions_over_all_tm_dict, latency_and_demand_fraction_dict):
        self.algo_name = algo
        self.topo = topo
        # print("in routing scheme and algo is: ", algo)
        # print("topo is: ", self.topo.edges(data=True))

        self.shared_dict = shared_dict
        self.matrices_sequence = matrices_sequence
        self.num_of_tms = len(matrices_sequence)

        self.sum_total_tm = 0
        for tm in matrices_sequence:
            self.sum_total_tm += sum([tm[s][d] for s in tm for d in tm[s]])

        # Building the scheme, otherwise, read scheme from file.
        self.te_route_selection_algo = None
        self.rate_adaptation = None
        self.all_pairs = list(combinations(self.topo.nodes(), 2))  # ingress, egress pairs

        self.initialize_routing_scheme()
        if '+' in self.algo_name:
            alist = self.algo_name.split('+')
            self.te_route_selection_algo = alist[0]
            if 'AD' in alist[1]:
                self.rate_adaptation = 'AD'
            if 'LB' in alist[1]:
                self.rate_adaptation = 'LB'

        if self.algo_name == 'YATES_SCHEME':
            self.read_scheme_from_file()

        if 'RAEKE' in self.algo_name:
            # self.routing_scheme = Raeke.calculate_raeke_scheme(self.topo, num_cand_path)
            self.routing_scheme = raeke_routing_scheme
            # cap out the scheme according to path budget

            self.cap_routing_scheme(num_cand_path)
            # print("routing scheme is : \n")
            # print(self.routing_scheme)

            # print("raeke routing scheme: ", self.routing_scheme)
            # self.selected_routes #TODO: I may need to fill selecte_routes and rate_adaptation later

        if self.te_route_selection_algo == 'KSP':
            self.selected_routes = Ksp.route_selection(self.topo, self.routing_scheme, num_cand_path)
            # print("routing scheme before rate adaptation", self.routing_scheme)
        if self.te_route_selection_algo == 'ALL':
            self.selected_routes = Ksp.route_selection(self.topo, self.routing_scheme, 25)

        if self.te_route_selection_algo == 'ECMP':
            # print(self.algo_name, " before: ", self.routing_scheme)
            Ecmp.route_selection(self.topo, self.routing_scheme, num_cand_path)
            # print(self.algo_name, " after: ", self.routing_scheme)

        if 'RAEKE' not in self.algo_name and 'YATES_SCHEME' not in self.algo_name:
            self.populate_second_half_routing_scheme()

        ########## rate adaptation part ###########
        if self.rate_adaptation == 'EVENLY':
            self.split_evenly()
            # print("scheme is: ", self.routing_scheme)
            # print("routing scheme after rate adaptation", self.routing_scheme)
        if self.rate_adaptation == 'EXPONENTIALLY_DECREASING':
            self.split_exponentially()

        if self.rate_adaptation == 'EXP-2':
            self.split_exponentially2(2)

        if self.rate_adaptation == 'EXP-3':
            self.split_exponentially2(3)

        # reading scheme from file:

        # print("algo name:", self.algo_name, " Scheme is : ", self.routing_scheme)

        links_to_route = self.create_links_to_route_structure()

        # passing shared dictionary for congestions:
        # import pickle
        # with open(self.algo_name + '_' + 'scheme', 'wb') as handle:
        #     pickle.dump(self.routing_scheme, handle)
        if self.rate_adaptation == 'LB' or self.rate_adaptation == 'AD':
            manager = Manager()
            mcf_schemes_dict = manager.dict()

            monitoring_process = Process(target=self.monitor_dict,
                                         args=(mcf_schemes_dict, links_to_route, congestions_over_all_tm_dict,
                                               latency_and_demand_fraction_dict,))
            monitoring_process.start()
            procs = []
            for t, matrix in enumerate(self.matrices_sequence):
                proc = Process(target=Mcf, args=(
                    self.routing_scheme, self.topo, matrix, self.algo_name, self.rate_adaptation, t, mcf_schemes_dict))
                procs.append(proc)
            for chunk in chunks(procs, 3):
                # print(len(i))
                for i in chunk:
                    i.start()
                for i in chunk:
                    i.join()
            monitoring_process.join()
        else:
            # t = 0
            for t, matrix in enumerate(self.matrices_sequence):
                Solve(t, self.routing_scheme, matrix, self.shared_dict, congestions_over_all_tm_dict,
                      latency_and_demand_fraction_dict, self.algo_name,
                      self.topo)
                # t += 1

        # checking if the routing scheme is valid:
        # for pair in self.routing_scheme:
        #     summ = 0
        #     for variableName in self.routing_scheme[pair]:
        #         summ += self.routing_scheme[pair][variableName]['ratio']
        #     print(summ)

    def create_route_to_ratio_dict(self, routing_scheme):
        route_to_ratio_dict = {}
        for pair in routing_scheme:
            # print(pair)
            # print(self.routing_scheme[pair])
            for route_name in routing_scheme[pair]:
                route_to_ratio_dict[route_name] = routing_scheme[pair][route_name]['ratio']
        # print(route_to_ratio_dict)

        return route_to_ratio_dict

    def create_links_to_route_structure(self):
        linksToRoutes = {}  # Mapping a link to all routes passing that link
        for link in self.topo.edges():
            linksToRoutes[link] = []
        for pair in self.routing_scheme:
            # print("pair is is : ", pair)
            for variableName in self.routing_scheme[pair]:
                # print("variableName is is : ", variableName)

                path = self.routing_scheme[pair][variableName]['path']
                # print("path is is : ", path)
                for index in range(len(path) - 1):
                    linksToRoutes[(path[index], path[index + 1])].append(variableName)
        return linksToRoutes

    def cap_routing_scheme(self, num_path):
        '''
        capping number of paths
        according to the
        provided path budget
        '''
        new_scheme = {}
        for pair in self.routing_scheme:
            temp = copy.deepcopy(
                dict(sorted(self.routing_scheme[pair].items(), key=lambda x: x[1]['ratio'], reverse=True)))
            if len(temp) < num_path:
                new_scheme[pair] = temp
            else:
                pairs = list(temp.keys())[:num_path]
                new_scheme[pair] = {key: temp[key] for key in pairs}

        self.routing_scheme = copy.deepcopy(new_scheme)

    def monitor_dict(self, mcf_schemes_dict, links_to_route, congestions_over_all_tm_dict,
                     latency_and_demand_fraction_dict):
        # print("dict type: ", type(dict))
        # print("self.matrices_sequence", type(self.matrices_sequence))
        for t in range(len(self.matrices_sequence)):
            # print("type is: ", type(mcf_schemes_dict))
            while True:
                if t not in mcf_schemes_dict:
                    continue
                else:
                    break
            routing_scheme = mcf_schemes_dict[t]
            # print(routing_scheme)
            # print("mcf_obj: ", mcf_obj)
            route_to_ratio_dict = self.create_route_to_ratio_dict(routing_scheme)
            Solve(t, routing_scheme, links_to_route, route_to_ratio_dict,
                  self.matrices_sequence[t], self.num_of_tms, self.sum_total_tm, self.shared_dict, congestions_over_all_tm_dict,
                  latency_and_demand_fraction_dict,
                  self.algo_name, self.topo)

    def read_scheme_from_file(self):
        new_scheme = {}
        f = open(YATES_SCHEME_FILE_PATH, 'r')
        for line in f:
            if '->' in line:
                path_n = 0
                temp = re.findall(r'\d+', line)
                # print(temp)
                res = list(map(int, temp))
                s = res[0] - 1
                d = res[1] - 1
                pair = (s, d)
                # print(res)
                # print(line, line.replace(" ", "").replace(":\n", "").replace("->", ""))  # line.split('->'))
                new_scheme[(s, d)] = {}
                # new_line = f.readline()
                # assert ('->' not in new_line)
            if '@' in line:
                line_list = line.strip().split('@')
                unprocessed_path = line_list[0]
                # print("line is:", line, " right side is: ", line_list[1])
                ratio = float(line_list[1])
                numbers = re.findall(r'\d+', unprocessed_path)

                path = []
                [path.append(x) for x in numbers if x not in path]
                # print("path is: ", path)
                path = list(map((lambda x: int(x) - 1), path))
                variableName = 'x' + "_Index_" + str(path_n) + '_s' + str(s) + '_d' + str(d)
                new_scheme[pair][variableName] = {}
                new_scheme[pair][variableName]['path'] = path
                new_scheme[pair][variableName]['ratio'] = ratio
                path_n += 1

        self.routing_scheme = new_scheme

    def populate_second_half_routing_scheme(self):
        ''' Because links capacities are the same in both directions (symmetric),
        we need this function to populate the second half of the routing scheme.
         This increases the calculation speed of the routing scheme'''
        # print(self.routing_scheme)
        routing_scheme_copy = copy.deepcopy(self.routing_scheme)
        for pair in routing_scheme_copy.keys():
            self.routing_scheme[pair[1], pair[0]] = {}
            for varName in self.routing_scheme[pair]:
                varNameList = varName.split('_')
                newVarName = str(
                    varNameList[0] + '_' + varNameList[1] + '_' + varNameList[2] + '_s' + varNameList[4][1:] + '_d' +
                    varNameList[
                        3][1:])
                # print(varName, varNameList, newVarName)
                reversed_path = copy.deepcopy(self.routing_scheme[pair][varName]['path'])
                reversed_path = reversed_path[::-1]
                self.routing_scheme[pair[1], pair[0]][newVarName] = {}

                self.routing_scheme[pair[1], pair[0]][newVarName]['path'] = reversed_path
                self.routing_scheme[pair[1], pair[0]][newVarName]['ratio'] = 0.0
        # print(self.routing_scheme)

    def initialize_routing_scheme(self):
        self.routing_scheme = {}
        for pair in self.all_pairs:
            self.routing_scheme[pair] = {}  # will be filled later, route:rate for all selected routes for this pair.

    def split_exponentially(self):
        for pair in self.routing_scheme.keys():
            summ = sum([1 / (n + 1) for n in range(len(self.routing_scheme[pair]))])
            # print("summmmmmmmmmmmmm: ", range(len(self.routing_scheme[pair])), len(self.routing_scheme[pair]))
            for n, varName in enumerate(self.routing_scheme[pair]):
                # self.routing_scheme[pair][varName]['ratio'] = 1 / len(self.routing_scheme[pair])
                ratio = (1 / (n + 1)) / summ
                self.routing_scheme[pair][varName]['ratio'] = ratio
        # print(self.routing_scheme)

    def split_exponentially2(self, exp):
        for pair in self.routing_scheme.keys():
            # summ = [n for n in range(len(self.routing_scheme[pair]))]
            ratios_list = [n for n in range(len(self.routing_scheme[pair]))]
            ratios_list = [(n + 1) ** exp for n in range(len(ratios_list))]
            ratios_list = [n / sum(ratios_list) for n in ratios_list]
            ratios_list.reverse()
            # print("summmmmmmmmmmmmm: ", range(len(self.routing_scheme[pair])), len(self.routing_scheme[pair]))
            for n, varName in enumerate(self.routing_scheme[pair]):
                # self.routing_scheme[pair][varName]['ratio'] = 1 / len(self.routing_scheme[pair])
                ratio = ratios_list[n]
                self.routing_scheme[pair][varName]['ratio'] = ratio
        # print(self.routing_scheme)

    def split_evenly(self):
        for pair in self.routing_scheme.keys():
            for varName in self.routing_scheme[pair]:
                self.routing_scheme[pair][varName]['ratio'] = 1 / len(self.routing_scheme[pair])
        # print(self.routing_scheme)
