from Visual import *
from Sensor import *
from multiprocessing import Manager
# from config import TE_RATE_ADAPTATION_ALGORITHM, TE_ROUTE_SELECTION_ALGORITHM
from utilities import return_algorithms_names
from config import RECORDED_INFORMATION


def initializeGlobalDictionary():
    # all_algo = [str(a) + '+' + str(b) for a in TE_ROUTE_SELECTION_ALGORITHM for b in TE_RATE_ADAPTATION_ALGORITHM]

    all_algo = return_algorithms_names()

    # print(all_algo)
    manager = Manager()
    shared_dict = manager.dict()
    for info in RECORDED_INFORMATION:
        inside_dict1 = manager.dict()
        shared_dict[info] = inside_dict1
        for algo in all_algo:
            inside_dict2 = manager.dict()
            shared_dict[info][algo] = inside_dict2
    return shared_dict


def initializeLatencyDictionary():
    all_algo = return_algorithms_names()
    manager = Manager()
    latency_and_demand_fraction_dict = manager.dict()
    for algo in all_algo:
        inside_dict = manager.dict()
        latency_and_demand_fraction_dict[algo] = inside_dict
    return latency_and_demand_fraction_dict


def initializeCongestionDictionary():
    all_algo = return_algorithms_names()
    manager = Manager()
    congestions_over_all_tm_dict = manager.dict()
    for algo in all_algo:
        inside_dict = manager.dict()
        congestions_over_all_tm_dict[algo] = inside_dict
    return congestions_over_all_tm_dict


def threads(callbackFunc, running):
    # Set multiple threads

    congestions_over_all_tm_dict = initializeCongestionDictionary()
    latency_and_demand_fraction_dict = initializeLatencyDictionary()
    shared_dict = initializeGlobalDictionary()
    sensor = Sensor(callbackFunc=callbackFunc, running=running,
                    shared_dict=shared_dict, congestions_over_all_tm_dict=congestions_over_all_tm_dict,
                    latency_and_demand_fraction_dict=latency_and_demand_fraction_dict)  # Instantiate the Sensor thread
    # Start threads 
    sensor.start()  # Run the thread to start collecting data


def main():
    # Set global flag
    event = threading.Event()  # Create an event to communicate between threads
    event.set()  # Set the event to True

    webVisual = Visual(callbackFunc=threads, running=event)  # Instantiate a Bokeh web document
    threads(callbackFunc=webVisual, running=event)  # Call Sensor thread


# Run command:
# bokeh serve --show streaming
# if __name__ == '__main__':
main()

# print("process id in main() : ", os.getpid())
