# -*- coding: utf-8 -*-
"""
Created on Sat Dec 28 22:38:08 2019

@author: ignac
"""
import gurobipy as gp
from gurobipy import GRB
import numpy as np
import xlwings as xw
from gurobipy import quicksum
import matplotlib.pyplot as plt

# =============================================================================
# READ DATA
# =============================================================================

M = 10000
NGen = 3
NLin = 3
NBar = 3
NHrs = 24

NEle = NGen + NLin
NFal = NGen + NLin
NSce = NFal + 1
numLin = range(NLin)
numBar = range(NBar)
numGen = range(NGen)
numFal = range(NFal)
numEle = range(NEle)
numSce = range(NSce)
numHrs = range(NHrs)
numScF = range(1,NSce)

wb = xw.Book('data_3_bus.xlsx')
sh = wb.sheets['data']

#Generator data
GENDATA = np.array(sh.range('A4:N6').value)
genBar =    GENDATA[:,1]
CV =        GENDATA[:,2]
CRUP =      GENDATA[:,3]
CRDOWN =    GENDATA[:,4]
CENC =      GENDATA[:,5]
CAPG =      GENDATA[:,6]
RUPMAX =    GENDATA[:,7]
RDOWNMAX =  GENDATA[:,8]
PMAXGEN =   GENDATA[:,9]
PMINGEN =   GENDATA[:,10]
QMAXGEN =   GENDATA[:,11]
QMINGEN =   GENDATA[:,12]

#Demand data
DEMDATA =   np.array(sh.range('P4:R6').value)
DPMAX =     DEMDATA[:,1]
DQMAX =     DEMDATA[:,2]

#Line data
LINDATA =   np.array(sh.range('T4:Z6').value)
FMAX =      LINDATA[:,1]
XL =        LINDATA[:,4]


#Battery data
STODATA =   np.array(sh.range('AB4:AM6').value)


#Scenarios data
A =  np.array(sh.range('AP4:AV6').value)
B =  np.array(sh.range('AP7:AV9').value)
PROB = np.array(sh.range('AW4:AW9').value)


wblc = xw.Book('load_curve.xlsx')
shlc = wblc.sheets['data']
DEMRES = np.array(shlc.range('B2:B25').value)
DEMIND = np.array(shlc.range('C2:C25').value)
DEMCOM = np.array(shlc.range('D2:D25').value)

D = np.array([DPMAX[0]*DEMRES,DPMAX[1]*DEMIND,DPMAX[2]*DEMCOM])



# =============================================================================
# DEFINE VARIABLES
# =============================================================================
#Define problem
model  = gp.Model("Model")
#Variables
p =     model.addVars(NGen,NSce,NHrs, vtype=GRB.CONTINUOUS)
x =     model.addVars(NGen,NHrs, vtype=GRB.BINARY)
e =     model.addVars(NGen,NHrs, vtype=GRB.BINARY)
a =     model.addVars(NGen,NHrs, vtype=GRB.BINARY)
f =     model.addVars(NLin,NSce,NHrs, vtype = GRB.CONTINUOUS, lb=-GRB.INFINITY)
theta = model.addVars(NBar,NSce,NHrs, vtype = GRB.CONTINUOUS, lb=-GRB.INFINITY)
rup =   model.addVars(NGen,NSce,NHrs, vtype = GRB.CONTINUOUS)
rdown = model.addVars(NGen,NSce,NHrs, vtype = GRB.CONTINUOUS)
xrup =  model.addVars(NGen,NSce,NHrs, vtype = GRB.BINARY)
xrdown = model.addVars(NGen,NSce,NHrs, vtype = GRB.BINARY)

#Objective Function
Objective = quicksum(quicksum(CV[g]*p[g,0,t] + CENC[g]*e[g,t] + CAPG[g]*a[g,t] for g in numGen) + 
            quicksum(PROB[s-1]*quicksum(CV[g]*p[g,s,t]  + CRUP[g]*rup[g,s,t] + CRDOWN[g]* rdown[g,s,t] for g in numGen) 
                     for s in numScF) for t in numHrs)
            
#Contraints

#Turn on and Turn Off machines
for g in numGen:
    model.addConstr(x[g,0] == e[g,0] - a[g,0])

            
for t in range(2,NHrs):
    for g in numGen:
        model.addConstr(x[g,t] == x[g,t-1] + e[g,t] - a[g,t])

for t in range(3,NHrs):
    for g in numGen:
        model.addConstr(x[g,t]>=quicksum(e[g,k] for k in range(t-3,t)))
        model.addConstr(1-x[g,t]>=quicksum(a[g,k] for k in range(t-3,t)))
    
for g in numGen:
    model.addConstr(x[g,0] >= e[g,0])
    model.addConstr(1 - x[g,0] >= a[g,0])


for g in numGen:
    model.addConstr(x[g,1] >= quicksum(e[g,k] for k in range(2)))        
    model.addConstr(1 - x[g,1] >= quicksum(a[g,k] for k in range(2)))  

for g in numGen:
    model.addConstr(x[g,2] >= quicksum(e[g,k] for k in range(3)))        
    model.addConstr(1 - x[g,2] >= quicksum(a[g,k] for k in range(3))) 

    
#Limits of Generators
for t in numHrs:
    for s in numSce:
        for g in numGen:
            model.addConstr(p[g,0,t] + rup[g,s,t] <= PMAXGEN[g]*x[g,t])
            model.addConstr(p[g,0,t] - rdown[g,s,t] >= PMINGEN[g]*x[g,t])
            
            model.addConstr(rup[g,s,t] <= RUPMAX[g]*xrup[g,s,t])
            model.addConstr(rdown[g,s,t] <= RDOWNMAX[g]*xrdown[g,s,t])
            model.addConstr(xrup[g,s,t] + xrdown[g,s,t] <= 1)
            

#Reserves are 0 for the base case scenario
for t in numHrs:
    for g in numGen:
        model.addConstr(xrup[g,0,t] +  xrdown[g,0,t] == 0)
        
    
#Nodal Balancing por scenarios pre and post failure
for t in numHrs:
    for s in numSce:
         model.addConstr(p[0,s,t] == D[0,t] + f[0,s,t] + f[2,s,t])
         model.addConstr(p[1,s,t] + f[0,s,t] == D[1,t] + f[1,s,t])
         model.addConstr(p[2,s,t] + f[2,s,t] + f[1,s,t] == D[2,t])

#Availability of elements
for t in numHrs:
    for s in numSce:
        #Availability of generators
        for g in numGen:
            model.addConstr(p[g,s,t] <= A[g,s]*(p[g,0,t] + rup[g,s,t]))
            model.addConstr(p[g,s,t] >= A[g,s]*(p[g,0,t] - rdown[g,s,t]))
        
        #Availability of lines
        for l in numLin:
            model.addConstr(f[l,s,t] <= FMAX[l]*B[l,s])
            model.addConstr(f[l,s,t] >= -1*FMAX[l]*B[l,s])
        
        model.addConstr(f[0,s,t] <= 1/XL[0]*(theta[0,s,t]-theta[1,s,t]) + M*(1-B[0,s]))
        model.addConstr(f[0,s,t] >= 1/XL[0]*(theta[0,s,t]-theta[1,s,t]) - M*(1-B[0,s]))
        model.addConstr(f[1,s,t] <= 1/XL[1]*(theta[1,s,t]-theta[2,s,t]) + M*(1-B[1,s]))
        model.addConstr(f[1,s,t] >= 1/XL[1]*(theta[1,s,t]-theta[2,s,t]) - M*(1-B[1,s]))
        model.addConstr(f[2,s,t] <= 1/XL[2]*(theta[0,s,t]-theta[2,s,t]) + M*(1-B[2,s]))
        model.addConstr(f[2,s,t] >= 1/XL[2]*(theta[0,s,t]-theta[2,s,t]) - M*(1-B[2,s]))
        
        
        
        
# =============================================================================
# RUN MODEL
# =============================================================================
model.setObjective(Objective, GRB.MINIMIZE)
model.optimize()
print('=== RESULTS: ===')
print(model.objVal)
            
# =============================================================================
# SAVE RESULTS
# ============================================================================= 

psol =      np.array([[[p[g,s,t].X for t in numHrs] for s in numSce] for g in numGen])
xsol =      np.array([[x[g,t].X for t in numHrs] for g in numGen])
esol =      np.array([[e[g,t].X for t in numHrs] for g in numGen])
asol =      np.array([[a[g,t].X for t in numHrs] for g in numGen])
fsol =      np.array([[[f[l,s,t].X for t in numHrs] for s in numSce] for l in numLin])
thetasol =  np.array([[[theta[n,s,t].X for t in numHrs] for s in numSce] for n in numBar])
rupsol =    np.array([[[rup[g,s,t].X for t in numHrs] for s in numSce] for g in numGen])
rdownsol =  np.array([[[rdown[g,s,t].X for t in numHrs] for s in numSce] for g in numGen])
xrupsol =   np.array([[[xrup[g,s,t].X for t in numHrs] for s in numSce] for g in numGen])
xrdownsol = np.array([[[xrdown[g,s,t].X for t in numHrs] for s in numSce] for g in numGen])


np.save('psol',psol)
np.save('xsol',xsol)
np.save('esol',esol)
np.save('asol',asol)
np.save('fsol',fsol)
np.save('thetasol',thetasol)
np.save('rupsol',rupsol)
np.save('rdownsol',rdownsol)
np.save('xrupsol',xrupsol)
np.save('xrdownsol',xrdownsol)

