from model import *
from scipy.optimize import minimize 

    
def obj(x):
    return calc_cost(x[0],x[1],x[2],x[3],x[4],x[5],x[6],x[7],x[8],[9],[10])


def con1(x):
    P_cr = calc_critical_buckling_load()
    F_d = calc_diagonal_force()
    n_buckling = P_cr / F_d
    return n_buckling - 3



if __name__ == '__main__':
    
    cons = []
    x0 = []
    bounds = []

    minimize(calc_cost, x0, bounds=bounds, constraints=cons)