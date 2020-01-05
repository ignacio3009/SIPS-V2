# -*- coding: utf-8 -*-
"""
Created on Fri Jan  3 05:50:49 2020

@author: ignac
"""

import numpy as np
import contingencies as cont
import simulation as sm
import loaddata as ld
import modelrelax as mdr

def getModelRelaxResults():
    mdr.relaxLine([1,2],[1.4,1.4])
    datacont1 = cont.getInstancesLineLimitsViolations1(tolerance=1.1)
    datacont2 = cont.getInstancesLineLimitsViolations2(tolerance=1.05)
    datacont3 = cont.getInstancesLineLimitsViolations3(tolerance=1.1)
    
    # sm.despachonormal(datacont3,relax_vm=[0.95, 1.05])
    # sm.redespacho(datacont2,relax_vm=[0.95, 1.05])
    # sm.sips(datacont1,relax_vm=[0.95, 1.05],print_results = True, verbose=True)
    
        
    
    
    
    # SIMLIN = np.load('results\\SIMLIN.npy')
    
    # =============================================================================
    # SOBRE 110
    # =============================================================================
    D = np.load('results\\EVALSIPSBATTERYLOADSHEDDING_D.npy')
    B = np.load('results\\EVALSIPSBATTERYLOADSHEDDING_B.npy')
    L = np.load('results\\EVALSIPSBATTERYLOADSHEDDING_L.npy')
    G = np.load('results\\EVALSIPSBATTERYLOADSHEDDING_G.npy')
    N = np.load('results\\EVALSIPSBATTERYLOADSHEDDING_N.npy')
    
    # =============================================================================
    # ENTRE 100 Y 110
    # =============================================================================
    D2 = np.load('results\\EVALSIPSBATTERYLOADSHEDDING_D2.npy')
    B2 = np.load('results\\EVALSIPSBATTERYLOADSHEDDING_B2.npy')
    L2 = np.load('results\\EVALSIPSBATTERYLOADSHEDDING_L2.npy')
    G2 = np.load('results\\EVALSIPSBATTERYLOADSHEDDING_G2.npy')
    N2 = np.load('results\\EVALSIPSBATTERYLOADSHEDDING_N2.npy')
    
    # =============================================================================
    # MENOR A 100
    # =============================================================================
    D3 = np.load('results\\EVALSIPSBATTERYLOADSHEDDING_D3.npy')
    B3 = np.load('results\\EVALSIPSBATTERYLOADSHEDDING_B3.npy')
    L3 = np.load('results\\EVALSIPSBATTERYLOADSHEDDING_L3.npy')
    G3 = np.load('results\\EVALSIPSBATTERYLOADSHEDDING_G3.npy')
    N3 = np.load('results\\EVALSIPSBATTERYLOADSHEDDING_N3.npy')
    
    
    
    numHrs = range(24)
    numSce = range(7)
    realcost = 0
    
    GENDATA,DEMDATA,LINDATA,STODATA =  ld.loadsystemdata()
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
    
    AA, BB,PROB = ld.loadscendata()
    
    DEM = DEMDATA[:,1]
    CDLS = DEMDATA[:,3]
    PREAL = np.ndarray((3,7,24))
    
    CBAT =    abs(STODATA[:,2])
    
    for t in numHrs:
        for s in numSce:
            z = (t,s)
            if z in datacont1:
                idx = datacont1.index(z)
                PG = G[idx,:,0]
                DM = D[idx,:,0]
                BM = B[idx,:,0]
                PREAL[:,s,t] = PG
               
               
            elif z in datacont2:
                idx = datacont2.index(z)
                PG = G2[idx,:,0]
                DM = D2[idx,:,0]
                BM = B2[idx,:,0]
                PREAL[:,s,t] = PG
                
            elif z in datacont3:
                idx = datacont3.index(z)
                PG = G3[idx,:,0]
                DM = D3[idx,:,0]
                BM = B3[idx,:,0]
                PREAL[:,s,t] = PG
            else:
                print('Data not found!')
                
            if s==0:
                   realcost = realcost + CV.dot(PG)
            else:
                crup  = CRUP.dot(PG-PREAL[:,0,t]) 
                if(crup<0): crup =0
                crdown  = CRDOWN.dot(PREAL[:,0,t]-PG) 
                if(crdown<0): crdown=0
                deltadem = abs(DEM[:] - DM)
                cdls = CDLS.dot(deltadem)
                cbat = BM.dot(CBAT[:])
                realcost = realcost + PROB[s-1]*(CV.dot(PG + crup + crdown + cdls + cbat))
            
            
            
    print('Costos Totales reales modelo Relajado', realcost)
    
    
