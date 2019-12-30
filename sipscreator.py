import xlwings as xw
import pandapower as pp
import numpy as np

def createnet(include_bat=False):
    wbd = xw.Book('data_3_bus.xlsx')
    sd = wbd.sheets['data']
    
    GENDATA = sd.range('A4:N6').value
    DEMDATA = sd.range('P4:R6').value
    LINDATA = sd.range('T4:Z6').value
    BATDATA = sd.range('AB4:AM6').value
    NUMNODES = 3

    numgen = len(GENDATA)
    numlin = len(LINDATA)
    numdem = len(DEMDATA)
    
    # =========================================================================
    # CREATE EMPTY NET
    # =========================================================================
    
    net = pp.create_empty_network(f_hz=50.0, sn_mva=100)
    
    # =========================================================================
    # CREATE BUSES
    # =========================================================================
    for i in range(numgen):
        pp.create_bus(net,vn_kv=220, index = i, max_vm_pu=1.05, min_vm_pu=0.95)
        
    cntidx = NUMNODES
    j=-1
    
    
    for i in range(numgen):
        barcon = GENDATA[i][1]
        if(barcon>j):
            j=j+1
            pp.create_bus(net, index = cntidx+j, vn_kv=13.8, max_vm_pu=1.05, min_vm_pu=0.95)
            
    # =========================================================================
    # CREATE GENERATORS
    # =========================================================================    
    j=-1
    indexgen=0
    for i in range(numgen):
        pp.create_gen(net, index=indexgen, bus=GENDATA[i][1], p_mw = 0, sn_mva = GENDATA[i][13],
                      max_p_mw = GENDATA[i][9], min_p_mw = GENDATA[i][10],max_q_mvar=GENDATA[i][11], 
                      min_q_mvar=GENDATA[i][12], controllable=True)
        indexgen = indexgen + 1
        #create trafos     
        barcon = GENDATA[i][1]
        if(barcon>j):
            j=j+1
        pp.create_transformer(net, hv_bus=GENDATA[i][1], lv_bus=cntidx+j, std_type="250 MVA 220/13.8 kV")
             
    # =========================================================================
    # CREATE LINES
    # =========================================================================
    for i in range(numlin):
        fmax = LINDATA[i][1]/(3**0.5*220)
        ltype = {'typ'+str(i):{"r_ohm_per_km": LINDATA[i][5], "x_ohm_per_km": LINDATA[i][4], "c_nf_per_km": 10, "max_i_ka": fmax, "type": "ol", "qmm2":490, "alpha":4.03e-3}}
        pp.create_std_types(net,data=ltype,element='line')
        
        pp.create_line(net, from_bus=LINDATA[i][2], to_bus=LINDATA[i][3], length_km=LINDATA[i][6], std_type="typ"+str(i))
        
        
    # =========================================================================
    # CREATE LOADS
    # =========================================================================
    for i in range(numdem):
        pp.create_load(net,  bus=DEMDATA[i][0], p_mw = DEMDATA[i][1], q_mvar=DEMDATA[i][2])

        
    # =========================================================================
    # CREATE STORAGE
    # =========================================================================
    indexsto = 0
    for i in range(3,6):
        pp.create_storage(net, index=indexsto, bus=i, p_mw = 0, q_mvar=0, max_e_mwh=1000, 
                          max_p_mw = BATDATA[i-3][7], min_p_mw=BATDATA[i-3][8], max_q_mvar=BATDATA[i-3][9],
                          min_q_mvar= BATDATA[i-3][10], in_service=include_bat, controllable=include_bat)
        indexsto = indexsto + 1
        
    return net

    
    
    
    

def evalsipsbattery(t,s,net,PGEN,DEM,print_results=False):
    
    #Economical results data
    # PGEN = np.load('results\\ECOPSOL.NPY') #(g,s,t)
    # DEM = np.load('results\\ECODEM.npy') #(i,t)
    # RUP = np.load('results\\ECORUPSOL.npy') #(g,s,t)
    # RDOWN = np.load('results\\ECORDOWNSOL.npy') #(g,s,t)
    numBar=3
    geninservice=False
    INF= 1000000000
    
    for i in range(numBar):
        pgi = PGEN[i,s,t]
        demi = DEM[i,t]
        # rupi = RUP[i,s,t]
        # rdowni = RDOWN[i,s,t]
        # pgi0 = PGEN[i,0,t]
        deltapgendem = pgi-demi
        if(deltapgendem>0):
            #Set generators pgen = pgi-demi
            net.gen['in_service'][i]=True
            net.gen['max_p_mw'][i]=deltapgendem
            net.gen['min_p_mw'][i]=deltapgendem
            net.gen['controllable'][i]=True
            net.gen['slack'][i]=True
            geninservice = True
            #Set loads out of service
            net.load['in_service'] = False
        else:
             #Set new load pdem = demi-pgi
             net.load['p_mw'][i] = -1*deltapgendem
             #Set generator out of service
             net.gen['in_service'][i]=False
    
        
    #Define slack bus
    if not geninservice:
        net.storage['slack'][0]=True
    #Run Optimal Power Flow
    net.trafo['max_loading_percent']=100
    net.line['max_loading_percent'] =100
    try:
        pp.runopp(net)
        if print_results:
            print('Results Storage:')
            print(net.res_storage)
            print('Results Generators')
            print(net.res_gen)
        return net.res_cost, net.res_storage.values
    except:
        print('OPF not converges')
        print('Pgen:', PGEN[:,s,t])
        print('Dem:',DEM[:,t])
        return INF, np.ndarray((3,2))
    

      
def sipsbattery(datacont, print_results=False, verbose=False):
    net = createnet(include_bat=True)
    wbd = xw.Book('data_3_bus.xlsx')
    sd = wbd.sheets['data']
    BATDATA = sd.range('AB4:AM6').value
    numGen = 3
    numBar = 3
    MINCOST = 0
    totalcost = 0
    #Create function costs:
    for i in range(numGen):
        pp.create_poly_cost(net, i ,'gen', cp1_eur_per_mw=MINCOST)
    for i in range(numBar):
        pp.create_poly_cost(net, i,'storage', cp1_eur_per_mw=BATDATA[i][2])
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
        cost,EVALSIPSBAT[i] = evalsipsbattery(t,s,net,PGEN,DEM)
        totalcost = totalcost+cost
    np.save('results\\EVALSIPSBAT',EVALSIPSBAT)
    if(print_results):
        print('------------------------')
        print('Costos Totales:',totalcost)
    return totalcost
    
    
        

    
    







