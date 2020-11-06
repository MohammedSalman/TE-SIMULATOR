# topology settings
# N = [i for i in range(80, 100, 5)]
# L = [i for i in range(125, 300, 5)]
TOPOLOGY_SOURCE = 'file'  # 'file', 'random'
# TOPOLOGY_PATH = 'streaming/data/topologies/dot/3cycle.dot'
TOPOLOGY_PATH = 'streaming/data/topologies/dot/AttMpls.dot'
# TOPOLOGY_PATH = 'streaming/data/topologies/dot/Ans.dot'
# TOPOLOGY_PATH = 'streaming/data/topologies/random/random_topo2020-06-08-H12-M36-S27.pickle'

# TOPOLOGY_PATH = 'streaming/data/topologies/dot/Abilene_1.dot'
# TOPOLOGY_PATH = 'streaming/data/topologies/graphml/Geant2009.graphml'
# TOPOLOGY_PATH = 'streaming/data/topologies/random/random_topo2020-05-31-H08-M27-S16.pickle'

DEMAND_SOURCE = 'file'  # 'file, 'generate'
# DEMAND_PATH = None

###################### RANDOM TOPOLOGY SETTINGS ##########################
N = [25]
L = [40]
TOPOLOGY_SEED = None  # None, or any int # 448672
# Nu_of_TOPOs_Per_N_L = 1
CAPACITY_SET = [30, 35, 40]
CAPACITY_TYPE = 'edge_betweenness'
###################### END OF RANDOM TOPOLOGY SETTINGS ###################


Nu_of_TMs_Per_TOPO = 200  # has no effect if your tm type is 'sin_cyclostationary'
YATES_SCHEME = False
# YATES_SCHEME_FILE_PATH = 'C:/Users/Mohammed
# Salman/PycharmProjects/TE_SIMULATOR/streaming/YATES_SCHEMES/raeke_0_4cycle' YATES_SCHEME_FILE_PATH =
# 'C:/Users/Mohammed Salman/PycharmProjects/TE_SIMULATOR/streaming/YATES_SCHEMES/raeke_0_6hosts'
YATES_SCHEME_FILE_PATH = '//streaming/YATES_SCHEMES/raeke_0_abilene'

# WEIGHT_SETTING = 'inv_cap'  # 'fixed', 'inv_cap'
FIXED_WEIGHT_VALUE = 1  # has no effect if WEIGHT_SETTING is not 'fixed'

TM_TYPE = [
    'gravity']  # 'gravity' , 'nucci' , 'bimodal', 'nucci_stationary', 'sin_cyclostationary', 'random'
# NETWORK_LOAD = [0.35]
NETWORK_LOAD = [0.95]

# sin_cyclostationary settings:
n = 5
period = 25


ROUTING_SCHEMES = {
    # 'ALL': ['LB', 'AD'],
    'RAEKE': ['LB', 'AD'],
    # 'ECMP': ['EVENLY'],
    'KSP': ['LB', 'AD']  # 'LB', 'AD'
}

#
# ROUTING_SCHEMES = {
#     'KSP': ['EVENLY', 'MCF']
# }

# CANDIDATE_PATHS = [i for i in range(1, 8)]
PATH_BUDGET = [4]

RECORDED_INFORMATION = ['throughput', 'max_congestion']

