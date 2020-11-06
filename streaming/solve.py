import networkx as nx
from calculate_throughput import Throughput_metric
from calculate_max_congestion import Max_congestion_metric
from calculate_latency import Latency_metric


class Solve:

    def __init__(self, t, routing_scheme, links_to_route, route_to_ratio_dict, tm, num_of_tms, sum_total_tm, shared_dict,
                 congestions_over_all_tm_dict, latency_and_demand_fraction_dict, algo_name, topo):


        # print(shared_dict)
        # routing_scheme = traffic_generator.routing_scheme
        # self.traffic_generator = traffic_generator
        # self.routing_scheme = routing_scheme
        # print("here : ", traffic_generator.routingscheme.algo_name)
        # print("routing_scheme = ", routing_scheme)
        # print("tm = ", tm)
        # print("topo = ", nx.to_dict_of_dicts(traffic_generator.topo))
        #
        Throughput_metric(t, routing_scheme, tm, nx.to_dict_of_dicts(topo), shared_dict, algo_name)
        Max_congestion_metric(t, routing_scheme, links_to_route, route_to_ratio_dict, tm,
                              nx.to_dict_of_dicts(topo),
                              shared_dict, congestions_over_all_tm_dict, algo_name)
        Latency_metric(t, routing_scheme, links_to_route, route_to_ratio_dict, tm, num_of_tms, sum_total_tm, nx.to_dict_of_dicts(topo),
                       shared_dict, latency_and_demand_fraction_dict,
                       algo_name)

        # f = open("dict.txt", "w")
        # f.write("routing_scheme = ")
        # f.write(str(routing_scheme))
        # f.write("\n")
        # f.write("tm = ")
        # f.write(str(traffic_generator.tm))
        # f.write("\ntopo = ")
        # f.write(str(nx.to_dict_of_dicts(traffic_generator.topo)))
        # f.close()
