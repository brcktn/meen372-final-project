from model import *
from scipy.optimize import minimize 

"""
x[0]: length_diagonal (float, inches)
x[1]: cross_section_height (float, inches)
x[2]: cross_section_width (float, inches)
x[3]: material_thickness (float, inches)
x[4]: crossbar_diameter (float, inches)
x[5]: hole_offset (float, inches)
x[6]: start_height (float, inches)
"""

def obj(x):
    return calc_cost(x[0],x[1],x[2],x[3],x[4],x[5],x[6],x[7],x[8],[9],[10])


def con1(x): #buckling constraint
    P_cr = calc_critical_buckling_load()
    F_d = calc_diagonal_force()
    n_buckling = P_cr / F_d
    return n_buckling - 3

def con2(x): #tensile contraint
    return None
def con3(x): #tearout constrait
    return None
def con4(x):
    return None
    

if __name__ == '__main__':
    
    cons = []
    x0 = []
    bounds = []

    minimize(calc_cost, x0, bounds=bounds, constraints=cons)