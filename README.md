# TE SIMULATOR

TE Simulator is a fast and efficient Traffic Engineering simulator for evaluating many TE systems in parallel.

This TE simulator is to model and test different TE scenarios. 
It was built with efficiency, simplicity, and extendability in mind. 
This simulator was built in Python and provides the ability to test many TE models in parallel while recording many statistics in the background. 
Required to install Gurobi for LP solving. Download from www.https://www.gurobi.com (Free academic license available).
This repository also includes the implementation of the breakthrough Räcke's oblivious routing model.



## Required Dependencies
- Gurobi (www.gurobi.com)
- NetworkX (https://networkx.org)
- Bokeh visualization tool (www.bokeh.org)
- Tornado (https://www.tornadoweb.org/en/stable/index.html)
- Numpy

# How to run experiments

### 1) Change parameters from config.py
- Specify the directory for topology file and traffic matrices file.
- Specify other parameters such as TM model generation, network load, path budget, metrics to be recorded.
- From the dictionary ROUTING_SCHEMES, specify the route selection algorithm (dictionary's keys) and rate adaptation (dictionary's values).
- 
### 2) Run the simulator using Bokeh command:
```sh
$ bokeh serve --show streaming
```
where streaming is the directory that contains the Bokeh application.
### 3) Recorded information (links congestions, throughput, latency) are all stored inside output file as a CSV file.


## Screenshots
### Real time throughput of four TE systems:
![](images/real%20time%20TE%20systems%20throughput.png)
