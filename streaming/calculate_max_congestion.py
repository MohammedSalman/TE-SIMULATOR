import copy
# from visualize import Visualize
import random
import time


# given a TM, a topology, and a routing scheme, find the max congestion

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
class Max_congestion_metric:
    def __init__(self, t, routing_scheme, links_to_route, route_to_ratio_dict, tm, topo, shared_dict,
                 congestions_over_all_tm_dict, algo_name):
        # self.shared_dict = shared_dict
        # self.routing_scheme = routingscheme.traffic_generator.routingscheme.routing_scheme
        self.routing_scheme = routing_scheme
        self.time = t
        self.links_to_route = links_to_route
        self.route_to_ratio_dict = route_to_ratio_dict
        # print(self.route_to_ratio_dict)
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
        self.calculate_max_congestion(shared_dict, congestions_over_all_tm_dict)
        # if self.algo_name == "ECMP+EVENLY":
        #     print("routing scheme for ecmp+evenly: is :", self.routing_scheme)
        # print("routing scheme is :", self.routing_scheme)

    def calculate_max_congestion(self, shared_dict, congestions_over_all_tm_dict):
        congestions = []
        # print(self.topo)
        links = [(a, b) for a in self.topo for b in self.topo[a]]
        for link in links:
            summ = 0
            for route_name in self.links_to_route[link]:
                s = int(route_name.split('_')[3][1:])
                d = int(route_name.split('_')[4][1:])
                # print("source is: ", s, " and dest is: ", d, " in route: ", route_name)
                summ += self.route_to_ratio_dict[route_name] * self.tm[s][d]


            # TODO: re-enable this to measure congestion
            # if summ > self.topo[link[0]][link[1]]['capacity']:
            #     congestion = self.topo[link[0]][link[1]]['capacity']
            # else:
            #     congestion = summ

            # TODO: this is to measure expected load. Enable later.
            congestion = summ


            # now normalize by capacity:
            congestion = congestion / self.topo[link[0]][link[1]]['capacity']
            congestions.append(congestion)
            # print("for link: ", link, " summ is: ", summ, " that link with capacity: ",
            #       self.topo[link[0]][link[1]]['capacity'])
        congestions_over_all_tm_dict[self.algo_name][self.time] = congestions
        shared_dict['max_congestion'][self.algo_name][self.time] = max(congestions)
