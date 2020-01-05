# # -*- coding: utf-8 -*-
# """
# Created on Sun Dec 29 18:00:45 2019

# @author: ignac
# """

import model as md
import modelrelax as mdr
import contingencies as cont
import sipscreator as sipscreator
import simulation as sm
import numpy as np
import loaddata as ld
import xlwings as xl






def getModelNormalResults():
    md.run()
    sm.despachosinsips(relax_vm=[0.9, 1.1])
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
    
    CBAT = abs(STODATA[:,2])
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
                
                realcost = realcost + PROB[s-1]*(CV.dot(PG) + crup + crdown + cdns)
            
            
            
    # print('Costos Totales Reales modelo No relajado', realcost)
    return realcost
    


def getModelRelaxResults():
    mdr.relaxLine([1,2],[1.4,1.4])
    datacont1 = cont.getInstancesLineLimitsViolations1(tolerance=1.1)
    datacont2 = cont.getInstancesLineLimitsViolations2(tolerance=1.1)
    datacont3 = cont.getInstancesLineLimitsViolations3(tolerance=1.1)
    
    sm.despachonormal(datacont3,relax_vm=[0.9, 1.1])
    sm.redespacho(datacont2,relax_vm=[0.9, 1.1])
    sm.sips(datacont1,relax_vm=[0.9, 1.1],print_results = False, verbose=False)
    
        
    
    
    
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
                realcost = realcost + PROB[s-1]*(CV.dot(PG) + crup + crdown + cdls + cbat)
            
            
            
    # print('Costos Totales reales modelo Relajado', realcost)
    return realcost



def test():
    fdem = 1
    step = 0.05
    wb = xl.Book('data_3_bus.xlsx')
    sh = xl.sheets['data']
    dem0 = sh.range('Q4:Q6').value
    
    for i in range(10):
        fact = (fdem+step*i)
        print(fact)
        # sh.range('Q4:Q6').options(transpose=True).value = [fact*i for i in dem0]
        # rcn =getModelNormalResults()
        # rcr =getModelRelaxResults()
        # print('Costos Reales Modelo Normal',rcn)
        # print('Costos Reales Modelo Relajado',rcr)

test()



def getCapacityStorage():
    pmaxbat= [0,0,0]
    pminbat= [0,0,0]
    
    qmaxbat=[0,0,0]
    qminbat=[0,0,0]
    
    
    for i in range(len(evalsipsbat)):
        data = evalsipsbat[i]
        for j in range(len(data)):
            pb = data[j,0]
            qb = data[j,1]
            #Max p
            if pb>pmaxbat[j]:
                pmaxbat[j] = pb
            if qb>qmaxbat[j]:
                qmaxbat[j] = qb
            #Min p
            if pb<pminbat[j]:
                pminbat[j] = pb
            if qb<qminbat[j]:
                qminbat[j] = qb
        
        
    
    print('Máxima potencia instalada baterías:',pmaxbat)
    print('Detalles')
    print('Qmax = ', qmaxbat)
    print('Pmax = ', pmaxbat)
    print('Qmin = ', qminbat)
    print('Pmin = ', pminbat)











#Simular todo
def optimizeeco():
    #Simulación Económica
    cost1 = mod.run() #caso full
    # cost2 = modrelax.relaxLine(1.2,1) #caso relajado
    cost2 = modrelax.relaxLine([1,2],[1.5,1.5])
    ahorrocosto = cost1-cost2
    print('Ahorro Costos:',ahorrocosto, 'USD')
    
# optimizeeco()


def evaluatesipsbattery(relax_vm=None, tolerance=1.1):
    optimizeeco()
    sm.simulateAll()
    #Seleccionar contingencias que producen sobrecarga de líneas nsl
    datacont = cont.getInstancesLineLimitsViolations(tolerance=tolerance)
    # datacont = [(23,4)]
    #SIPS 1: Baterias
    costsips = sipscreator.sipsbattery(datacont,relax_vm,print_results=True, verbose=True)
    print('Costos Operación SIPSBAT', costsips,'USD')
    evalsipsbat = np.load('results\\EVALSIPSBAT.npy') # (nsl,3,2)
    
    pmaxbat= [0,0,0]
    pminbat= [0,0,0]
    
    qmaxbat=[0,0,0]
    qminbat=[0,0,0]
    
    
    for i in range(len(evalsipsbat)):
        data = evalsipsbat[i]
        for j in range(len(data)):
            pb = data[j,0]
            qb = data[j,1]
            #Max p
            if pb>pmaxbat[j]:
                pmaxbat[j] = pb
            if qb>qmaxbat[j]:
                qmaxbat[j] = qb
            #Min p
            if pb<pminbat[j]:
                pminbat[j] = pb
            if qb<qminbat[j]:
                qminbat[j] = qb
        
        
    
    print('Máxima potencia instalada baterías:',pmaxbat)
    print('Detalles')
    print('Qmax = ', qmaxbat)
    print('Pmax = ', pmaxbat)
    print('Qmin = ', qminbat)
    print('Pmin = ', pminbat)

    


# x = cont.getInstancesLineLimitsViolations1()
# y = cont.getInstancesLineLimitsViolations2()
# z = cont.getInstancesLineLimitsViolations3()





# evaluatesipsbattery(relax_vm=[0.95, 1.05])




    
def evaluatesipsloadshedding(relax_vm=None, tolerance=1.1):
    datacont = cont.getInstancesLineLimitsViolations(tolerance=tolerance)
    costsips = sipscreator.sipsloadshedding(datacont,relax_vm,print_results=True, verbose=True)
    print('Costos Operación SIPSLOADSHEDDING', costsips,'USD')


def evaluatesipsbatteryloadshedding(relax_vm=None, tolerance=1.1):
    datacont = cont.getInstancesLineLimitsViolations1(tolerance=tolerance)
    costsips = sipscreator.sipsbatteryloadshedding(datacont,relax_vm,print_results=True, verbose=True)
    print('Costos Operación SIPSBATTERYLOADSHEDDING', costsips,'USD')

# evaluatesipsloadshedding(relax_vm=[0.95, 1.05],tolerance=1.1)
# evaluatesipsbattery(relax_vm=[0.85, 1.15], tolerance=1.3)
# evaluatesipsbatteryloadshedding(relax_vm=[0.95, 1.05], tolerance=1.1)



# #Medidas posibles:
# # Subir P mediante baterías                 -> storage                         SIPSBAT
# # Bajar D mediante load shedding            -> demand response                 SIPSLOADSHEDDING
# # Bajar P mediante Pmaxmod (<Pmax original) -> limitar inyección de generador  SIPSLIMITPMAX
# # Bajar P mediante Pminmod (<Pmin original) -> bracking resistor               SIPSBRACKINGRESISTOR

