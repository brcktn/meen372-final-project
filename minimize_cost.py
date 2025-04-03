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
    return None


# def con3(x):  # tearout constrait
#     return None


# def con4(x):
#     return None


# if __name__ == "__main__":

#     cons = []
#     x0 = []
#     bounds = []

#     minimize(calc_cost, x0, bounds=bounds, constraints=cons)
