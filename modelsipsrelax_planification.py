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
import loaddata as ld

# =============================================================================
# READ DATA
# =============================================================================
def run(lin,relaxcapacity,verbose=False):
    """
    Realiza Optimización de Despacho con Seguridad para 
    horizonte de tiempo sin considerar relajo de restricciones.
    """
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
    
    GENDATA,DEMDATA,LINDATA,STODATA = ld.loadsystemdata()
    
    #Generator data
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
    DPMAX =     DEMDATA[:,1]
    DQMAX =     DEMDATA[:,2]
    
    #Line data
    FMAX =      LINDATA[:,1]
    XL =        LINDATA[:,4]
    LENGTHLINE= LINDATA[:,6]
    #Demand data
    DEMRES, DEMIND, DEMCOM  = ld.loadcurvedata()    
    D = np.array([DPMAX[0]*DEMRES,DPMAX[1]*DEMIND,DPMAX[2]*DEMCOM])
    
    
    #Scenarios data
    A, B,PROB = ld.loadscendata()
    
    # =============================================================================
    #     SIPS 
    # =============================================================================
    #Storage data
    CBAT =    abs(STODATA[:,2])
    PMAXBAT = abs(STODATA[:,8])
    
    #Load Shedding
    DEMLSMAX  = DEMDATA[:,4]
    CLS = DEMDATA[:,3]

    # =============================================================================
    # ADD MORE CAPACITY TO LINE TO RELAX CONSTRAINT
    # =============================================================================
    FMAXP = FMAX.copy()
            
    if type(lin) is list:
        for (l,rc) in zip(lin,relaxcapacity):
            FMAXP[l] = rc*FMAXP[l]
    elif type(lin) is int:
        FMAXP[lin] = relaxcapacity*FMAXP[lin] 
    
    # =============================================================================
    # FACTOR CRECIMIENTO GENERACIÓN, DEMANDA Y LINEAS   
    # =============================================================================
    #crecimiento demanda anual
    fdem = 1.05
    #crecimiento capacidad en MW
    fcap = 100 
    #crecimiento generacion
    fgen = 1.07
    # =============================================================================
    #     COSTOS DE INVERSION POR MW
    # =============================================================================
    CINVLIN = 740*LENGTHLINE[0]
    CINVBAT = 400000
    print(CINVLIN*fcap)
    
    # =============================================================================
    # HORIZONTE PLANIFICACION    
    # =============================================================================
    NYears = 20
    numYears = range(NYears)
    
    
    DEMY =      np.ndarray((NYears,NBar,NHrs))
    RUPMAXY =   np.ndarray((NYears,NGen))
    RDOWNMAXY = np.ndarray((NYears,NGen))
    PMAXGENY =  np.ndarray((NYears,NGen))
    PMINGENY =  np.ndarray((NYears,NGen))
    
    
    
    for y in numYears:
        DEMY[y,:] = (fdem**y)*D
        PMAXGENY[y,:] = (fgen**y)*PMAXGEN[:]
        RUPMAXY[y,:] = (fgen**y)*RUPMAX[:]
        RDOWNMAXY[y,:] = (fgen**y)*RDOWNMAX[:]
        PMINGENY[y,:] = PMINGEN[:]
        
    
    
    # =============================================================================
    # DEFINE VARIABLES
    # =============================================================================
    #Define problem
    model  = gp.Model("Model")
    if not verbose:
        model.setParam('OutputFlag',0)
    else:
        model.setParam('OutputFlag',1)
    #Variables
    p =     model.addVars(NYears,NGen,NSce,NHrs, vtype=GRB.CONTINUOUS)
    x =     model.addVars(NYears,NGen,NHrs, vtype=GRB.BINARY)
    e =     model.addVars(NYears,NGen,NHrs, vtype=GRB.BINARY)
    a =     model.addVars(NYears,NGen,NHrs, vtype=GRB.BINARY)
    f =     model.addVars(NYears,NLin,NSce,NHrs, vtype = GRB.CONTINUOUS, lb=-GRB.INFINITY)
    theta = model.addVars(NYears,NBar,NSce,NHrs, vtype = GRB.CONTINUOUS, lb=-GRB.INFINITY)
    rup =   model.addVars(NYears,NGen,NSce,NHrs, vtype = GRB.CONTINUOUS)
    rdown = model.addVars(NYears,NGen,NSce,NHrs, vtype = GRB.CONTINUOUS)
    xrup =  model.addVars(NYears,NGen,NSce,NHrs, vtype = GRB.BINARY)
    xrdown = model.addVars(NYears,NGen,NSce,NHrs, vtype = GRB.BINARY)
    #SIPS
    pbat = model.addVars(NYears,NGen, NSce, NHrs, vtype = GRB.CONTINUOUS)
    demls= model.addVars(NYears,NGen, NSce, NHrs, vtype = GRB.CONTINUOUS)
    #Investments Line
    xf50 = model.addVars(NLin, vtype=GRB.BINARY)
    #Battery
    xbat = model.addVars(NBar, vtype=GRB.BINARY)
    #Objective Function
    Objective = quicksum(quicksum(quicksum(CV[g]*p[y,g,0,t] + CENC[g]*e[y,g,t] + CAPG[g]*a[y,g,t] for g in numGen) + 
                quicksum(PROB[s-1]*quicksum(CV[g]*p[y,g,s,t]  + CRUP[g]*rup[y,g,s,t] + CRDOWN[g]* rdown[y,g,s,t] 
                                            for g in numGen) for s in numScF) for t in numHrs) + 
                quicksum(quicksum(PROB[s-1]*quicksum(CBAT[b]*pbat[y,b,s,t] + CLS[b]*demls[y,b,s,t] for b in numBar) 
                                 for s in numScF) for t in numHrs)for y in numYears) + \
                quicksum(fcap*xf50[l]*CINVLIN for l in numLin) + \
                quicksum(PMAXBAT[b]*CINVBAT*xbat[b] for b in numBar)
               
    
    
    #Contraints
    #Turn on and Turn Off machines
    for y in numYears:
        for g in numGen:
            model.addConstr(x[y,g,0] == e[y,g,0] - a[y,g,0])
        
                    
        for t in range(2,NHrs):
            for g in numGen:
                model.addConstr(x[y,g,t] == x[y,g,t-1] + e[y,g,t] - a[y,g,t])
        
        for t in range(3,NHrs):
            for g in numGen:
                model.addConstr(x[y,g,t]>=quicksum(e[y,g,k] for k in range(t-3,t)))
                model.addConstr(1-x[y,g,t]>=quicksum(a[y,g,k] for k in range(t-3,t)))
            
        for g in numGen:
            model.addConstr(x[y,g,0] >= e[y,g,0])
            model.addConstr(1 - x[y,g,0] >= a[y,g,0])
        
        
        for g in numGen:
            model.addConstr(x[y,g,1] >= quicksum(e[y,g,k] for k in range(2)))        
            model.addConstr(1 - x[y,g,1] >= quicksum(a[y,g,k] for k in range(2)))  
        
        for g in numGen:
            model.addConstr(x[y,g,2] >= quicksum(e[y,g,k] for k in range(3)))        
            model.addConstr(1 - x[y,g,2] >= quicksum(a[y,g,k] for k in range(3))) 
        
            
        #Limits of Generators
        for t in numHrs:
            for s in numSce:
                for g in numGen:
                    model.addConstr(p[y,g,0,t] + rup[y,g,s,t] <= PMAXGENY[y,g]*x[y,g,t])
                    model.addConstr(p[y,g,0,t] - rdown[y,g,s,t] >= PMINGENY[y,g]*x[y,g,t])
                    
                    model.addConstr(rup[y,g,s,t] <= RUPMAXY[y,g]*xrup[y,g,s,t])
                    model.addConstr(rdown[y,g,s,t] <= RDOWNMAXY[y,g]*xrdown[y,g,s,t])
                    model.addConstr(xrup[y,g,s,t] + xrdown[y,g,s,t] <= 1)
                    #Baterias
                    model.addConstr(pbat[y,g,s,t]<=PMAXBAT[g]*xbat[g])
                    #Loas shedding
                    model.addConstr(demls[y,g,s,t]<=DEMLSMAX[g])
                    
        
        #Reserves are 0 for the base case scenario
        for t in numHrs:
            for g in numGen:
                model.addConstr(xrup[y,g,0,t] +  xrdown[y,g,0,t] == 0)
                model.addConstr(demls[y,g,0,t] == 0)
                model.addConstr(pbat[y,g,0,t]==0)
                
            
        #Nodal Balancing por scenarios pre and post failure
        for t in numHrs:
            for s in numSce:
                 model.addConstr(p[y,0,s,t] + pbat[y,0,s,t] == DEMY[y,0,t] + f[y,0,s,t] + f[y,2,s,t] - demls[y,0,s,t])
                 model.addConstr(p[y,1,s,t] + pbat[y,1,s,t] + f[y,0,s,t] == DEMY[y,1,t] + f[y,1,s,t] - demls[y,1,s,t])
                 model.addConstr(p[y,2,s,t] + pbat[y,2,s,t] + f[y,2,s,t] + f[y,1,s,t] == DEMY[y,2,t] - demls[y,2,s,t])
        
        #Availability of elements
        for t in numHrs:
            for s in numSce:
                #Availability of generators
                for g in numGen:
                    model.addConstr(p[y,g,s,t] <= A[g,s]*(p[y,g,0,t] + rup[y,g,s,t]))
                    model.addConstr(p[y,g,s,t] >= A[g,s]*(p[y,g,0,t] - rdown[y,g,s,t]))
                
                #Availability of lines
                for l in numLin:
                    model.addConstr(f[y,l,s,t] <= FMAX[l]*B[l,s] + fcap*xf50[l]*B[l,s])
                    model.addConstr(f[y,l,s,t] >= -1*FMAX[l]*B[l,s] - fcap*xf50[l]*B[l,s])
                
                model.addConstr(f[y,0,s,t] <= 1/XL[0]*(theta[y,0,s,t]-theta[y,1,s,t]) + M*(1-B[0,s]))
                model.addConstr(f[y,0,s,t] >= 1/XL[0]*(theta[y,0,s,t]-theta[y,1,s,t]) - M*(1-B[0,s]))
                model.addConstr(f[y,1,s,t] <= 1/XL[1]*(theta[y,1,s,t]-theta[y,2,s,t]) + M*(1-B[1,s]))
                model.addConstr(f[y,1,s,t] >= 1/XL[1]*(theta[y,1,s,t]-theta[y,2,s,t]) - M*(1-B[1,s]))
                model.addConstr(f[y,2,s,t] <= 1/XL[2]*(theta[y,0,s,t]-theta[y,2,s,t]) + M*(1-B[2,s]))
                model.addConstr(f[y,2,s,t] >= 1/XL[2]*(theta[y,0,s,t]-theta[y,2,s,t]) - M*(1-B[2,s]))
                
                
        #Capacity of lines in scenario base 0
        for t in numHrs:
            for l in numLin:
                model.addConstr(f[y,l,0,t] <= FMAX[l]*B[l,0] + fcap*xf50[l]*B[l,0]) #scenario 0: must respect limits
                model.addConstr(f[y,l,0,t] >= -1*FMAX[l]*B[l,0] - fcap*xf50[l]*B[l,0]) #scenarios of contingencies can violate limits until a treshhold
                
        
        #Capacity of lines relaxed for scenarios of contingencies
        for t in numHrs:
            for s in numScF:
                for l in numLin:
                    model.addConstr(f[y,l,s,t] <= FMAXP[l]*B[l,s]  + fcap*xf50[l]*B[l,s])
                    model.addConstr(f[y,l,s,t] >= -1*FMAXP[l]*B[l,s] -  fcap*xf50[l]*B[l,s])
            
            
    # =============================================================================
    # RUN MODEL
    # =============================================================================
    model.setObjective(Objective, GRB.MINIMIZE)
    model.optimize()
   
    print('Costos Totales:',model.objVal)
                
    # =============================================================================
    # SAVE RESULTS
    # ============================================================================= 
    
    psol =      np.array([[[[p[y,g,s,t].X for t in numHrs] for s in numSce] for g in numGen] for y in numYears])
    xsol =      np.array([[[x[y,g,t].X for t in numHrs] for g in numGen]for y in numYears])
    esol =      np.array([[[e[y,g,t].X for t in numHrs] for g in numGen]for y in numYears])
    asol =      np.array([[[a[y,g,t].X for t in numHrs] for g in numGen]for y in numYears])
    fsol =      np.array([[[[f[y,l,s,t].X for t in numHrs] for s in numSce] for l in numLin]for y in numYears])
    thetasol =  np.array([[[[theta[y,n,s,t].X for t in numHrs] for s in numSce] for n in numBar]for y in numYears])
    rupsol =    np.array([[[[rup[y,g,s,t].X for t in numHrs] for s in numSce] for g in numGen]for y in numYears])
    rdownsol =  np.array([[[[rdown[y,g,s,t].X for t in numHrs] for s in numSce] for g in numGen]for y in numYears])
    xrupsol =   np.array([[[[xrup[y,g,s,t].X for t in numHrs] for s in numSce] for g in numGen]for y in numYears])
    xrdownsol = np.array([[[[xrdown[y,g,s,t].X for t in numHrs] for s in numSce] for g in numGen]for y in numYears])
    demlssol =  np.array([[[[demls[y,g,s,t].X for t in numHrs] for s in numSce] for g in numGen]for y in numYears])
    pbatsol =   np.array([[[[pbat[y,g,s,t].X for t in numHrs] for s in numSce] for g in numGen]for y in numYears])
    xf50sol =   np.array([xf50[l].X for l in numLin])
    xbatsol =   np.array([xbat[b].X for b in numBar])
    
    print('Inversion Lineas',xf50sol)
    print('Inversion Baterias', xbatsol)

    np.save('results\\ECOPSOL_SIPS_PLANIFICACION',psol)
    np.save('results\\ECOXSOL_SIPS_PLANIFICACION',xsol)
    np.save('results\\ECOESOL_SIPS_PLANIFICACION',esol)
    np.save('results\\ECOASOL_SIPS_PLANIFICACION',asol)
    np.save('results\\ECOFSOL_SIPS_PLANIFICACION',fsol)
    np.save('results\\ECOTHETASOL_SIPS_PLANIFICACION',thetasol)
    np.save('results\\ECORUPSOL_SIPS_PLANIFICACION',rupsol)
    np.save('results\\ECORDOWNSOL_SIPS_PLANIFICACION',rdownsol)
    np.save('results\\ECOXRUPSOL_SIPS_PLANIFICACION',xrupsol)
    np.save('results\\ECOXRDOWNSOL_SIPS_PLANIFICACION',xrdownsol)
    np.save('results\\ECODEM_SIPS_PLANIFICACION',D)
    np.save('results\\ECOPDEMLSSOL_SIPS_PLANIFICACION',demlssol)
    np.save('results\\ECOPBATSOL_SIPS_PLANIFICACION',pbatsol)
    return model.objVal

if __name__ == '__main__':
    run([1,2],[2,2])
    
