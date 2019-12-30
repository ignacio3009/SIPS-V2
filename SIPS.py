# -*- coding: utf-8 -*-
"""
Created on Sat Dec 28 18:11:43 2019

@author: ignac
"""

import simulation
import model
import numpy as np
import matplotlib.pyplot as plt



# model.mainModel()
simulation.solve()


def getNumberOfLineLimitsViolations(line):
    simlin = np.load('results\\SIMLIN.npy') 
    NHrs =  24
    NSce =  7
    line_loading_column = 9
    cnt =   0
    for s in range(NSce):
        for t in range(NHrs):
            if(simlin[t,s,line,line_loading_column]>1.001):
                cnt=cnt+1
    return cnt
    
def getLineLimitsViolations(line):
    simlin = np.load('results\\SIMLIN.npy') 
    instances = []
    NHrs =  24
    NSce =  7
    line_loading_column = 13
    cnt =   0
    for s in range(NSce):
        for t in range(NHrs):
            if(simlin[t,s,line,line_loading_column]>115.0):
                cnt=cnt+1
                instances.append((t,s,simlin[t,s,line,line_loading_column]))
    return cnt,instances





x1,ins = getLineLimitsViolations(1)
print(x1)
print(ins)


# simgen = np.load('results\\SIMGEN.npy') #t,s,g,field
# print(simgen[0,2,0,:])
# ecogen = np.load('results\\ECOPSOL.npy') #g,s,t
# print(ecogen[0,2,0])





# simbus = np.load('results\\SIMBUS.npy') #(24,7,6,4)
# simlin = np.load('results\\SIMLIN.npy') #(24,7,3,14)
# simtrf = np.load('results\\SIMTRF.npy') #(24,7,3,13)
# simgen = np.load('results\\SIMGEN.npy') #(24,7,3,4)
# simsto = np.load('results\\SIMSTO.npy') #(24,7,3,2)
# print(simsto)

# line = 2 #0,1
# scen = 6 #1,2
# cat = 9 #line loading
# plt.plot(simlin[:,scen,line,cat])
# plt.ylim((0.9,1.1))
#simbus = 



#SIMBUS DATA
#0: vm_pu	             voltage magnitude [p.u]
#1: va_degree	         voltage angle [degree]
#2: p_mw	             resulting active power demand [MW]
#3: q_mvar	             resulting reactive power demand [Mvar]


#SIMLIN 
#0: p_from_mw	        active power flow into the line at “from” bus [MW]	
#1: q_from_mvar	        reactive power flow into the line at “from” bus [MVar]	
#2: p_to_mw	            active power flow into the line at “to” bus [MW]	
#3: q_to_mvar	        reactive power flow into the line at “to” bus [MVar]	
#4: pl_mw	            active power losses of the line [MW]	
#5: ql_mvar	            reactive power consumption of the line [MVar]	
#6: i_from_ka	        Current at to bus [kA]	
#7: i_to_ka	            Current at from bus [kA]	
#8: i_ka	            Maximum of i_from_ka and i_to_ka [kA]	
#9: loading_percent	    line loading [%]	

#SIMTRF 
#0:	p_hv_mw	            active power flow at the high voltage transformer bus [MW]
#1:	q_hv_mvar	        reactive power flow at the high voltage transformer bus [MVar]
#2: p_lv_mw	            active power flow at the low voltage transformer bus [MW]
#3:	q_lv_mvar	        reactive power flow at the low voltage transformer bus [MVar]
#4:	pl_mw	            active power losses of the transformer [MW]
#5:	ql_mvar	            reactive power consumption of the transformer [Mvar]
#6:	i_hv_ka	            current at the high voltage side of the transformer [kA]
#7:	i_lv_ka	            current at the low voltage side of the transformer [kA]
#8:	loading_percent	    load utilization relative to rated power [%]

#SIMGEN 
#0:	p_mw	            resulting active power demand after scaling [MW]
#1:	q_mvar	            resulting reactive power demand after scaling [MVar]
#2:	va_degree	        generator voltage angle [degree]
#3:	vm_pu	            voltage at the generator [p.u]


#SIMSTO 
#0:	p_mw	           resulting active power after scaling [MW]
#1:	q_mvar	           resulting reactive power after scaling [MVar]


