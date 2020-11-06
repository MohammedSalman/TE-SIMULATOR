import os
from utilities import return_algorithms_names

algorithms = return_algorithms_names()

CPU_COUNT = len(algorithms)  # os.cpu_count()  # // 4
# PARALLELISM = True
VISUALIZE_TOPOLOGY = False
WAITING_TIME = 100  # How long to wait to return None before finding a graph.
MIPGapAbs = 0.000001  # was 0.02 or 0.1
GUROBILogToConsole = 0  # 0 or 1
PRINT_LOG = 1
PRINT_TM = 0
