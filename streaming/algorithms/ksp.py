from shortest_path_strategy import Shortest_Path


class Ksp:
    @staticmethod
    def route_selection(topo, routing_scheme, num_cand_path):
        return Shortest_Path(topo, routing_scheme, 'ksp', num_cand_path)
