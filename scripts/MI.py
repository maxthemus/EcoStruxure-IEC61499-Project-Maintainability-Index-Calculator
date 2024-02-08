# file calculates hold functions that calculate values for the Maintainability index
import math
import re
import xmltodict
import os
import glob
import FunctionBlock
from collections import deque

#XML parser
def parse_XML_file(file):
    with open(file, 'r') as f:
        xml_data = f.read()
    return xmltodict.parse(xml_data)


def get_FB_name(xml_dict):
    return xml_dict['FBType']['@Name']


def get_FB_type(xml_dict):
    if 'FBNetwork' not in xml_dict['FBType'].keys():
        return "BFB"
    else:
        return "CFB"


def is_BFB(xml_dict):
    return 'FBNetwork' not in xml_dict['FBType'].keys()


def get_CFB_children_names(xml_dict):
    if get_FB_type(xml_dict) == "CFB":
        child_names = []
        if isinstance(xml_dict['FBType']['FBNetwork']['FB'], list):
            #Multiple child
            child_list = xml_dict['FBType']['FBNetwork']['FB']
            for child in child_list:
                if child['@Namespace'] == "Main":
                    child_names.append(child['@Type'])
        else:
            #Single child FB
            child_dict = xml_dict['FBType']['FBNetwork']['FB']
            child_names.append(child_dict['@Type'])
        return child_names
    else:
        return []


#Create FB obj
def create_FB_from_dict(FB_dict, xml_dict):
    name = get_FB_name(xml_dict)
    type = get_FB_type(xml_dict)

    if name in FB_dict:
        FB_obj = FB_dict[name]
        FB_obj.set_type(type)
        FB_obj.set_xml(xml_dict)
    else:
        FB_obj = FunctionBlock.FB(name, type, xml_dict)
        FB_dict.update({ name: FB_obj })

    if not is_BFB(xml_dict):
        childrenNames = get_CFB_children_names(xml_dict)  

        for child_name in childrenNames:
            #Checking if FB already exist
            if child_name not in FB_dict:
                new_FB_obj = FunctionBlock.FB(child_name, "UNKNOWN", "")
                FB_dict.update({ child_name: new_FB_obj })

            child_obj = FB_dict[child_name]
            #appending child to FB_obj
            FB_obj.addChild(child_obj)

    return FB_obj



#BFB LOC calc
def create_BFB_dict(xml_dict):
    name = get_BFB_name(xml_dict)
    FB_Obj = FunctionBlock.FB(name, "BFB")

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
            FB_Obj = FB_dict[child_fb['@Type']]

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
        dict.update({ get_FB_name(xml_dict): xml_dict })
    return

def topological_sort_util(FB, visited, stack):
    visited[FB.get_name()] = True

    for child in FB.get_children():
        if(visited[child.get_name()] == False):
            topological_sort_util(child, visited, stack)

    stack.append(FB)


def topological_sort(FB_dict):
    incomingEdgeCount = { }
    visited = { }
    stack = [] 

    for key in FB_dict:
        visited.update({ key: False })
        incomingEdgeCount.update({ key: 0 })

    #Finding in comming count
    for FB_name in FB_dict.keys():
        FB = FB_dict[FB_name]
        for child in FB.get_children():
            count = incomingEdgeCount[child.get_name()]
            incomingEdgeCount[child.get_name()] = count + 1

    #sorting names 
    sortedNames = sorted(incomingEdgeCount, key=incomingEdgeCount.get)

    for FB_name in sortedNames:
        if visited[FB_name] == False:
            topological_sort_util(FB_dict[FB_name], visited, stack)
    
    return stack



#Runtime vars
FB_dict = { } 
BFB_dict = { } #dictionary of Basic function blocks maps name->BFB obj)
CFB_dict = { }
extension = "fbt"
folder = "../example/"
all_fbt_files_names = []
all_FB_files_dict = { } #dictionary mapping FB name to xml
BFB_files = []
CBF_files = []

FB_dict = { } # maps fb name to fb object

#Run time logic
#Given folder find all files that are .fbt file extension
all_fbt_files_names = find_files_with_extension(folder, extension)

#Parsing all the xml files 
files_to_dict(all_FB_files_dict, all_fbt_files_names)

#Split files into BFB files and CFB files
for file_name in all_FB_files_dict:
    FB_obj = create_FB_from_dict(FB_dict, all_FB_files_dict[file_name])
    
    if FB_obj.get_type() == "BFB":
        BFB_files.append(FB_obj)
    elif FB_obj.get_type() == "CFB":
        CBF_files.append(FB_obj)
    else:
        print("Unknown FB")

#Now we want to perform Topological sort on the FB_dict to figure out what order we need to calculate the MI
order = topological_sort(FB_dict)

#Claculating the MI of each FB
sum = 0
for i in order:
    i.update_MI()

for i in order:
    print(i.get_name(), " = ", i.get_MI())
    sum = sum + i.get_MI()

MI_total = sum / len(order)
print("Project MI total = ", MI_total)





    



