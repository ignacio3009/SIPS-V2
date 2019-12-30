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
        pp.create_bus(net,vn_kv=220, index = i, max_vm_pu=1.1, min_vm_pu=0.9)
        
    cntidx = NUMNODES
    j=-1
    
    
    for i in range(numgen):
        barcon = GENDATA[i][1]
        if(barcon>j):
            j=j+1
            pp.create_bus(net, index = cntidx+j, vn_kv=13.8, max_vm_pu=1.1, min_vm_pu=0.9)
            
    # =========================================================================
    # CREATE GENERATORS
    # =========================================================================    
    j=-1
    
    for i in range(numgen):
        print('Pmax ',GENDATA[i][9])
        pp.create_gen(net, bus=GENDATA[i][1], p_mw = 0, sn_mva = GENDATA[i][13],
                      max_p_mw = GENDATA[i][9], min_p_mw = GENDATA[i][10],max_q_mvar=GENDATA[i][11], 
                      min_q_mvar=GENDATA[i][12], controllable=True)
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
    for i in range(3,6):
        pp.create_storage(net,  bus=i, p_mw = 0, q_mvar=0, max_e_mwh=100, max_p_mw = BATDATA[i-3][7], 
                          max_q_mvar=BATDATA[i-3][9], in_service=False)
        
    return net


def sipsbat():
    # simgen = np.load('results\\SIMGEN.npy')
    notconv = np.load('results\\SIMNOTCONV.npy') 
    
    
    
def testsipsbat(s,t):
    net = createnet()
    PGEN = np.load('results\\ECOPSOL.NPY')
    DEM = np.load('results\\ECODEM.npy')
    for i in range(3):
        net.gen['p_mw'][i] = PGEN[i,s,t]
        print('P ist',PGEN[i,s,t])
        
    for i in range(3):
        net.load['p_mw'][i] = DEM[i,t]
        # print('P ist',PGEN[i,s,t])
    if(s!=0):
        net.gen['slack'][0]=True
    else:
        net.gen['slack'][1]=False
        
    pp.runpp(net)    
    print(net.res_gen)
    
    
    
testsipsbat(6,0)
        
    
    
        
    
    
    







