from model import *
from scipy.optimize import minimize 

"""
x[0]: length_diagonal
x[1]: cross_section_height
x[2]: cross_section_width
x[3]: material_thickness
x[4]: crossbar_diameter
x[5]: hole_offset
x[6]: start_height
"""


def obj():
    pass




if __name__ == '__main__':
    cons = []
    x0 = []
    bounds = []
    
    minimize(obj, x0, bounds=bounds, constraints=cons)