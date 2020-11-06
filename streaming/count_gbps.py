# fname = input("Enter file name: ")
#
# num_words = 0
#
# with open(fname, 'r') as f:
#     for line in f:
#         words = line.split()
#         num_words += len(words)
# print("Number of words:")
# print(num_words)


import os

directory = 'C:/Users/Mohammed Salman/PycharmProjects/TE_SIMULATOR/streaming/topologies'

for filename in os.listdir(directory):
    # print(filename)

    num_gbps = 0
    num_1gbps = 0

    with open(directory + '/' + filename, 'r') as f:
        for line in f:
            #print(line)
            if 'Gbps' in line:
                num_gbps += 1
            if '1Gbps' in line:
                num_1gbps += 1
    if num_1gbps != num_gbps:
        print(filename)
        print(num_gbps, num_1gbps)
