# # -*- coding: utf-8 -*-
# """
# Created on Sun Dec 29 18:00:45 2019

# @author: ignac
# """

import model as mod
import modelrelax as modrelax
import contingencies as cont
import sipscreator as sipscreator
import simulation as sm
import numpy as np



#Simular todo
def optimizeeco():
    #Simulación Económica
    cost1 = mod.run() #caso full
    # cost2 = modrelax.relaxLine(1.2,1) #caso relajado
    cost2 = modrelax.relaxLine([1,2],[1.2,1.2])
    ahorrocosto = cost1-cost2
    print('Ahorro Costos:',ahorrocosto, 'USD')
    



def evaluatesipsbattery(relax_vm=None, tolerance=1.3):
    # optimizeeco()
    # sm.simulateAll()
    #Seleccionar contingencias que producen sobrecarga de líneas nsl
    datacont = cont.getInstancesLineLimitsViolations(tolerance=tolerance)
    # datacont = [(23,4)]
    #SIPS 1: Baterias
    costsipsbat = sipscreator.sipsbattery(datacont,relax_vm,print_results=True, verbose=True)
    print('Costos Operación SIPSBAT', costsipsbat,'USD')
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

    




evaluatesipsbattery(relax_vm=[0.85, 1.15])
# datacont = cont.getInstancesLineLimitsViolations(tolerance=1.3)
# cost = sipscreator.sipsloadshedding(datacont,print_results=True,verbose=True)
# #SIPS 1: Baterias
# costsipsbat = sipscreator.sipsloadshedding(datacont,print_results=True,verbose=True)



# datacont = cont.getInstancesLineLimitsViolations(tolerance=1.3)
# print('Number of points out of limits:',len(datacont),'/',24*7)








# import numpy as np
# import xlwings as xw
# import matplotlib.pyplot as plt

# wbd = xw.Book('data_3_bus.xlsx')
# sd = wbd.sheets['data']

# GENDATA = sd.range('A4:N6').value
# DEMDATA = sd.range('P4:R6').value
# LINDATA = sd.range('T4:Z6').value
# BATDATA = sd.range('AB4:AM6').value

# # PGEN = np.load('results\\ECOPSOL.npy') 
# # DEM =  np.load('results\\ECODEM.npy') 
# # NGen = 3
# # NHrs = 24
# # numGen = range(NGen)
# # numHrs = range(NHrs)

# # pgen = []
# # dem = []
# # scen = 6
# # for t in numHrs:
# #     totalpgenhour = sum(PGEN[:,scen,t])
# #     pgen.append(totalpgenhour)
# #     totaldemhour = sum(DEM[:,t])
# #     dem.append(totaldemhour)

# # plt.plot(pgen,  label='Generation')
# # plt.plot(dem, label = 'Demand')
# # plt.title('Demand and Generation Scenario '+str(scen))
# # plt.ylabel('[MW]')
# # plt.xlabel('Hour')
# # plt.legend()

# # notconv = np.load('results\\SIMNOTCONV.npy') 
# # # PGEN = np.load('results\\ECOPSOL.npy') 
# # # DEM =  np.load('results\\ECODEM.npy') 
# simgen = np.load('results\\SIMGEN.npy')
# # x = notconv[0]
# # s=x[0]
# # t=x[1]
# # print(notconv)
# # # print(simgen)
# print(simgen[0,2,0,:])


# #Medidas posibles:
# # Subir P mediante baterías                 -> storage                         SIPSBAT
# # Bajar D mediante load shedding            -> demand response                 SIPSLOADSHEDDING
# # Bajar P mediante Pmaxmod (<Pmax original) -> limitar inyección de generador  SIPSLIMITPMAX
# # Bajar P mediante Pminmod (<Pmin original) -> bracking resistor               SIPSBRACKINGRESISTOR

