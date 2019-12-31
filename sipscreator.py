import pandapower as pp
import numpy as np
import simulation as sm
import loaddata as ld

# =============================================================================
# CONFIG NET 
# =============================================================================
    
    
def confignet(net,t,s,PGEN,DEM,XSOL,GENDATA):
    numBar=3
    numGen=3
    RUPMAX =    GENDATA[:,7]
    RDOWNMAX =  GENDATA[:,8]
    PMAX =      GENDATA[:,9]
    PMIN =      GENDATA[:,10]
    
    for i in range(numGen):
        net.gen['p_mw'][i]=PGEN[i,0,t]
        net.gen['max_p_mw'][i]=XSOL[i,t]*(min(PGEN[i,0,t]+RUPMAX[i],PMAX[i]))
        net.gen['min_p_mw'][i]=XSOL[i,t]*(max(PGEN[i,0,t]-RDOWNMAX[i],0))
        net.gen['controllable'][i]=(XSOL[i,t]==1)
    for i in range(numBar):
        net.load['p_mw'][i]=DEM[i,t]
    #set element out of service
    for i in range(numGen):
        net.gen['in_service'][i]=(XSOL[i,t]==1)
        net.line['in_service'][i]=True
        net.load['in_service'][i]=True
    if (0<s and s<=3):
        net.gen['in_service'][s-1]=False
    elif(s>3):
        net.line['in_service'][s-4]=False
    
    #set
    # for i in range(numBar):
        # pgi = PGEN[i,0,t]
        # demi = DEM[i,t]
        # # rupi = RUP[i,s,t]
        # # rdowni = RDOWN[i,s,t]
        # # pgi0 = PGEN[i,0,t]
        # deltapgendem = pgi-demi
        # if(deltapgendem>0):
        #     #Set generators pgen = pgi-demi
        #     net.gen['in_service'][i]=True
        #     net.gen['max_p_mw'][i]=deltapgendem
        #     net.gen['min_p_mw'][i]=deltapgendem
        #     net.gen['controllable'][i]=True
        #     net.gen['slack'][i]=True
        #     #Set loads out of service
        #     net.load['in_service'] = False
        # else:
        #      #Set new load pdem = demi-pgi
        #      net.load['p_mw'][i] = -1*deltapgendem
        #      #Set generator out of service
        #      net.gen['in_service'][i]=False
    
    return net


# =============================================================================
# BATTERY SIPS
# =============================================================================

def evalsipsbattery(net,t,s,PGEN,DEM,XSOL,GENDATA,print_results=False):
    print('PGEN:',PGEN[:,0,t])
    print('DEM:',DEM[:,t ])
    net = confignet(net,t,s,PGEN,DEM,XSOL,GENDATA)
    numGen = 3
    INF = 1e32
    
    geninservice = False
    for i in range(numGen):
        if (net.gen['in_service'][i]):
            geninservice=True
            net.gen['slack'][i] = True
            break
    
    #Define slack bus
    if not geninservice:
        net.storage['slack'][0]=True
        
    #Run Optimal Power Flow
    net.trafo['max_loading_percent']=100
    net.line['max_loading_percent'] =100
    try:
        pp.runopp(net)
        if print_results:
            print('Results Storage')
            print(net.res_storage)
            print('Results Generators')
            print(net.res_gen)
        return net.res_cost, net.res_storage.values
    except:
        print('OPF not converges')
        print('Pgen:', PGEN[:,0,t])
        print('Dem:',DEM[:,t])
        return INF, np.ndarray((3,2))
    

      
def sipsbattery(datacont, print_results=False, verbose=False):
    net = sm.createnet(include_bat=True)
    GENDATA = ld.loadgendata()
    XSOL = np.load('results\\ECOXSOL.npy')
    print('Simulating scenarios with overloading lines and proposing corrective actions with batteries. This may take some time...')
    totalcost = 0
    #Create function costs:
   
    PGEN = np.load('results\\ECOPSOL.NPY') #(g,s,t)
    DEM = np.load('results\\ECODEM.npy') #(i,t)
    
    if(verbose): 
        print('Evaluating Battery SIPS')
    numcases = len(datacont)
    EVALSIPSBAT = np.ndarray((numcases,3,2))
    for i in range(len(datacont)):
        t = datacont[i][0]
        s = datacont[i][1]
        if(verbose):
            print('------------------------')
            print('Case:',i+1,'/',numcases)
            print('Scenario:',s)
            print('Hour:',t)
        cost,EVALSIPSBAT[i] = evalsipsbattery(net,t,s,PGEN,DEM,XSOL,GENDATA,print_results=print_results)
        totalcost = totalcost+cost
    np.save('results\\EVALSIPSBAT',EVALSIPSBAT)
    if(print_results):
        print('------------------------')
        print('Costos Totales:',totalcost)
    return totalcost
    
    
    
# =============================================================================
# LOAD SHEDDING SIPS
# =============================================================================

    

def evalsipsloadshedding(net,t,s,PGEN,DEM,print_results=False):
    net = confignet(net,t,s,PGEN,DEM)
    MINCOST=0
    numGen = 3
    for i in range(numGen):
        pp.create_poly_cost(net, i ,'gen', cp1_eur_per_mw=MINCOST)
    numGen = 3
    INF = 1e32
    
    geninservice = False
    for i in range(numGen):
        if (net.gen['in_service'][i]):
            geninservice=True
            net.gen['slack'][i] = True
            break
    
    #Define slack bus
    if not geninservice:
        net.gen['slack'][0] = True
        net.gen['p_mw'][0] = PGEN[0,0,t]
        net.gen['max_p_mw'] = PGEN[0,0,t]
        net.gen['min_p_mw'] = PGEN[0,0,t]
        
        
    #Run Optimal Power Flow
    net.trafo['max_loading_percent']=100
    net.line['max_loading_percent'] =100
    try:
        pp.runopp(net)
        if print_results:
            print('Results Load Shedding:')
            print(net.res_load)
            print('Results Generators')
            print(net.res_gen)
        return net.res_cost, net.res_load.values
    except:
        print('OPF not converges')
        print('Pgen:', PGEN[:,s,t])
        print('Dem:',DEM[:,t])
        return INF, np.ndarray((3,2))


def sipsloadshedding(datacont, print_results=False, verbose=False):
    net = sm.createnet(include_load_shedding=True)
    print('Simulating scenarios with overloading lines and proposing corrective actions with load shedding. This may take some time...')
    totalcost = 0
    #Create function costs:
   
    PGEN = np.load('results\\ECOPSOL.NPY') #(g,s,t)
    DEM = np.load('results\\ECODEM.npy') #(i,t)
    
    if(verbose): 
        print('Evaluating Loading Shedding SIPS')
    numcases = len(datacont)
    EVALSIPSLOADSHEDDING = np.ndarray((numcases,3,2))
    for i in range(len(datacont)):
        t = datacont[i][0]
        s = datacont[i][1]
        if(verbose):
            print('------------------------')
            print('Case:',i+1,'/',numcases)
            print('Scenario:',s)
            print('Hour:',t)
        cost,EVALSIPSLOADSHEDDING[i] = evalsipsloadshedding(net,t,s,PGEN,DEM)
        totalcost = totalcost+cost
    np.save('results\\EVALSIPSLOADSHEDDING',EVALSIPSLOADSHEDDING)
    if(print_results):
        print('------------------------')
        print('Costos Totales:',totalcost)
    return totalcost