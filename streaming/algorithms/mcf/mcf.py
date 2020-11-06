from gurobipy import *
from itertools import islice, combinations
import networkx as nx
from programsettings import MIPGapAbs, GUROBILogToConsole
import copy
import time


class Mcf:
    # TODO: demandsToRoutes can be replaced by the routing_scheme.
    # TODO: divide decision variable by the demand volume before updating the routing_scheme.

    # linksToRoutes = None
    # m = None
    # count = 0
    # def __init__(self, numCandPath, trafficGenerator):
    def __init__(self, routing_scheme, topo, matrix, algo_name, objective, t, mcf_schemes_dict):
        self.time = t
        self.routing_scheme = routing_scheme
        # print(self.routing_scheme)
        self.demandVolumes = matrix
        self.topo = topo
        self.algo_name = algo_name

        self.formulate_paths_flow_var(self.topo, self.routing_scheme)
        if objective == 'LB':
            self.formulate_LB_Multipath()

        if objective == 'AD':
            self.formulate_AD_Multipath()
        self.solve()
        print("In mcf.py, algo_name: ", algo_name)
        self.update_routing_scheme()
        mcf_schemes_dict[self.time] = self.routing_scheme

    def return_updated_routing_scheme(self):
        return self.routing_scheme

    # def __new__(cls):
    #     print("the updated routing scheme is: ", cls.routing_scheme)
    #     return cls.routing_scheme

    # def update_routing_scheme(self):
    #     print("routing scheme before normalizing: ", self.routing_scheme)
    #     for pair in self.routing_scheme:
    #         for variableName in self.routing_scheme[pair]:
    #             if self.decision_variables_dict[variableName] == 0:
    #                 continue  # no need to normalize of the decision variable is already a 0.
    #             self.routing_scheme[pair][variableName]['ratio'] = self.decision_variables_dict[variableName] / \
    #                                                                self.demandVolumes[pair[0]][pair[1]]
    #     print("routing scheme after normalizing: ", self.routing_scheme)

    def update_routing_scheme(self):
        rs = copy.deepcopy(self.routing_scheme)
        for pair in rs:
            for variableName in rs[pair]:
                if self.demandVolumes[pair[0]][pair[1]] == 0.0:
                    continue
                else:
                    self.routing_scheme[pair][variableName]['ratio'] = float(
                        self.decision_variables_dict[variableName] / self.demandVolumes[pair[0]][pair[1]])

    def initialize_model(self):
        # print("ever got here")
        try:
            self.m = Model(name="model")
        except:
            print("Gurobi license error")
            exit(0)
        self.obj_val = 0
        # This will disable console output
        self.m.params.LogToConsole = GUROBILogToConsole
        self.m.params.MIPGapAbs = MIPGapAbs
        # self.demandVolumes = trafficGenerator.tm
        self.feasible = True

    def formulate_paths_flow_var(self, topo, routing_scheme):
        self.initialize_model()
        self.pathsVariables = {}  # These are the decision variables
        self.demandsToRoutes = {}

        self.linksToRoutes = {}  # Mapping a link to all routes passing that link
        for link in topo.edges():
            self.linksToRoutes[link] = []
        for pair in routing_scheme:
            # print("pair is is : ", pair)
            self.demandsToRoutes[pair] = []
            self.demandsToRoutes[pair] = []
            for variableName in routing_scheme[pair]:
                # print("variableName is is : ", variableName)
                self.pathsVariables[variableName] = self.m.addVar(lb=0.0, vtype=GRB.CONTINUOUS, name=variableName)
                path = routing_scheme[pair][variableName]['path']
                # print("path is is : ", path)
                for index in range(len(path) - 1):
                    self.linksToRoutes[(path[index], path[index + 1])].append(variableName)
                self.demandsToRoutes[pair].append(variableName)
                self.m.addConstr(self.pathsVariables[variableName] >= 0.0)
        self.m.update()

    def solve(self):

        # self.m.write("Mymodel" + str(Mcf.count) + ".lp")  # TODO: this should have a unique name to the object, overwritten otherwise.
        # Mcf.count+=1
        self.m.write("Mymodel.lp")
        # self.m.write("Mymodel.mps")
        self.m.optimize()
        self.decision_variables_dict = {}
        for v in self.m.getVars():
            self.decision_variables_dict[v.varName] = v.x
            # print(v.varName, ": ", v.x)
        # print("algo name: ", self.algo_name, "objective value: ", self.m.getObjective().getValue())
        # try:
        #     ObjValue = float('%.8f' % self.m.getObjective().getValue())
        # except AttributeError:
        #     print("Model infeasible")
        #     self.feasible = False
        #     return

        # self.obj_val = ObjValue

    def formulate_LB_Multipath(self):
        # one more variable for the objective function:
        self.z = self.m.addVar(lb=0.0, vtype=GRB.CONTINUOUS, name="z")
        self.m.setObjective(self.z, GRB.MINIMIZE)
        self.addDemandConstr()
        self.addCapacityConstr()
        self.m.update()

    def addDemandConstr(self):
        for demand in self.demandsToRoutes:
            tmp_list = []
            for variable in self.demandsToRoutes[demand]:
                tmp_list.append(self.pathsVariables[variable])
            self.m.addConstr(sum(tmp_list) == self.demandVolumes[demand[0]][demand[1]])
        self.m.update()

    def addCapacityConstr(self):
        # Adding the constraints for:
        # summation of all traffic for paths using link L divided by L's capacity should not exceed 'z'
        for link in self.linksToRoutes:
            tmp_list = []
            for variable in self.linksToRoutes[link]:
                tmp_list.append(self.pathsVariables[variable])
            self.m.addConstr(sum(tmp_list) <= self.z * self.topo[link[0]][link[1]]['capacity'])
            # self.m.addConstr(sum(tmp_list) <= self.topo[link[0]][link[1]]['capacity'])
            # m.addConstr(sum(tmp_list) <= g[link[0]][link[1]]['capacity'])  # '''REMOVING THIS CONSTR WILL AFFECT EFFICIENCY'''
        self.m.update()

    def formulate_AD_Multipath(self):
        # See the 2018 book, Page 136
        # TODO: try the piece-wise builtin feature in Gurobi.
        '''for link in linksToRoutes:
            for variable in linksToRoutes[link]:
                r = m.addVar(name='c' + str(link[0]) + '_' + str(link[1]))'''
        # r = m.addVars(linksToRoutes.keys())

        r = self.m.addVars(self.linksToRoutes.keys(), name="r")

        # print("r: ", r)
        c = {}
        for link in self.linksToRoutes:
            c[link] = self.topo[link[0]][link[1]]['capacity']
        # print("c: ", c)
        self.m.setObjective(quicksum(r[link] / c[link] for link in self.linksToRoutes), GRB.MINIMIZE)
        self.addDemandConstr()

        y = self.m.addVars(self.linksToRoutes.keys())
        # print("y: ", y)
        for link in self.linksToRoutes:
            tmp_list = tuplelist()
            for variable in self.linksToRoutes[link]:
                tmp_list.append(self.pathsVariables[variable])
            self.m.addConstr((quicksum(tmp_list)) == y[link])

        '''m.addConstrs(
            (quicksum(nutritionValues[f, c] * buy[f] for f in foods)
             == [minNutrition[c], maxNutrition[c]]
             for c in categories), "_")'''
        # print(type(r), type(y))
        # self.m.update()

        for link in self.linksToRoutes:
            self.m.addConstr(r[link] >= 3 / 2 * y[link])
            self.m.addConstr(r[link] >= 9 / 2 * y[link] - c[link])
            self.m.addConstr(r[link] >= 15 * y[link] - 8 * c[link])
            self.m.addConstr(r[link] >= 50 * y[link] - 36 * c[link])
            self.m.addConstr(r[link] >= 200 * y[link] - 171 * c[link])
            self.m.addConstr(r[link] >= 4000 * y[link] - 3781 * c[link])
            self.m.update()
