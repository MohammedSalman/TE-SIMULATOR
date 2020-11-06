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
class Latency_metric:
    def __init__(self, t, routing_scheme, links_to_route, route_to_ratio_dict, tm, num_of_tms, sum_total_tm, topo,
                 shared_dict,
                 latency_and_demand_fraction_dict, algo_name):
        # self.shared_dict = shared_dict
        # self.routing_scheme = routingscheme.traffic_generator.routingscheme.routing_scheme
        self.routing_scheme = routing_scheme
        self.time = t
        self.tm = tm
        self.topo = topo
        # self.algo_name = routingscheme.traffic_generator.routingscheme.algo_name
        self.algo_name = algo_name
        self.links_to_route = links_to_route
        self.route_to_ratio_dict = route_to_ratio_dict
        self.links_delay_dict = {}
        self.calculate_links_delay()
        self.num_of_tms = num_of_tms
        self.calculate_received_demands_dict()
        self.total_demand_sum = sum([self.tm[s][d] for s in self.tm for d in self.tm[s]])
        self.sum_total_tm = sum_total_tm
        # print(self.time)
        # shared_dict[self.algo_name][self.time] = None
        # print(shared_dict[self.algo_name][self.time])
        # print("shared dict: ", shared_dict)
        # print(self.algo_name)
        # print("in calulate throughput.. Algo name: ", self.algo_name, " topo is: ", self.topo)
        self.calculate_latency(latency_and_demand_fraction_dict)
        # if self.algo_name == "ECMP+EVENLY":
        #     print("routing scheme for ecmp+evenly: is :", self.routing_scheme)
        # print("routing scheme is :", self.routing_scheme)

    # def calculate_links_load(self):
    #     links = [(a, b) for a in self.topo for b in self.topo[a]]
    #     for link in links:
    #         summ = 0
    #         for route_name in self.links_to_route[link]:
    #             s = int(route_name.split('_')[3][1:])
    #             d = int(route_name.split('_')[4][1:])
    #             # print("source is: ", s, " and dest is: ", d, " in route: ", route_name)
    #             summ += self.route_to_ratio_dict[route_name] * self.tm[s][d]
    #
    #         if summ >= self.topo[link[0]][link[1]]['capacity']:
    #             load = self.topo[link[0]][link[1]]['capacity'] - 0.05  # Epsilon
    #         else:
    #             load = summ
    #
    #         self.links_load_dict[link] = load

    def calculate_latency(self, latency_and_demand_fraction_dict):
        # residual_topo = copy.deepcopy(self.topo)
        sd_pairs = [sd_pair for sd_pair in self.routing_scheme]
        # total_demand_sum = sum([self.tm[s][d] for s in self.tm for d in self.tm[s]])
        # they will be stored in a list of tupels
        # each tuple has two items (l, f).
        # l is latency, and f is for fraction.
        temp_list = []
        for sd_pair in sd_pairs:
            # s = sd_pair[0]
            # d = sd_pair[1]
            for path_id in self.routing_scheme[sd_pair]:
                path = self.routing_scheme[sd_pair][path_id]['path']
                # ratio = self.routing_scheme[sd_pair][path_id]['ratio']
                # demand = self.tm[s][d] * ratio
                # if demand == 0.0:
                #     continue
                # current_d = demand
                delay_sum = 0
                for link in [(path[i], path[i + 1]) for i in range(len(path) - 1)]:
                    a = link[0]
                    b = link[1]
                    # if residual_topo[a][b]['capacity'] <= 0:
                    #     delay_sum += (
                    #             self.links_load_dict[link] / (self.topo[a][b]['capacity'] - self.links_load_dict[link]))
                    #     break
                    # if residual_topo[a][b]['capacity'] > 0:
                    #     if current_d < residual_topo[a][b]['capacity']:
                    #         residual_topo[a][b]['capacity'] -= current_d
                    #     if current_d >= residual_topo[a][b]['capacity']:
                    #         current_d = residual_topo[a][b]['capacity']
                    #         residual_topo[a][b]['capacity'] = 0
                    # # if d == b:
                    # #     received_demand_per_path = demand - current_d
                    # delay_sum += (
                    #         self.links_delay_dict[link] / (self.topo[a][b]['capacity'] - self.links_delay_dict[link]))
                    delay_sum += self.links_delay_dict[link]
                latency = delay_sum
                t = (latency, self.received_demand_dict[path_id] / self.total_demand_sum / self.num_of_tms)
                # / self.total_demand_sum)  # / self.num_of_tms)
                temp_list.append(t)
        latency_and_demand_fraction_dict[self.algo_name][self.time] = temp_list

    def calculate_links_delay(self):
        links = [(a, b) for a in self.topo for b in self.topo[a]]
        for link in links:
            summ = 0
            for route_name in self.links_to_route[link]:
                s = int(route_name.split('_')[3][1:])
                d = int(route_name.split('_')[4][1:])
                # print("source is: ", s, " and dest is: ", d, " in route: ", route_name)
                summ += self.route_to_ratio_dict[route_name] * self.tm[s][d]

            if summ >= self.topo[link[0]][link[1]]['capacity']:
                load = self.topo[link[0]][link[1]]['capacity'] - 0.05  # avoiding div by 0
            else:
                load = summ

            self.links_delay_dict[link] = load / (self.topo[link[0]][link[1]]['capacity'] - load)

    def calculate_received_demands_dict(self):
        residual_topo = copy.deepcopy(self.topo)
        sd_pairs = [sd_pair for sd_pair in self.routing_scheme]

        received_demand_dict = {}
        for sd_pair in sd_pairs:
            s = sd_pair[0]
            d = sd_pair[1]
            for path_id in self.routing_scheme[sd_pair]:
                received_demand = 0
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
                received_demand_dict[path_id] = received_demand
        self.received_demand_dict = received_demand_dict

        # total_demand_sum = sum([self.tm[s][d] for s in self.tm for d in self.tm[s]])
        # throughput_value = received_demand / total_demand_sum * 100
        # shared_dict['throughput'][self.algo_name][self.time] = throughput_value

    # TODO: Don't delete the code below (backup)


def calculate_latency_backup(self, latency_and_demand_fraction_dict):
    residual_topo = copy.deepcopy(self.topo)
    sd_pairs = [sd_pair for sd_pair in self.routing_scheme]
    total_demand_sum = sum([self.tm[s][d] for s in self.tm for d in self.tm[s]])
    # they will be stored in a list of tupels
    # each tuple has two items (l, f).
    # l is latency, and f is for fraction.
    temp_list = []
    for sd_pair in sd_pairs:
        s = sd_pair[0]
        d = sd_pair[1]
        for path_id in self.routing_scheme[sd_pair]:
            path = self.routing_scheme[sd_pair][path_id]['path']
            ratio = self.routing_scheme[sd_pair][path_id]['ratio']
            demand = self.tm[s][d] * ratio
            if demand == 0.0:
                continue
            current_d = demand
            delay_sum = 0
            for link in [(path[i], path[i + 1]) for i in range(len(path) - 1)]:
                a = link[0]
                b = link[1]
                if residual_topo[a][b]['capacity'] <= 0:
                    delay_sum += (
                            self.links_load_dict[link] / (self.topo[a][b]['capacity'] - self.links_load_dict[link]))
                    break
                if residual_topo[a][b]['capacity'] > 0:
                    if current_d < residual_topo[a][b]['capacity']:
                        residual_topo[a][b]['capacity'] -= current_d
                    if current_d >= residual_topo[a][b]['capacity']:
                        current_d = residual_topo[a][b]['capacity']
                        residual_topo[a][b]['capacity'] = 0
                # if d == b:
                #     received_demand_per_path = demand - current_d
                delay_sum += (
                        self.links_load_dict[link] / (self.topo[a][b]['capacity'] - self.links_load_dict[link]))
            latency = delay_sum
            t = (latency, current_d / total_demand_sum / self.num_of_tms)
            temp_list.append(t)
    latency_and_demand_fraction_dict[self.algo_name][self.time] = temp_list

    # throughput_value = received_demand / total_demand_sum * 100

    # shared_dict['throughput'][self.algo_name][self.time] = throughput_value
