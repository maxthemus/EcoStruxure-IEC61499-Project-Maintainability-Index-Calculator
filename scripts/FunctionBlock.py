import math

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

    #Setters 
    def set_type(self, type):
        self.type = type
        return

    def set_LOC(self, LOC):
        self.LOC = LOC
        self.update_MI()

    def set_HV(self, HV):
        self.HV = HV
        self.update_MI()

    def set_CC(self, CC):
        self.CC = CC
        self.update_MI()
    

    #Methods
    def update_MI(self):
        self.MI = self.calc_MI(self.HV, self.LOC, self.CC)

    def calc_MI(self, HV, LOC, CC):
        if HV == 0 or LOC == 0 or CC == 0:
            return 0
        else:
            return (171 - (5.2 * math.log(HV)) - (0.23 * math.log(CC)) - (16.2 * math.log(LOC)))

    def addChild(self, childFB):
        self.children.append(childFB)

    def __str__(self):
        return self.name + " : " + self.type + " : " + str(len(self.children))







