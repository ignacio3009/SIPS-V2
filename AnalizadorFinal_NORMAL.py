# -*- coding: utf-8 -*-
"""
Created on Fri Jan  3 05:50:49 2020

@author: ignac
"""

import numpy as np
import contingencies as cont
import simulation as sm
import loaddata as ld
import model as md
# md.run()
# sm.despachosinsips()

def getModelNormalResults():
    # =============================================================================
    # DESPACHO NORMAL
    # =============================================================================
    DN = np.load('results\\EVALNOSIPS_D.npy')
    BN = np.load('results\\EVALNOSIPS_B.npy')
    LN = np.load('results\\EVALNOSIPS_L.npy')
    GN = np.load('results\\EVALNOSIPS_G.npy')
    NN = np.load('results\\EVALNOSIPS_N.npy')
    
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
    CENS = 10000
    for t in numHrs:
        for s in numSce:
            PG = GN[t,s,:,0]
            DM = DN[t,s,:,0]
            
            if s==0:
                   realcost = realcost + CV.dot(PG)
            else:
                crup  = CRUP.dot(PG-PREAL[:,0,t]) 
                if(crup<0): crup =0
                crdown  = CRDOWN.dot(PREAL[:,0,t]-PG) 
                if(crdown<0): crdown=0
                
                ens = sum(DM) - sum(PG)
                if(ens>0): 
                    cdns = CENS*ens
                else:
                    cdns = 0
                
                realcost = realcost + PROB[s-1]*(CV.dot(PG + crup + crdown) + cdns)
            
            
            
    print('Costos Totales Reales modelo No relajado', realcost)
    
    
