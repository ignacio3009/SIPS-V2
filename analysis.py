# -*- coding: utf-8 -*-
"""
Created on Sun Dec 29 18:00:45 2019

@author: ignac
"""


import numpy as np
import xlwings as xw
import matplotlib.pyplot as plt

wbd = xw.Book('data_3_bus.xlsx')
sd = wbd.sheets['data']

GENDATA = sd.range('A4:N6').value
DEMDATA = sd.range('P4:R6').value
LINDATA = sd.range('T4:Z6').value
BATDATA = sd.range('AB4:AM6').value

# PGEN = np.load('results\\ECOPSOL.npy') 
# DEM =  np.load('results\\ECODEM.npy') 
# NGen = 3
# NHrs = 24
# numGen = range(NGen)
# numHrs = range(NHrs)

# pgen = []
# dem = []
# scen = 6
# for t in numHrs:
#     totalpgenhour = sum(PGEN[:,scen,t])
#     pgen.append(totalpgenhour)
#     totaldemhour = sum(DEM[:,t])
#     dem.append(totaldemhour)

# plt.plot(pgen,  label='Generation')
# plt.plot(dem, label = 'Demand')
# plt.title('Demand and Generation Scenario '+str(scen))
# plt.ylabel('[MW]')
# plt.xlabel('Hour')
# plt.legend()

# notconv = np.load('results\\SIMNOTCONV.npy') 
# # PGEN = np.load('results\\ECOPSOL.npy') 
# # DEM =  np.load('results\\ECODEM.npy') 
simgen = np.load('results\\SIMGEN.npy')
# x = notconv[0]
# s=x[0]
# t=x[1]
# print(notconv)
# # print(simgen)
print(simgen[0,2,0,:])


#Medidas posibles:
# Subir P mediante baterías                 -> storage                         SIPSBAT
# Bajar D mediante load shedding            -> demand response                 SIPSLOADSHEDDING
# Bajar P mediante Pmaxmod (<Pmax original) -> limitar inyección de generador  SIPSLIMITPMAX
# Bajar P mediante Pminmod (<Pmin original) -> bracking resistor               SIPSBRACKINGRESISTOR

