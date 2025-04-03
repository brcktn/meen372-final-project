from model import *
from scipy.optimize import minimize
from numpy import sin, cos, tan, pi, degrees, arcsin

"""
x[0]: length_diagonal (float, inches)
x[1]: cross_section_height (float, inches)
x[2]: cross_section_width (float, inches)
x[3]: material_thickness (float, inches)
x[4]: crossbar_diameter (float, inches)
x[5]: hole_offset (float, inches)
STARTING_HEIGHT: start_height (float, inches)
"""

# Constants
HEIGHT_LIFTED = 6.0  # inches
HOLE_DIAMETER = 0.5  # inches
FORCE = 3000  # lbs
STARTING_HEIGHT = 5.0  # inches
DISTANCE_LIFTED = 6.0  # inches

material_dict = {  # density in lb/in^3, cost in $/lb, Young's modulus in psi, yield strength in psi, ultimate tensile strength in psi
    "steel 1030 1000C": {  # check values
        "density": 490 / 12**3,
        "cost": 2.22,
        "E": 27600000,
        "S_y": 75000,
        "S_UT": 97000,
    },
    "AL 3004 h38": {  # check values
        "density": 170 / 12**3,
        "cost": 1.13,
        "E": 10400000,
        "S_y": 34000,
        "S_UT": 40000,
    },
    "AL 3003 h16": {  # check values
        "density": 170 / 12**3,
        "cost": 1.13,
        "E": 10400000,
        "S_y": 24000,
        "S_UT": 26000,
    },
    "AL  5052 h32": {  # check values
        "density": 170 / 12**3,
        "cost": 1.13,
        "E": 10400000,
        "S_y": 27000,
        "S_UT": 34000,
    },
    "Ti-5Al 2.5Sn": {  # check values
        "density": 280 / 12**3,
        "cost": 9,
        "E": 16500000,
        "S_y": 75000,
        "S_UT": 97000,
    },
}
cost = material_dict["steel 1030 1000C"]["cost"]  # $/lb
density = material_dict["steel 1030 1000C"]["density"]  # lb/in^3
E = material_dict["steel 1030 1000C"]["E"]  # psi
S_y = material_dict["steel 1030 1000C"]["S_y"]  # psi
S_UT = material_dict["steel 1030 1000C"]["S_UT"]  # psi


"""
x[0]: length_diagonal (float, inches)
x[1]: cross_section_height (float, inches)
x[2]: cross_section_width (float, inches)
x[3]: material_thickness (float, inches)
x[4]: crossbar_diameter (float, inches)
x[5]: hole_offset (float, inches)
STARTING_HEIGHT: start_height (float, inches)
"""


def obj(x):
    return calc_cost(
        x[0],
        x[1],
        x[2],
        x[3],
        HOLE_DIAMETER,
        x[4],
        calc_length_crossbar(x[0], STARTING_HEIGHT),
        density,
        material_dict["steel 1030 1000C"]["density"],
        cost,
        material_dict["steel 1030 1000C"]["cost"],
    )


def con1(x):  # n_buckling 1
    l = x[0] - 2 * x[5]
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

    start_angle = degrees(arcsin((STARTING_HEIGHT / 2) / x[0]))

    F_d = calc_diagonal_force(FORCE, start_angle)
    n_buckling = P_cr / F_d
    return n_buckling - 10


def con2(x):  # n_buckling 2
    l = x[0] - 2 * x[5]
    h = x[1]
    w = x[2]
    t = x[3]

    I_yy = h * w**3 / 12 - 2 * h * (-t + w / 2) ** 3 / 3 + 2 * t * (-t + w / 2) ** 3 / 3
    P_cr = 1.2 * pi**2 * E * I_yy / l**2

    start_angle = degrees(arcsin((STARTING_HEIGHT / 2) / x[0]))

    F_d = calc_diagonal_force(FORCE, start_angle)
    n_buckling = P_cr / F_d
    return n_buckling - 6


def con3(x):  # n_tensile
    S_y_cb = material_dict["steel 1030 1000C"]["S_y"]
    start_angle = degrees(arcsin((STARTING_HEIGHT / 2) / (x[0] - 2 * x[5])))
    F_cb = calc_crossbar_force(FORCE, start_angle)
    n_tensile = S_y_cb / calc_crossbar_stress(F_cb, x[4])

    return n_tensile - 4


def con4(x):  # n_tearout
    start_angle = degrees(arcsin((STARTING_HEIGHT / 2) / (x[0] - 2 * x[5])))
    F_d = calc_diagonal_force(FORCE, start_angle)
    sigma_tearout = calc_tearout_stress(x[5], x[3], F_d)
    n_tearout = S_y / sigma_tearout

    return n_tearout - 5


def con5(x):  # n_bearing
    start_angle = degrees(arcsin((STARTING_HEIGHT / 2) / (x[0] - 2 * x[5])))
    F_d = calc_diagonal_force(FORCE, start_angle)
    sigma_bearing = calc_bearing_stress(HOLE_DIAMETER, x[3], F_d)

    n_bearing = S_y / sigma_bearing
    return n_bearing - 4


def con6(x):  # n_axial
    start_angle = degrees(arcsin((STARTING_HEIGHT / 2) / (x[0] - 2 * x[5])))
    F_d = calc_diagonal_force(FORCE, start_angle)
    sigma_axial = calc_diagonal_axial_stress(HOLE_DIAMETER, x[3], x[1], F_d)

    n_axial = S_y / sigma_axial
    return n_axial - 4


def con7(x):  # final angle
    final_angle = degrees(arcsin(((STARTING_HEIGHT + HEIGHT_LIFTED) / 2) / (x[0] - 2 * x[5])))
    return 80 - final_angle


def con8(x):  # thickness smaller than cross_section_height
    return x[1] - x[3]*2 - x[4]


def con9(x):  # thickness smaller than cross_section_width
    return x[2] - x[3]*2 - x[4]


def con10(x):  # hole offset is reasonable
    return x[0] - x[5]*10


constraints = [
    {"type": "ineq", "fun": con1},
    {"type": "ineq", "fun": con2},
    {"type": "ineq", "fun": con3},
    {"type": "ineq", "fun": con4},
    {"type": "ineq", "fun": con5},
    {"type": "ineq", "fun": con6},
    {"type": "ineq", "fun": con7},
    {"type": "ineq", "fun": con8},
    {"type": "ineq", "fun": con9},
    {"type": "ineq", "fun": con10},
]

bounds = [
    (STARTING_HEIGHT/2, 20),  # length_diagonal
    (0.25, 5),  # cross_section_height
    (0.25, 5),  # cross_section_width
    (0.01, 1),  # material_thickness
    (0.2, 2),  # crossbar_diameter
    (0.51, 1),  # hole_offset
]

initial_guess = [15, 2, 2, 0.25, 1, 2]

result = minimize(
    obj,
    initial_guess,
    constraints=constraints,
    bounds=bounds,
    method="COBYQA",
    options={"disp": False, "adaptive": True, "maxiter": 10000, "maxfev": 10000, "initial_tr_radius": 0.01},
)

print("Optimization Success:", result.success)  # True if optimization succeeded
print("Optimal Value of x:", result.x)  # The value of x that minimizes the function
print("Minimum Function Value:", result.fun)  # The minimum function value
print("Exit Message:", result.message)
