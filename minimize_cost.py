from model import *
from scipy.optimize import minimize
from numpy import sin, cos, tan, pi

"""
x[0]: length_diagonal (float, inches)
x[1]: cross_section_height (float, inches)
x[2]: cross_section_width (float, inches)
x[3]: material_thickness (float, inches)
x[4]: crossbar_diameter (float, inches)
x[5]: hole_offset (float, inches)
x[6]: start_height (float, inches)
"""

# Constants
HEIGHT_LIFTED = 6.0  # inches
HOLE_DIAMETER = 0.5  # inches
FORCE = 3000  # lbs
material_dict = {  # density in lb/in^3, cost in $/lb, Young's modulus in psi, yield strength in psi, ultimate tensile strength in psi
    "steel": {  # check values
        "density": None,
        "cost": None,
        "E": None,
        "S_y": None,
        "S_UT": None,
    },
    "aluminum1": {  # check values
        "density": None,
        "cost": None,
        "E": None,
        "S_y": None,
        "S_UT": None,
    },
    "aluminum2": {  # check values
        "density": None,
        "cost": None,
        "E": None,
        "S_y": None,
        "S_UT": None,
    },
    "aluminum3": {  # check values
        "density": None,
        "cost": None,
        "E": None,
        "S_y": None,
        "S_UT": None,
    },
    "titanium": {  # check values
        "density": None,
        "cost": None,
        "E": None,
        "S_y": None,
        "S_UT": None,
    },
}
cost = material_dict["steel"]["cost"]  # $/lb
density = material_dict["steel"]["density"]  # lb/in^3
E = material_dict["steel"]["E"]  # psi
S_y = material_dict["steel"]["S_y"]  # psi
S_UT = material_dict["steel"]["S_UT"]  # psi

def obj(x):
    return calc_cost(
        x[0],
        x[1],
        x[2],
        x[3],
        HOLE_DIAMETER,
        x[4],
        calc_length_crossbar(x[0], x[6]),
        density,
        material_dict["steel"]["density"],
        cost,
        material_dict["steel"]["cost"],
    )


def con1(x):  # n_buckling 1
    l = x[0]
    h = x[1]
    w = x[2]
    t = x[3]

    y_bar = (t * w - 2 * t**2 + 2 * h**2) / (4 * h + 2 * w - 4 * t)
    I_xx = (
        2 * t * y_bar**3 / 3
        + 2 * t * (h - y_bar) ** 3 / 3
        + y_bar**3 * (-2 * t + w) / 3
        + (-2 * t + w) * (t - y_bar) ** 3 / 3
    )
    P_cr = 1.2 * pi**2 * E * I_xx / l**2

    start_angle = degrees(arcsin(x[6] / 2 / x[0]))

    F_d = calc_diagonal_force(FORCE, start_angle)
    n_buckling = P_cr / F_d
    return n_buckling - 3


def con2(x):  # n_buckling 2
    l = x[0]
    h = x[1]
    w = x[2]
    t = x[3]

    I_yy = h * w**3 / 12 - 2 * h * (-t + w / 2) ** 3 / 3 + 2 * t * (-t + w / 2) ** 3 / 3
    P_cr = 1.2 * pi**2 * E * I_yy / l**2

    start_angle = degrees(arcsin(x[6] / 2 / x[0]))

    F_d = calc_diagonal_force(FORCE, start_angle)
    n_buckling = P_cr / F_d
    return n_buckling - 3


def con3(x):  # n_tensile
    S_y_cb = material_dict["steel"]["S_y"]
    start_angle = degrees(arcsin(x[6] / 2 / x[0]))
    F_cb = calc_diagonal_force(FORCE, start_angle)
    n_tensile = S_y_cb / calc_crossbar_stress(F_cb, x[4])

    return n_tensile - 2


def con4(x): # n_tearout
    start_angle = degrees(arcsin(x[6] / 2 / x[0]))
    F_d = calc_diagonal_force(FORCE, start_angle)
    sigma_tearout = calc_tearout_stress(x[5], x[3], F_d)
    n_tearout = S_y / sigma_tearout

    return n_tearout - 2.5


def con5(x): # n_bearing
    start_angle = degrees(arcsin(x[6] / 2 / x[0]))
    F_d = calc_diagonal_force(FORCE, start_angle)
    sigma_bearing = calc_bearing_stress(HOLE_DIAMETER, x[3], F_d)
    
    n_bearing = S_y / sigma_bearing
    return n_bearing - 2


def con6(x): # n_axial
    start_angle = degrees(arcsin(x[6] / 2 / x[0]))
    F_d = calc_diagonal_force(FORCE, start_angle)
    sigma_axial = calc_diagonal_axial_stress(HOLE_DIAMETER, x[3], x[1], F_d)

    n_axial = S_y / sigma_axial
    return n_axial - 2



