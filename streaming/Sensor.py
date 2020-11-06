import time
import threading
import random
from functools import partial
from multiprocessing import Process, Manager
from config import N, L, Nu_of_TMs_Per_TOPO, TM_TYPE, n, period, RECORDED_INFORMATION, TOPOLOGY_PATH
import pandas as pd
from itertools import product
from topology import Topology
from utilities import chunks, return_algorithms_names
from programsettings import CPU_COUNT
import csv
import copy
import os
import sys


class Sensor(threading.Thread):
    def __init__(self, callbackFunc, running, shared_dict, congestions_over_all_tm_dict,
                 latency_and_demand_fraction_dict):
        threading.Thread.__init__(self)  # Initialize the threading superclass
        self.val = 0  # Set default sensor data to be zero
        self.running = running  # Store the current state of the Flag
        self.callbackFunc = callbackFunc  # Store the callback function
        self.shared_dict = shared_dict
        self.congestions_over_all_tm_dict = congestions_over_all_tm_dict
        self.latency_and_demand_fraction_dict = latency_and_demand_fraction_dict
        # threading.thread.start_new_thread(self.runSimulation, ( ))
        # threading.Thread.start(self.runSimulation)

        # thread1 = threading.Thread(target=runSimulation, args=())
        # thread1.start()
        # self.runSimulation()
        # self.all_algo = [str(a) + '+' + str(b) for a in TE_ROUTE_SELECTION_ALGORITHM for b in
        #                  TE_RATE_ADAPTATION_ALGORITHM]
        # if YATES_SCHEME:
        #     self.all_algo.append('YATES_SCHEME')
        self.all_algo = return_algorithms_names()
        self.simulationProcess = Process(target=runSimulation,
                                         args=(self.shared_dict, self.congestions_over_all_tm_dict,
                                               self.latency_and_demand_fraction_dict,))
        self.simulationProcess.start()

    def run(self):
        # TODO: re-write this to keep track of more than one (t).
        #  One (t) for each algorithm. Some algorithms are slow.
        #  The stop condition should be something like this:
        #  min_t = min(last_t) # where (last_t) is a list of all last time frame for each algorithm.
        #  if min_t == Nu_of_TMs_Per_TOPO:
        #       break
        t = 0
        while self.running.is_set():  # Continue grabbing data from sensor while Flag is set
            # print(self.shared_dict)
            # time.sleep(0.001)  # Time to sleep in seconds, emulating some sensor process taking time
            throughput_list = []
            try:
                for algo_name in self.all_algo:
                    throughput_list.append(self.shared_dict['throughput'][algo_name][t])
                # print(throughput_list)
            except:
                continue
            # self.val = random.randint(0, 10)  # Generate random integers to emulate data from sensor
            t += 1
            # print(t, Nu_of_TMs_Per_TOPO)

            if TM_TYPE[0] == 'sin_cyclostationary' and t == (n * period):
                break
            elif TM_TYPE[0] != 'sin_cyclostationary' and t == Nu_of_TMs_Per_TOPO:
                break
            self.callbackFunc.doc.add_next_tick_callback(partial(self.callbackFunc.update,
                                                                 throughput_list))  # Call Bokeh webVisual to inform that new data is available
        #
        # sys.exit(1)
        # time.sleep(100)
        self.simulationProcess.join()
        # exit(0)
        print("Done...")  # Print to indicate that the thread has ended
        print("process id: ", os.getpid())
        # sys.exit(1)
        # os.kill(os.getpid(), signal.SIGKILL)
        # os.getpid()
        # exit(0)


def write_csv_to_output(shared_dict):
    # first, write csv for 'throughput'
    topology_file_name = TOPOLOGY_PATH.split('/')[-1]

    for info in RECORDED_INFORMATION:
        OutputDirName = 'output/' + topology_file_name + '/'
        try:
            os.makedirs(OutputDirName)
        except OSError:
            pass
        filename = info + '.csv'
        arbitrary_algo_name = str(list(shared_dict[info].keys())[0])
        throughput_row = []
        # header_written = False
        try:
            with open(OutputDirName + filename, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile, delimiter=',')
                # if not header_written:
                writer.writerow(shared_dict[info].keys())
                #     header_written = True
                for t in shared_dict[info][arbitrary_algo_name].keys():
                    for algo in shared_dict[info].keys():
                        throughput_row.append(shared_dict[info][algo][t])
                    writer.writerow(throughput_row)
                    # print(throughput_row)
                    throughput_row = []
        except PermissionError:
            print("PermissionError: Check if the file is open.")


def write_congestions_to_csv(congestions_over_all_tm_dict):
    topology_file_name = TOPOLOGY_PATH.split('/')[-1]
    OutputDirName = 'output/' + topology_file_name + '/'
    try:
        os.makedirs(OutputDirName)
    except OSError:
        pass
    filename = 'congestions_distribution.csv'
    arbitrary_algo_name = str(list(congestions_over_all_tm_dict.keys())[0])
    congestions_row = []
    congestions_rows = []
    with open(OutputDirName + filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerow(congestions_over_all_tm_dict.keys())  # writing the header
        for i, _ in enumerate(congestions_over_all_tm_dict[arbitrary_algo_name][0]):
            for t in congestions_over_all_tm_dict[arbitrary_algo_name].keys():
                for algo in congestions_over_all_tm_dict.keys():
                    congestions_row.append(congestions_over_all_tm_dict[algo][t][i])
                congestions_rows.append(congestions_row)
                #writer.writerow(congestions_row)
                congestions_row = []
        writer.writerows(congestions_rows)



def write_latency_demand_fraction_to_csv(latency_and_demand_fraction_dict):
    topology_file_name = TOPOLOGY_PATH.split('/')[-1]
    OutputDirName = 'output/' + topology_file_name + '/' + 'latency/'
    try:
        os.makedirs(OutputDirName)
    except OSError:
        pass

    for algo_name in latency_and_demand_fraction_dict.keys():
        filename = algo_name + '.csv'
        row = []
        rows = []
        with open(OutputDirName + filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=',')
            header = []
            header.append('delay')
            header.append('fraction')
            writer.writerow(header)
            # print("algo name ", algo_name, " start time: ", time.time())
            for time_t in latency_and_demand_fraction_dict[algo_name].keys():

                for tup in latency_and_demand_fraction_dict[algo_name][time_t]:
                    row.append(tup[0])
                    row.append(tup[1])
                    rows.append(row)
                    # writer.writerow(row)
                    row = []
            # print("end time: ", time.time())
            writer.writerows(rows)

    # arbitrary_algo_name = str(list(latency_and_demand_fraction_dict.keys())[0])
    # row = []
    # filename = 'delay_distribusion_fraction_of_traffic_delivered.csv'
    # with open(filename, 'w', newline='') as csvfile:
    #     writer = csv.writer(csvfile, delimiter=',')
    #     header = []
    #     for algo_name in latency_and_demand_fraction_dict.keys():
    #         header.append(algo_name + '_' + 'delay')
    #         header.append(algo_name + '_' + 'fraction')
    #     writer.writerow(header)
    #     for t in range(len(latency_and_demand_fraction_dict[arbitrary_algo_name])):
    #         for algo in latency_and_demand_fraction_dict.keys():
    #             row.append(latency_and_demand_fraction_dict[algo][t][0])
    #             row.append(latency_and_demand_fraction_dict[algo][t][1])
    #         writer.writerow(row)
    #         row = []

    # for algo in latency_and_demand_fraction_dict.keys():
    #     alist = latency_and_demand_fraction_dict[algo]
    #     sum_a(algo, alist)


def sum_a(algo, alist):
    pass
    # print(algo, sum([a for (a, b) in alist]))
    # print("sum b", algo, sum([b for (a, b) in alist]))


def runSimulation(shared_dict, congestions_over_all_tm_dict, latency_and_demand_fraction_dict):
    # Saving style of the shared object

    # OutputDirName = time.strftime("%Y-%m-%d-H%H-M%M-S%S") + '_PID-' + str(os.getpid())
    OutputDirName = 'output'
    try:
        os.makedirs(OutputDirName)
    except OSError:
        pass

    tic = time.time()
    procs = []

    # for n, l in product(N, L):

    for n, l in random.sample(list(product(N, L)), len(N) * len(L)):
        proc = Process(target=Topology, args=(
            n, l, OutputDirName, shared_dict, congestions_over_all_tm_dict, latency_and_demand_fraction_dict))
        procs.append(proc)

    for i in chunks(procs, CPU_COUNT):
        for j in i:
            j.start()
        for j in i:
            j.join()

    print("Writing output ...")
    write_csv_to_output(shared_dict)
    write_congestions_to_csv(congestions_over_all_tm_dict)
    write_latency_demand_fraction_to_csv(latency_and_demand_fraction_dict)
    print("Done writing output!")
    print("Program finished after (BEFORE COLLECTING): ", time.time() - tic, " seconds.")
    # self.simulationProcess.join()
