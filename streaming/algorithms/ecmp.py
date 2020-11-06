from shortest_path_strategy import Shortest_Path


class Ecmp:
    @staticmethod
    def route_selection(topo, routing_scheme, num_cand_path):
        return Shortest_Path(topo, routing_scheme, 'ecmp', num_cand_path)
