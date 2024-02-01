# file calculates hold functions that calculate values for the Maintainability index
import re
import math
import xmltodict
import os
import glob
import FunctionBlock
from collections import deque


#Calculating the Halstead Volume of a function block
def calc_HV(unique_operands, total_operands, unique_operators, total_operators):
    return (unique_operands + unique_operators) * math.log2(total_operands + total_operators)

#Calculating Cyclomatic complexity of function block
def calc_CC(ECC_num_edges, ECC_num_nodes):
    return (ECC_num_edges - ECC_num_nodes) + 2

#Calculating Lines of code for Execution controll chart of FB
def calc_LOC_ECC(states, transitions):
    return states + transitions

def calc_LOC_ALGS(algorithms=[]):
    return sum(algorithms)


#Calcultaing the Lines of code for function block
#LOC_ALG is array of algorithm LOC
def calc_LOC_FB(LOC_ECC, LOC_ALG=[]):
    return LOC_ECC + sum(LOC_ALG)

def calc_MI(HV, LOC, CC):
    return (171 - (5.2 * math.log(HV)) - (0.23 * math.log(CC)) - (16.2 * math.log(LOC)))


#XML parser
def parse_XML_file(file):
    with open(file, 'r') as f:
        xml_data = f.read()
    return xmltodict.parse(xml_data)


#CSV of algorithms FB algorithms
#Will count the new lines in the @Comment and in the @Text
def get_algorithms_LOC_BFB(xml_dict):
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


def get_algorithm_names_BFB(xml_dict):
    return xml_dict['FBType']['BasicFB']['Attribute']['@Value'].split(',')

def get_ECC_node_count(xml_dict):
    return len(xml_dict['FBType']['BasicFB']['ECC']['ECState'])

def get_ECC_edge_count(xml_dict):
    return len(xml_dict['FBType']['BasicFB']['ECC']['ECTransition'])

def get_ECC_unique_edges(xml_dict):
    unique = []

    edges = xml_dict['FBType']['BasicFB']['ECC']['ECTransition']
    for i in edges:
        if i['@Condition'] not in unique:
            unique.append(i['@Condition'])

    return unique

def get_ECC__basic_transition_count(xml_dict):
    count = 0
    edges = xml_dict['FBType']['BasicFB']['ECC']['ECTransition']

    for i in edges:
        if i['@Condition'] == '1':
            count += 1
    return count

def calc_ECC_HV_program_volume(xml_dict):
    #N = (N1 + n2) sum of total num of operands and operators
    #n = (n1 + n2) sum of unique operands and operators
    #1 = operators, 2 = operands

    unique_state_algo_operators= []
    unique_algos = []
    unique_event_outputs = []

    #getting total operators
    #N1
    total_operators = 0
    total_operators += get_ECC_edge_count(xml_dict)
    
    for i in xml_dict['FBType']['BasicFB']['ECC']['ECState']:
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
    unique_operators += len(get_ECC_unique_edges(xml_dict))
    unique_operators += len(unique_state_algo_operators)

    #Getting total operands
    #N1
    total_operands = 0
    total_operands += get_ECC_edge_count(xml_dict)
    
    for i in xml_dict['FBType']['BasicFB']['ECC']['ECState']:
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
    unique_operands += len(get_ECC_unique_edges(xml_dict))
    unique_operands += len(unique_algos)
    unique_operands += len(unique_event_outputs)

    #Calculating the HV
    return calc_HV(unique_operands, total_operands, unique_operators, total_operators)


def calc_ALGO_HV_program_volume(xml_dict):
    return
    



def get_HV_edge_count(xml_dict):
    unique_edges = get_ECC_unique_edges(xml_dict)
    if '1' in unique_edges:
        return len(unique_edges -1)
    else:
        return len(unique_edges)


def get_total_LOC_Algo(LOC_dict):
    count = 0
    for i in LOC_dict.keys():
        count += LOC_dict[i]
    return count

def calc_total_LOC_BFB(xml_dict):
    algo_dict = get_algorithms_LOC_BFB(xml_dict)
    LOC = 0
    #Algo LOC
    LOC += get_total_LOC_Algo(algo_dict)
    #ECC LOC
    ECC_Nodes = get_ECC_node_count(xml_dict) 
    ECC_Edges = get_ECC_edge_count(xml_dict)
    LOC += (ECC_Nodes + ECC_Edges)
    return LOC


def calc_CC_BFB(xml_dict):
    edges = 0
    edges += get_ECC_node_count(xml)

def calc_total_CC_BFB(xml_dict):
    #Getting CC of algorithmms
    algorithms = xml_dict['FBType']['BasicFB']['Algorithm']

    CC = 0
    for algo in algorithms:
        CC += calc_CC_algorithm(algo['ST']['@Text'])

    #Getting CC of ECC
    ECC_Nodes = get_ECC_node_count(xml_dict) 
    ECC_Edges = get_ECC_edge_count(xml_dict)
    CC += (ECC_Edges - ECC_Nodes + 2)

    return CC

def calc_CC_algorithm(algorithm_text):
    control_flow_statements = re.findall(r'(IF.*?END_IF;|ELSIF.*?;|ELSE.*?;|END_IF;|[^;]+;)', algorithm_text)
    Nodes = len(control_flow_statements)
    Edges = Nodes - 1
    P = 2
    cyclomatic_complexity = Edges - Nodes + 2
    return cyclomatic_complexity 

def get_BFB_name(xml_dict):
    return xml_dict['FBType']['@Name']

def is_BFB(xml_dict):
    return 'FBNetwork' not in xml_dict['FBType'].keys()


#BFB LOC calc
def create_BFB_dict(xml_dict):
    name = get_BFB_name(xml_dict)
    FB_Obj = FunctionBlock.FunctionBlock(name, "BFB")

    FB_Obj.set_LOC(calc_total_LOC_BFB(xml_dict))
    FB_Obj.set_CC(calc_total_CC_BFB(xml_dict))
    FB_Obj.set_HV(calc_ECC_HV_program_volume(xml_dict))
    return FB_Obj

    
#Creates a dictionary of information from the CFB
def create_CFB_dict(FB_dict, xml_dict, name): 
    #Find all Basic function blocks in composite function block -> into array
    if type(xml_dict['FBType']['FBNetwork']['FB']) is dict:
        #Single Basic function block
        FB_Obj = FB_dict[xml_dict['FBType']['FBNetwork']['FB']['@Type']]
        return {
                'NAME': name,
                'MI': FB_Obj['MI']
                }

    else:
        #Array of Basic function blocks
        MI_sum = 0
        for child_fb in xml_dict['FBType']['FBNetwork']['FB']:
            print(child_fb['@Type'])
            FB_Obj = FB_dict[child_fb['@Type']]
            print(FB_Obj)

            MI_sum += FB_Obj['MI']


        #Divide values by length of array
        MI_avg = MI_sum / len(xml_dict['FBType']['FBNetwork']['FB'])

        return {
                'NAME': name,
                'MI': MI_avg
                }

#Finds all files in given dir with extension
def find_files_with_extension(directory, extension):
    search_pattern = os.path.join(directory, f"*.{extension}")
    print(search_pattern)
    files = glob.glob(search_pattern)
    return files

def files_to_dict(dict, file_paths):
    for file in file_paths:
        xml_dict = parse_XML_file(file)
        dict.update({ get_BFB_name(xml_dict): xml_dict })
    return



#Runtime vars
FB_dict = { } 
BFB_dict = { } #dictionary of Basic function blocks maps name->BFB obj
CFB_dict = { }
extension = "fbt"
folder = "../example/"
all_fbt_files_names = []
all_FB_files = { } #dictionary mapping FB name to xml
BFB_files = []
CBF_files = []


#Run time logic
#Given folder find all files that are .fbt file extension
all_fbt_files_names = find_files_with_extension(folder, extension)
print(all_fbt_files_names)

#Parsing all the xml files 
files_to_dict(all_FB_files, all_fbt_files_names)
print(all_FB_files.keys())

#Split files into BFB files and CFB files
for file_name in all_FB_files:
    if is_BFB(all_FB_files[file_name]):
        BFB_files.append(file_name)
    else:
        CBF_files.append(file_name)

#Create dictionary of MI of basic function blocks
for file_name in BFB_files:
    BFB_dict.update({ file_name: create_BFB_dict(all_FB_files[file_name]) })


#Create dictionary of MI of composite function blocks using the basic function blocks
FB_processing_queue = deque()
#Putting all CFB in queue
for file_name in CBF_files:
    FB_processing_queue.append(create_CFB_dict(FB_dict, all_FB_files[file_name], file_name))
    #CFB_dict.update({ file_name: create_CFB_dict(FB_dict, all_FB_files[file_name], file_name) })

print(FB_processing_queue)
print("-----------")


#Addition functions
#Average all MI from all CFB and BFB
