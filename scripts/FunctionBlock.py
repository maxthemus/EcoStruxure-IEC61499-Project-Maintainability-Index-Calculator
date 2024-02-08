import math
import re

class FB:
    #Will Create the function block class from the given XML_Dict given .fbt file
    def __init__(self, name, type, xml_dict):
        self.name = name # name of FB
        self.type = type # can be BFB or CFB
        self.children = [] #Array holding if CFB will have children
        self.valid = False #Valid if information has been filed by parsing XML

        self.xml_dict = xml_dict #dict 

        #Info Fields
        self.MI = 0
        self.LOC = 0
        self.CC = 0
        self.HV = 0
    
    #Getters
    def get_type(self):
        return self.type
    
    def get_name(self):
        return self.name

    def get_children(self):
        return self.children

    def get_xml_dict(self):
        return self.xml_dict

    def get_MI(self):
        return self.MI

    #Setters 
    def set_type(self, type):
        self.type = type
        return

    def set_xml(self, xml):
        self.xml_dict = xml

    #Methods
    def update_HV(self):
        #N = (N1 + n2) sum of total num of operands and operators
        #n = (n1 + n2) sum of unique operands and operators
        #1 = operators, 2 = operands

        unique_state_algo_operators= []
        unique_algos = []
        unique_event_outputs = []

        #getting total operators
        #N1
        total_operators = 0
        total_operators += self.get_ECC_edge_count(self.xml_dict)
        
        for i in self.xml_dict['FBType']['BasicFB']['ECC']['ECState']:
            if 'ECAction' in i.keys():
                if type(i['ECAction']) is dict:
                    total_operators += 1
                    #compare single algo and output to dict
                    #checking if in array
                    if not any(d == i['ECAction'] for d in unique_state_algo_operators):
                        unique_state_algo_operators.append(i['ECAction'])
                else:
                    total_operators += len(i['ECAction'])
                    for j in i['ECAction']:
                        if not any(d == j for d in unique_state_algo_operators):
                            unique_state_algo_operators.append(j)

        #Getting unique operators
        #n2
        unique_operators = 0
        unique_operators += len(self.get_ECC_unique_edges(self.xml_dict))
        unique_operators += len(unique_state_algo_operators)

        #Getting total operands
        #N1
        total_operands = 0
        total_operands += self.get_ECC_edge_count(self.xml_dict)
        
        for i in self.xml_dict['FBType']['BasicFB']['ECC']['ECState']:
            if 'ECAction' in i.keys():
                if type(i['ECAction']) is dict:
                    total_operands += 1
                    if '@Algorithm' in i['ECAction'].keys():
                        if i['ECAction']['@Algorithm'] not in unique_algos:
                            unique_algos.append(i['ECAction']['@Algorithm'])
                    if '@Output' in i['ECAction'].keys():
                        if i['ECAction']['@Output'] not in unique_event_outputs:
                            unique_event_outputs.append(i['ECAction']['@Output'])
                else:
                    total_operands += len(i['ECAction'])
                    for j in i['ECAction']:
                        if '@Algorithm' in j.keys():
                            if j['@Algorithm'] not in unique_algos:
                                unique_algos.append(j['@Algorithm'])
                        if '@Output' in j.keys():
                            if j['@Output'] not in unique_event_outputs:
                                unique_event_outputs.append(j['@Output'])


        #Getting unique operands
        #N2
        unique_operands= 0
        unique_operands += len(self.get_ECC_unique_edges(self.xml_dict))
        unique_operands += len(unique_algos)
        unique_operands += len(unique_event_outputs)

        #Calculating the HV
        self.HV = self.calc_HV(unique_operands, total_operands, unique_operators, total_operators)


    def update_LOC(self):
        algo_dict = self.get_algorithms_LOC_BFB(self.xml_dict)
        LOC = 0
        #Algo LOC
        LOC += self.get_total_LOC_Algo(algo_dict)
        #ECC LOC
        ECC_Nodes = self.get_ECC_node_count(self.xml_dict) 
        ECC_Edges = self.get_ECC_edge_count(self.xml_dict)
        LOC += (ECC_Nodes + ECC_Edges)
        self.LOC = LOC

    def update_CC(self):
        #Getting CC of algorithmms
        algorithms = self.xml_dict['FBType']['BasicFB']['Algorithm']

        CC = 0
        for algo in algorithms:
            CC += self.calc_CC_algorithm(algo['ST']['@Text'])

        #Getting CC of ECC
        ECC_Nodes = self.get_ECC_node_count(self.xml_dict) 
        ECC_Edges = self.get_ECC_edge_count(self.xml_dict)
        CC += (ECC_Edges - ECC_Nodes + 2)

        self.CC = CC


    def update_MI(self):
        if len(self.children) == 0:
            #If BFB
            self.update_CC()
            self.update_LOC()
            self.update_HV()

            self.MI = self.calc_MI(self.HV, self.LOC, self.CC)
        else:
            #ELSE CFB
            sum = 0
            count = 0
            for child in self.children:
                sum = sum + child.get_MI()
                count = count + 1

            self.MI = sum / count


    def calc_MI(self, HV, LOC, CC):
        if HV == 0 or LOC == 0 or CC == 0:
            return 0
        else:
            return (171 - (5.2 * math.log(HV)) - (0.23 * math.log(CC)) - (16.2 * math.log(LOC)))

    def addChild(self, childFB):
        self.children.append(childFB)

    def __str__(self):
        return self.name + " : " + self.type + " : " + str(len(self.children))

    #private methods
    def calc_CC_algorithm(self, algorithm_text):
        control_flow_statements = re.findall(r'(IF.*?END_IF;|ELSIF.*?;|ELSE.*?;|END_IF;|[^;]+;)', algorithm_text)
        Nodes = len(control_flow_statements)
        Edges = Nodes - 1
        P = 2
        cyclomatic_complexity = Edges - Nodes + 2
        return cyclomatic_complexity 


    def get_algorithms_LOC_BFB(self, xml_dict):
        algorithm_dict = dict()
        algorithms = xml_dict['FBType']['BasicFB']['Algorithm']
        for i in algorithms:
            count = 0
            if '@Comment' in i.keys():
                count += len(i['@Comment'].split("\n"))
            count += len(i['ST']['@Text'].split("\n"))
            #adding count to dictionary
            algorithm_dict[i['@Name']] = count

        return algorithm_dict

    def get_total_LOC_Algo(self, LOC_dict):
        count = 0
        for i in LOC_dict.keys():
            count += LOC_dict[i]
        return count

    def calc_HV(self, unique_operands, total_operands, unique_operators, total_operators):
        return (unique_operands + unique_operators) * math.log2(total_operands + total_operators)


    def get_ECC_node_count(self, xml_dict):
        return len(xml_dict['FBType']['BasicFB']['ECC']['ECState'])

    def get_ECC_edge_count(self, xml_dict):
        return len(xml_dict['FBType']['BasicFB']['ECC']['ECTransition'])

    def get_ECC_unique_edges(self, xml_dict):
        unique = []

        edges = xml_dict['FBType']['BasicFB']['ECC']['ECTransition']
        for i in edges:
            if i['@Condition'] not in unique:
                unique.append(i['@Condition'])

        return unique

    def get_ECC__basic_transition_count(self, xml_dict):
        count = 0
        edges = xml_dict['FBType']['BasicFB']['ECC']['ECTransition']

        for i in edges:
            if i['@Condition'] == '1':
                count += 1
        return count





