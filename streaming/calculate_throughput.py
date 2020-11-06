import copy
# from visualize import Visualize
import random
import time


# given a TM, a topology, and a routing scheme, find the throughput

# for example:

# routing_scheme = {
#     (0, 3): {'x_Index_0_s0_d1': {'path': [0, 2, 3], 'ratio': 1.0}},
#     (1, 3): {'x_Index_0_s1_d2': {'path': [1, 2, 3], 'ratio': 1.0}},
# }
# tm = {
#     0: {3: 60.0},
#     1: {3: 60.0}
# }
# topo = {
#     0: {2: {'capacity': 60.0, 'weight': 1.0}},
#     1: {2: {'capacity': 30.0, 'weight': 1.0}},
#     2: {3: {'capacity': 90.0, 'weight': 1.0}}
# }
class Throughput_metric:
    def __init__(self, t, routing_scheme, tm, topo, shared_dict, algo_name):
        # self.shared_dict = shared_dict
        # self.routing_scheme = routingscheme.traffic_generator.routingscheme.routing_scheme
        self.routing_scheme = routing_scheme
        self.time = t
        self.tm = tm
        self.topo = topo
        # self.algo_name = routingscheme.traffic_generator.routingscheme.algo_name
        self.algo_name = algo_name
        # print(self.time)
        # shared_dict[self.algo_name][self.time] = None
        # print(shared_dict[self.algo_name][self.time])
        # print("shared dict: ", shared_dict)
        # print(self.algo_name)
        # print("in calulate throughput.. Algo name: ", self.algo_name, " topo is: ", self.topo)
        self.calculate_throughput(shared_dict)
        # if self.algo_name == "ECMP+EVENLY":
        #     print("routing scheme for ecmp+evenly: is :", self.routing_scheme)
        # print("routing scheme is :", self.routing_scheme)

    def calculate_throughput2(self, shared_dict):
        residual_topo = copy.deepcopy(self.topo)
        sd_pairs = [sd_pair for sd_pair in self.routing_scheme]

        received_demand = 0

        for sd_pair in sd_pairs:
            s = sd_pair[0]
            d = sd_pair[1]
            for path_id in self.routing_scheme[sd_pair]:

                path = self.routing_scheme[sd_pair][path_id]['path']
                ratio = self.routing_scheme[sd_pair][path_id]['ratio']
                demand = self.tm[s][d] * ratio
                current_d = demand

                for link in [(path[i], path[i + 1]) for i in range(len(path) - 1)]:
                    a = link[0]
                    b = link[1]
                    if residual_topo[a][b]['capacity'] <= 0:
                        break
                    if residual_topo[a][b]['capacity'] > 0:
                        if current_d < residual_topo[a][b]['capacity']:
                            residual_topo[a][b]['capacity'] -= current_d
                        if current_d >= residual_topo[a][b]['capacity']:
                            current_d = residual_topo[a][b]['capacity']
                            residual_topo[a][b]['capacity'] = 0
                    # if d == b:
                    #     received_demand_per_path = demand - current_d
                received_demand += current_d

        total_demand_sum = sum([self.tm[s][d] for s in self.tm for d in self.tm[s]])
        throughput_value = received_demand / total_demand_sum * 100
        shared_dict['throughput'][self.algo_name][self.time] = throughput_value

    # TODO: Don't delete the code below (backup)
    def calculate_throughput(self, shared_dict):
        residual_topo = copy.deepcopy(self.topo)
        sd_pairs = [sd_pair for sd_pair in self.routing_scheme]

        received_demand = 0

        for sd_pair in sd_pairs:
            s = sd_pair[0]
            d = sd_pair[1]
            for path_id in self.routing_scheme[sd_pair]:

                path = self.routing_scheme[sd_pair][path_id]['path']
                ratio = self.routing_scheme[sd_pair][path_id]['ratio']
                demand_fraction = self.tm[s][d] * ratio

                for link in [(path[i], path[i + 1]) for i in range(len(path) - 1)]:
                    a = link[0]
                    b = link[1]
                    # if this is the first link, calculate the amount of demand that will be transferred on that link.
                    if a == s:
                        if demand_fraction >= residual_topo[a][b]['capacity']:
                            current_flow = residual_topo[a][b]['capacity']
                        else:  # tm[s][d] < residual_topo[a][b]['capacity']:
                            current_flow = demand_fraction

                    if residual_topo[a][b]['capacity'] == 0:  # no need to continue
                        break

                    if residual_topo[a][b]['capacity'] >= current_flow:  # if there is a space to forward
                        residual_topo[a][b]['capacity'] -= current_flow

                        if b == d:  # if this is the last link in this path
                            received_demand += current_flow
                    else:
                        # residual_topo[a][b]['capacity'] < current_flow:  # if there is not enough space to forward
                        current_flow = residual_topo[a][b]['capacity']
                        residual_topo[a][b]['capacity'] = 0

                        if b == d:  # if this is the last link in this path
                            received_demand += current_flow

        total_demand_sum = sum([self.tm[s][d] for s in self.tm for d in self.tm[s]])
        throughput_value = received_demand / total_demand_sum * 100
        shared_dict['throughput'][self.algo_name][self.time] = throughput_value
