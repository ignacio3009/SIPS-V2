# -*- coding: utf-8 -*-
"""
Created on Mon Dec 30 12:53:32 2019

@author: ignac
"""

import numpy as np

def getLineLimitsViolations1(line, tolerance):
    """
    Entrega las instancias de violacion de límites de capacidad de transferencia en las líneas sobre 110%.
    Devuelve una lista con tuplas (t,s,loading)
    """
    simlin = np.load('results\\SIMLIN.npy') 
    instances = []
    NHrs =  24
    NSce =  7
    line_loading_column = 13
    cnt =   0
    for s in range(NSce):
        for t in range(NHrs):
            if(simlin[t,s,line,line_loading_column]>tolerance*100):
                cnt=cnt+1
                instances.append((t,s,simlin[t,s,line,line_loading_column]))
    return instances


def getLineLimitsViolations2(line, tolerance):
    """
    Entrega las instancias de violacion de límites de capacidad de transferencia en las líneas sobre 110%.
    Devuelve una lista con tuplas (t,s,loading)
    """
    simlin = np.load('results\\SIMLIN.npy') 
    instances = []
    NHrs =  24
    NSce =  7
    line_loading_column = 13
    cnt =   0
    for s in range(NSce):
        for t in range(NHrs):
            if(simlin[t,s,line,line_loading_column]>90 and simlin[t,s,line,line_loading_column]<tolerance*100):
                cnt=cnt+1
                instances.append((t,s,simlin[t,s,line,line_loading_column]))
    return instances

def getInstancesLineLimitsViolations2(tolerance=1.1):
    """
    Entrega las instancias de violacion de límites de capacidad de transferencia en las líneas desde 100% a 110%.
    Devuelve una lista con tuplas (t,s,loading)
    """
    NLin = 3
    numLin = range(NLin)
    #filtrar contingencias que se repiten
    datacontaux = []
    for l in numLin:
        x = getLineLimitsViolations2(l,tolerance)
        for i in x:
            datacontaux.append((i[0],i[1]))
    return list(set(datacontaux))


def getLineLimitsViolations3(line, tolerance):
    """
    Entrega las instancias de violacion de límites de capacidad de transferencia en las líneas bajo 110%.
    Devuelve una lista con tuplas (t,s,loading)
    """
    simlin = np.load('results\\SIMLIN.npy') 
    instances = []
    NHrs =  24
    NSce =  7
    line_loading_column = 13
    cnt =   0
    for s in range(NSce):
        for t in range(NHrs):
            if(simlin[t,s,line,line_loading_column]<90):
                cnt=cnt+1
                instances.append((t,s,simlin[t,s,line,line_loading_column]))
    return instances

def getInstancesLineLimitsViolations3(tolerance=1.1):
    """
    Entrega las instancias de violacion de límites de capacidad de transferencia en las líneas bajo 100%.
    Devuelve una lista con tuplas (t,s,loading)
    """
    NLin = 3
    numLin = range(NLin)
    #filtrar contingencias que se repiten
    datacontaux = []
    for l in numLin:
        x = getLineLimitsViolations3(l,tolerance)
        for i in x:
            datacontaux.append((i[0],i[1]))
    return list(set(datacontaux))

def getInstancesLineLimitsViolations1(tolerance=1.1):
    """
    Entrega lista con pares ordenados (t,s) de momentos donde se violan límites de capacidad de líneas.
    """
    NLin = 3
    numLin = range(NLin)
    #filtrar contingencias que se repiten
    datacontaux = []
    for l in numLin:
        x = getLineLimitsViolations1(l,tolerance)
        for i in x:
            datacontaux.append((i[0],i[1]))
    return list(set(datacontaux))


