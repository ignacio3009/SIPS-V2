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

    




evaluatesipsbattery(relax_vm=[0.95, 1.05])




    
def evaluatesipsloadshedding(relax_vm=None, tolerance=1.1):
    datacont = cont.getInstancesLineLimitsViolations(tolerance=tolerance)
    costsips = sipscreator.sipsloadshedding(datacont,relax_vm,print_results=True, verbose=True)
    print('Costos Operación SIPSLOADSHEDDING', costsips,'USD')


def evaluatesipsbatteryloadshedding(relax_vm=None, tolerance=1.1):
    datacont = cont.getInstancesLineLimitsViolations(tolerance=tolerance)
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

