import pandapower as pp
import numpy as np
import loaddata as ld

def createnet(include_load_shedding=False, include_bat=False):
    GENDATA,DEMDATA,LINDATA,STODATA = ld.loadsystemdata()
    NUMNODES = 3

    numgen = len(GENDATA)
    numlin = len(LINDATA)
    numdem = len(DEMDATA)
    numsto = len(STODATA)
    
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
        pp.create_gen(net, vm_pu=1.02, index=indexgen, bus=GENDATA[i][1], p_mw = 0, sn_mva = GENDATA[i][13],
                      max_p_mw = GENDATA[i][9], min_p_mw = GENDATA[i][10],max_q_mvar=GENDATA[i][11], 
                      min_q_mvar=GENDATA[i][12], controllable=True)
        indexgen = indexgen + 1
        #create trafos     
        barcon = GENDATA[i][1]
        if(barcon>j):
            j=j+1
        pp.create_transformer(net, hv_bus=GENDATA[i][1], lv_bus=cntidx+j, std_type="500 MVA 220/13.8 kV")
             
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
        pp.create_load(net, index=i, bus=DEMDATA[i][0], p_mw = DEMDATA[i][1], q_mvar=DEMDATA[i][2],
                       max_p_mw = DEMDATA[i][1], min_p_mw=DEMDATA[i][1], 
                       max_q_mvar = DEMDATA[i][2], min_q_mvar=DEMDATA[i][5],
                       controllable = include_load_shedding)
        pp.create_poly_cost(net,i,'load',cp1_eur_per_mw=DEMDATA[i][3])
        
    # =========================================================================
    # CREATE STORAGE
    # =========================================================================
    for i in range(numsto):
        pp.create_storage(net, index=i, bus=NUMNODES + i, p_mw = 0, q_mvar=0, max_e_mwh=100000, 
                          max_p_mw = STODATA[i][7], min_p_mw=STODATA[i][8], max_q_mvar=STODATA[i][9],
                          min_q_mvar= STODATA[i][10], in_service=include_bat, controllable=include_bat)
        pp.create_poly_cost(net,i,'storage',cp1_eur_per_mw=STODATA[i][2])
        
    return net





# =============================================================================
# TAKE RESULTS AND SIMULATE 
# =============================================================================
def simulateAll():
    print('Run power flow all scenarios for each hour')
    PGEN = np.load('results\\ECOPSOL.npy')   
    DEM = np.load('results\\ECODEM.npy')
    NHrs = 24
    NSce = 7
    SIMBUS = np.ndarray((NHrs,NSce,6,4))
    SIMLIN = np.ndarray((NHrs,NSce,3,14))
    SIMTRF = np.ndarray((NHrs,NSce,3,13))
    SIMGEN = np.ndarray((NHrs,NSce,3,4))
    SIMSTO = np.ndarray((NHrs,NSce,3,2))
    
    net = createnet()
    num_not_convergence = 0
    not_convergence_data = [] #(s,t) scen,hour (
    for t in range(NHrs):
        print('Simulating Hour ',t+1,'/ 24 ...')
        for s in range(NSce):
            #reset availability of elements
            for i in range(3):
                net.gen['in_service']=True
                net.line['in_service']=True
            #set demand of generators
            for i in range(3):
                net.gen['p_mw'][i] = PGEN[i,s,t]
            #set demand
            for i in range(3):
                net.load['p_mw'][i] = DEM[i,t]
            #set unavailable element generator or line
            if (0<s and s<=3):
                net.gen['in_service'][s-1]=False
            elif(s>3):
                net.line['in_service'][s-4]=False
            #set slack bus
            if s==1:
                net.gen['slack'][0]=False
                net.gen['slack'][1]=True
            
            else:
                net.gen['slack'][0]=True
                net.gen['slack'][1]=False
                
            #Run power flow
            try:
                pp.runpp(net,max_iteration=20, enforce_q_lims=True)  
                #Save results into file
                SIMBUS[t,s] = net.res_bus.values
                SIMLIN[t,s] = net.res_line.values
                SIMTRF[t,s] = net.res_trafo.values
                SIMGEN[t,s] = net.res_gen.values
                SIMSTO[t,s] = net.res_storage.values
            except:
                print('Power Flow did not converge:')
                print('Hour:',t)
                print('Scenario:',s)
                print('Data gen:')
                print(PGEN[:,s,t])
                num_not_convergence = num_not_convergence + 1
                not_convergence_data.append((s,t))
            
            
            
          
    SIMNOTCONV = np.array(not_convergence_data)        
    np.save('results\\SIMBUS',SIMBUS)
    np.save('results\\SIMLIN',SIMLIN)
    np.save('results\\SIMTRF',SIMTRF)
    np.save('results\\SIMGEN',SIMGEN)
    np.save('results\\SIMSTO',SIMSTO)
    np.save('results\\SIMNOTCONV',SIMNOTCONV)
    print('End Simulations!')
    print('Number of not convergence:',num_not_convergence)

if __name__ == '__main__':
    simulateAll()