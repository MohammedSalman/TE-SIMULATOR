import copy
import pickle

host_list = []

with open('AttMpls.hosts', 'r') as f_in:
    lines = (line.rstrip() for line in f_in)
    lines = (line for line in lines if line)

    for line in lines:
        host_list.append(line[1:])

host_list = [int(a) for a in host_list]
print(host_list)

traffic_matrices = []
tm = {}
for s in host_list:
    tm[s] = {}
    for d in host_list:
        tm[s][d] = 0.0
line_num = 0
with open('AttMpls.txt', 'r') as fobj:
    for line in fobj:
        numbers = [float(num) for num in line.split()]
        # print(numbers)
        index = 0
        for src in host_list:
            for dst in host_list:
                tm[src][dst] = numbers[index] / 1000000.0
                index += 1
                if src == dst:
                    tm[src][dst] = 0.0
        traffic_matrices.append(copy.deepcopy(tm))

pickle_out = open('att_converted_demands.pickle', "wb")
pickle.dump(traffic_matrices, pickle_out)
pickle_out.close()
