# -*- coding: utf-8 -*-
"""
Created on Mon Dec 30 21:32:59 2019

@author: ignac
"""


import xlwings as xw
import numpy as np

def  loadsystemdata(filename='data_3_bus.xlsx'):
    """
    Returns GENDATA, DEMDATA, LINDATA, STODATA
    """
    range_gen = 'A4:N6'
    range_dem = 'P4:U6'
    range_lin = 'W4:AC6'
    range_sto = 'AE4:AP6'
    wb = xw.Book(filename)
    sh = wb.sheets['data']
    GENDATA =   np.array(sh.range(range_gen).value)
    DEMDATA =   np.array(sh.range(range_dem).value)
    LINDATA =   np.array(sh.range(range_lin).value)
    STODATA =   np.array(sh.range(range_sto).value)
    
    return GENDATA,DEMDATA,LINDATA,STODATA
    

def loadscendata(filename='data_3_bus.xlsx'):
    """
    Returns A,B,PROB
    """
    wb = xw.Book(filename)
    sh = wb.sheets['data']
    range_A = 'AS4:AY6'
    range_B = 'AS6:AY9'
    range_prob = 'AZ4:AZ9'
    A =  np.array(sh.range(range_A).value)
    B =  np.array(sh.range(range_B).value)
    PROB = np.array(sh.range(range_prob).value)
    
    return A, B, PROB

def loadcurvedata(filename='data_3_bus.xlsx'):
    """
    Returns load curve data
    """
    wb = xw.Book(filename)
    shlc = wb.sheets['loadcurve']
    range_demres = 'B2:B25'
    range_demind = 'C2:C25'
    range_demcom = 'D2:D25'
    DEMRES = np.array(shlc.range(range_demres).value)
    DEMIND = np.array(shlc.range(range_demind).value)
    DEMCOM = np.array(shlc.range(range_demcom).value)
    
    return DEMRES, DEMIND, DEMCOM