# -*- coding: utf-8 -*-
"""
Created on Mon Dec 30 13:52:23 2019

@author: ignac
"""

import pandapower as pp
import numpy as np
net = pp.create_empty_network()

#create buses
bus1 = pp.create_bus(net, vn_kv=220.)
bus2 = pp.create_bus(net, vn_kv=110.)
bus3 = pp.create_bus(net, vn_kv=110.)
bus4 = pp.create_bus(net, vn_kv=110.)

#create 220/110 kV transformer
pp.create_transformer(net, bus1, bus2, std_type="100 MVA 220/110 kV")

#create 110 kV lines
pp.create_line(net, bus2, bus3, length_km=70., std_type='149-AL1/24-ST1A 110.0')
pp.create_line(net, bus3, bus4, length_km=50., std_type='149-AL1/24-ST1A 110.0')
pp.create_line(net, bus4, bus2, length_km=40., std_type='149-AL1/24-ST1A 110.0')

#create loads
load1 = pp.create_load(net, bus2, p_mw=60, min_p_mw= 30, max_p_mw =60, min_q_mvar= 0, max_q_mvar = 10, controllable=True)
load2 = pp.create_load(net, bus3, p_mw=70, controllable=False)
load3 = pp.create_load(net, bus4, p_mw=10, controllable=False)

#create generators
eg = pp.create_ext_grid(net, bus1, min_p_mw=-1000, max_p_mw=1000)
g0 = pp.create_gen(net, bus3, p_mw=80, min_p_mw=0, max_p_mw=80,  vm_pu=1.01, controllable=True)
g1 = pp.create_gen(net, bus4, p_mw=100, min_p_mw=0, max_p_mw=100, vm_pu=1.01, controllable=True)

costeg = pp.create_poly_cost(net, 0, 'ext_grid', cp1_eur_per_mw=10)
costgen1 = pp.create_poly_cost(net, 0, 'gen', cp1_eur_per_mw=15)
costgen2 = pp.create_poly_cost(net, 1, 'gen', cp1_eur_per_mw=12)

# net.load['p_mw'][0]=100
costload1 = pp.create_poly_cost(net, load1, 'load', cp1_eur_per_mw = 1)



pp.runopp(net)

print(net.res_ext_grid)