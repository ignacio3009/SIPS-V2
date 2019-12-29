# -*- coding: utf-8 -*-
"""
Created on Sat Dec 28 18:11:43 2019

@author: ignac
"""

from simulation import*
import xlwings as xw
import numpy as np
import matplotlib.pyplot as plt

# filename_res = 'results.xlsx'

# wb = xw.Book(filename_res)
# sh = wb.sheets['Economicos']
# PGEN = np.array(sh.range('B2:H4').value)



# numele = 5
# numsce = 7
# numt = 24
# numbus = 6
# numline = 3
# numtrafo = 3
# numgen = 3
# numsto = 3

# M = numt*[numsce*[numele*[numbus*[4*[0]] ,numline*[14*[0]],numtrafo*[13*[0]],numgen*[4*[0]],numsto*[2*[0]]]]]
filename_data = 'data_3_bus.xlsx'
psol_eco = np.load('psol.npy')
M = solve(psol_eco,filename_data)

# plt.plot(M[:][][1][2])
# plt.plot(psol_eco[1,0,:]) #g,s,t