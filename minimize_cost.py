from model import *
from scipy.optimize import minimize

def obj():
    pass




if __name__ == '__main__':
    cons = []
    x0 = []
    bounds = []
    
    minimize(obj, x0, bounds=bounds, constraints=cons)