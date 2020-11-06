import subprocess

# ax.set_xlim(0, 1300) 1300 for Geant and 100 for Attmpls
# only change the topology name and the script will do the rest
topology_name = 'AttMpls.dot'
# topology_name = 'Geant2009.graphml'
# topology_name = 'Abilene_1.dot'
# topology_name = 'random_topo2020-06-08-H12-M36-S27.pickle'

full_path = '../output/replace_this/'
full_path = full_path.replace('replace_this', topology_name)

filename_arg1 = "display_CDF_graph.py" + " \'" + full_path + 'congestions_distribution.csv' + "\'"
subprocess.call(filename_arg1, shell=True)

filename_arg1 = "display_CDF_graph_throughput.py" + " \'" + full_path + 'throughput.csv' + "\'"
subprocess.call(filename_arg1, shell=True)

filename_arg1 = "display_CDF_latency_graph.py" + " " + topology_name
subprocess.call(filename_arg1, shell=True)

filename_arg1 = "display_graphs.py" + " " + full_path
subprocess.call(filename_arg1, shell=True)
