import xlwings as xw
import pandapower as pp

def createNet(filename_data):
    wbd = xw.Book(filename_data)
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
            pp.create_bus(net, index = cntidx+j, vn_kv=13.8, max_vm_pu=1.03, min_vm_pu=0.97)
            
    # =========================================================================
    # CREATE GENERATORS
    # =========================================================================    
    j=-1
    for i in range(numgen):
        pp.create_gen(net, bus=GENDATA[i][1], p_mw = 0, sn_mva = GENDATA[i][13],
                      max_p_mw = GENDATA[i][9], min_p_mw = GENDATA[i][10],max_q_mvar=GENDATA[i][11], 
                      min_q_mvar=GENDATA[i][12], controllable=False)
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
    for i in range(3,5):
        pp.create_storage(net,  bus=i, p_mw = 0, q_mvar=0, max_e_mwh=100, in_service=False)
        
    return net





# =============================================================================
# TAKE RESULTS AND SIMULATE
# =============================================================================
def solve(PGEN, filename_data,include_bat=False):

    numele = 5
    numSce = 7
    numHrs = 24
    numbus = 6
    numline = 3
    numtrafo = 3
    numgen = 3
    numsto = 3
    
    M = numHrs*[numSce*[numele*[numbus*[4*[0]] ,numline*[14*[0]],numtrafo*[13*[0]],numgen*[4*[0]],numsto*[2*[0]]]]]
    net = createNet(filename_data)
    for t in range(numHrs):
        for s in range(numSce):
            for i in range(3):
                net.gen['in_service']=True
                net.line['in_service']=True
            # print('Simulating Scenario '+str(s)+'. Please wait...')
            for i in range(3):
                net.gen['p_mw'][i] = PGEN[i,s,t]
                
            if (0<s and s<=3):
                net.gen['in_service'][s-1]=False
            elif(s>3):
                net.line['in_service'][s-4]=False
            
            if s==1:
                net.gen['slack'][0]=False
                net.gen['slack'][1]=True
            
            else:
                net.gen['slack'][0]=True
                net.gen['slack'][1]=False
            # print(net.gen['slack'])
            # print(net.gen['in_service'])
                
            #Run power flow
            pp.runpp(net)    
            
            #Save Results
            M[t][s][0] = net.res_bus
            M[t][s][1] = net.res_line
            M[t][s][2] = net.res_trafo
            M[t][s][3] = net.res_gen
            M[t][s][4] = net.res_storage
            
            # M[t][s][0] = net.res_bus.values.tolist()
            # M[t][s][1] = net.res_line.values.tolist()
            # M[t][s][2] = net.res_trafo.values.tolist()
            # M[t][s][3] = net.res_gen.values.tolist()
            # M[t][s][4] = net.res_storage.values.tolist()
            

    return M
    # print('End Simulations!')
    