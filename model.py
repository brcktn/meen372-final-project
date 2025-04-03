"""
todo:
- add materials
- minimize cost using scipy
"""

from numpy import pi, sqrt, sin, cos, tan, radians, degrees, arcsin, abs

# Constants
material_dict = {  # density in lb/in^3, cost in $/lb, Young's modulus in psi, yield strength in psi, ultimate tensile strength in psi
    "steel 1030 1000C": {  # check values 
        "density": 490,
        "cost": 2.22,
        "E": 27600000,
        "S_y": 75000,
        "S_UT": 97000,
    },
    "AL 3004 h38": {  # check values
        "density": 170,
        "cost": 1.13,
        "E": 10400000,
        "S_y": 34000,
        "S_UT": 40000,
    },
    "AL 3003 h16": {  # check values
        "density": 170,
        "cost": 1.13,
        "E": 10400000,
        "S_y": 24000,
        "S_UT": 26000,
    },
    "AL  5052 h32": {  # check values
        "density": 170,
        "cost": 1.13,
        "E": 10400000,
        "S_y": 27000,
        "S_UT": 34000,
    },
    "Ti-5Al 2.5Sn": {  # check values
        "density": 280,
        "cost": 9,
        "E": 16500000,
        "S_y": 75000,
        "S_UT": 97000,
    },
}
HEIGHT_LIFTED = 6.0  # inches
HOLE_DIAMETER = 0.5  # inches
FORCE = 3000  # lbs

def model(
    length_diagonal: float,  # inches
    cross_section_height: float,  # inches
    cross_section_width: float,  # inches
    material_thickness: float,  # inches
    crossbar_diameter: float,  # inches
    hole_offset: float,  # inches
    start_height: float,  # inches
    material: str,
) -> tuple[float, float, float, float, float, float, float]:
    """
    Calculates the safety factors for a jack made with the given inputs.

    assumes that the crossbar is made of steel and is extactly the
    length needed when the jack is at the start height

    Parameters
    ----------
    length_diagonal : float
        The length of the diagonal of the jack.
    cross_section_height : float
        The length of the cross section of the jack.
    cross_section_width : float
        The width of the cross section of the jack.
    material_thickness : float
        The thickness of the material.
    crossbar_diameter : float
        The diameter of the crossbar.
    hole_offset : float
        How far the pin is from the end of the diagonal member
    start_height : float
        The height at which the jack is started.
    material : str
        The material used to make the jack, referenced from material_dict.

    Returns
    -------
    tuple of floats
        - Diagonal buckling safety factor
        - Crossbar tensile safety factor
        - Tearout safety factor
        - Bearing stress safety factor
        - Axial stress safety factor
        - Weight (lbs)
        - Cost ($)
    """

    # Calculated values
    start_angle = degrees(arcsin(start_height / 2 / length_diagonal))  # (degrees)
    length_cb = calc_length_crossbar(
        length_diagonal,
        start_height,
        )

    F_d = calc_diagonal_force(FORCE, start_angle)  # (lbs)
    F_cb = calc_crossbar_force(FORCE, start_angle)  # (lbs)
    E = material_dict[material]["E"]  # (psi)
    S_y = material_dict[material]["S_y"]  # (psi)
    S_UT = material_dict[material]["S_UT"]  # (psi)

    P_cr = calc_critical_buckling_load(
        E,
        length_diagonal,
        cross_section_height,
        cross_section_width,
        material_thickness,
        hole_offset,
    )

    n_buckling = P_cr / F_d
    n_tensile = material_dict["steel"]["S_y"] / calc_crossbar_stress(
        F_cb,
        crossbar_diameter,
    )
    n_tearout = S_y / calc_tearout_stress(
        hole_offset,
        material_thickness,
        F_d,
    )
    n_bearing = S_y / calc_bearing_stress(
        HOLE_DIAMETER,
        material_thickness,
        F_d,
    )
    n_axial = S_y / calc_diagonal_axial_stress(
        HOLE_DIAMETER,
        material_thickness,
        cross_section_height,
        F_d,
    )
    weight = calc_weight(
        length_diagonal,
        cross_section_height,
        cross_section_width,
        material_thickness,
        HOLE_DIAMETER,
        crossbar_diameter,
        length_cb,
        material_dict[material]["density"],
        material_dict["steel"]["density"],
    )
    cost = calc_cost(
        length_diagonal,
        cross_section_height,
        cross_section_width,
        material_thickness,
        HOLE_DIAMETER,
        crossbar_diameter,
        length_cb,
        material_dict[material]["density"],
        material_dict["steel"]["density"],
        material_dict[material]["cost"],
        material_dict["steel"]["cost"],
    )

    print(f"Diagonal Buckling Safety Factor: {n_buckling:.5f}")
    print(f"Crossbar Tensile Safety Factor: {n_tensile:.5f}")
    print(f"Tearout Safety Factor: {n_tearout:.5f}")
    print(
        f"Bearing Stress Safety Factor: {n_bearing:.5f}"
        if n_bearing is not None
        else "Bearing Stress Safety Factor: Not calculated"
    )
    print(f"Axial Stress Safety Factor: {n_axial:.5f}")
    print(
        f"Weight: {weight:.5f} lbs" if weight is not None else "Weight: Not calculated"
    )
    print(f"Cost: ${cost:.5f}" if cost is not None else "Cost: Not calculated")

    return (
        n_buckling,
        n_tensile,
        n_tearout,
        n_bearing,
        n_axial,
        weight,
        cost,
    )


def calc_diagonal_force(
    force: float,  # lbs
    start_angle: float,  # degrees
) -> float:  # lbs
    """
    Calculates the compressive force in a single diagonal of the jack.
    Assumes that maximum force is applied to the jack at the start angle.
    The force is calculated using the formula:
           F
        ────────
        2⋅sin(θ)
    where F is the force applied to the jack and θ is the angle at which the jack is started.

    Parameters
    ----------
    force : float
        The force applied to the jack.
    start_angle : float
        The angle at which the jack is started.

    Returns
    -------
    float
        The force in the diagonal of the jack (lbs).
    """
    return force / (2 * sin(radians(start_angle)))


def calc_crossbar_force(
    force: float,  # lbs
    start_angle: float,  # degrees
) -> float:  # lbs
    """
    Calculates the tensile force in the crossbar of the jack.
    Assumes that maximum force is applied to the jack at the start angle.
    The force is calculated using the formula:
           F
        ────────
         tan(θ)
    where F is the force applied to the jack and θ is the angle at which the jack is started.

    Parameters
    ----------
    force : float
        The force applied to the jack.
    start_angle : float
        The angle at which the jack is started.

    Returns
    -------
    float
        The force in the crossbar (lbs).
    """
    return force / tan(radians(start_angle))


def calc_crossbar_stress(
    F_cb,  # lbs
    crossbar_diameter: float,  # inches
) -> float:  # psi
    """
    Calculates the tensile stress in the crossbar of the jack.
    Assumes that maximum force is applied to the jack at the start angle."""
    A_cb = pi * (crossbar_diameter / 2) ** 2  # inches^2
    return F_cb / A_cb  # psi


def calc_centeroid(
    h: float,  # cross section height (inches)
    w: float,  # cross section width (inches)
    t: float,  # cross section thickness (inches)
) -> tuple[float, float]:
    """
    Calculates the centroid of a given cross section
    Parameters. Viewing the C beam in the "U" orientation
    x is measured from the left, y is measured from the bottom
    ----------
    h : float
        The length of the cross section of the jack.
    w : float
        The width of the cross section of the jack.
    t : float
        The thickness of the material.

    Returns
    -------
    tuple of floats
        - x coordinate of the centroid
        - y coordinate of the centroid
    """
    x_bar = h / 2
    y_bar = (t * w - 2 * t**2 + 2 * h**2) / (4 * h + 2 * w - 4 * t)

    return x_bar, y_bar


def calc_moments_of_inertia(
    h: float,  # cross section height (inches)
    w: float,  # cross section width (inches)
    t: float,  # cross section thickness (inches)
) -> tuple[float, float]:  # inches^4
    """
    Calculates the second moments of area for a given cross section
    Parameters. Viewing the C beam in the "U" orientation
    x is the horizontal axis, y is the vertical axis

    Parameters
    ----------
    h : float
        The height of the cross section of the jack.
    w : float
        The width of the cross section of the jack.
    t : float
        The thickness of the material.

    Returns
    -------
    tuple of floats
        - Moment of inertia about the x-axis (in inches^4).
        - Moment of inertia about the y-axis (in inches^4).
    """
    x_bar, y_bar = calc_centeroid(h, w, t)

    I_xx = (
        2 * t * y_bar**3 / 3
        + 2 * t * (h - y_bar) ** 3 / 3
        + y_bar**3 * (-2 * t + w) / 3
        + (-2 * t + w) * (t - y_bar) ** 3 / 3
    )
    I_yy = h * w**3 / 12 - 2 * h * (-t + w / 2) ** 3 / 3 + 2 * t * (-t + w / 2) ** 3 / 3

    return I_xx, I_yy


def calc_critical_buckling_load(
    E: float,  # Young's modulus (psi)
    length_diagonal: float,  # (inches)
    h: float,  # height of the cross section (inches)
    w: float,  # Width of the cross section (inches)
    t: float,  # Thickness of the cross section (inches)
    hole_offset: float,  # distance from end of diagonal to hole (inches)
) -> float:  # lbs
    """
    Calculates the critical buckling load for a given cross section
    Parameters. Uses Euler's formula for buckling:
                C⋅π^2⋅E⋅I
        P_cr = ───────────
                   l^2
    where P_cr is the critical buckling load, C is an end condition factor,
    E is the Young's modulus, I is the smaller moment of inertia, and l
    is the length of the diagonal between the two pins.
    """
    min_I = min(
        calc_moments_of_inertia(h, w, t)
    )  # smaller of the two moments of inertia
    l = length_diagonal - 2 * hole_offset  # length of the diagonal between the two pins
    C = 1.2  # end condition factor for pinned-pinned

    P_cr = C * pi**2 * E * min_I / l**2
    return P_cr


def calc_tearout_stress(
    de: float,  # distance from center of bolt to edge of member (inches)
    t: float,  # thickness of member (inches)
    F_d: float,  # tearout force (lbs)
) -> float:  # tearout stress
    return sqrt(3) * F_d / (4 * de * t)


def calc_diagonal_axial_stress(
    d_h: float,  # diameter of bolt hole (inches)
    t: float,  # thickness of member (inches)
    h: float,  # height of channel (inches)
    F_d: float,  # tearout force (lbs)
) -> float:  # axial stress
    return abs(F_d / (2 * t * (h - d_h)))


def calc_bearing_stress(
    d_h: float,  # diameter of bolt hole (inches)
    t: float,  # thickness of member (inches)
    F_d: float,  # tearout force (lbs)
) -> float:  # bearing stress
    return abs(F_d / (2 * t * d_h))


# I don't think we need this
#
# def calc_crossbar_bearing_stress(
#     d:float, #diameter crossbar
#     fcb:float,  #tearout force
# ) -> float: #tearout stress
#     return abs(fcb/((pi/4)*d**2))


def calc_weight(
    l_d: float,  # length of diagonal (inches)
    h: float,  # cross-section height (inches)
    w: float,  # cross-section width (inches)
    t: float,  # material thickness (inches)
    d_h: float,  # diameter of hole (inches)
    d_cb: float,  # diameter of crossbar (inches)
    l_cb: float,  # length of crossbar (inches)
    density_d: float,  # material density (lb/in^3)
    density_cb: float,  # material density (lb/in^3)
) -> float:  # weight (lbs)
    """
    Calculates the weight of the jack.

    Parameters
    ----------
    l_d : float
        Length of the diagonal member.
    h : float
        Height of the cross-section.
    w : float
        Width of the cross-section.
    t : float
        Thickness of the material.
    d_h : float
        Diameter of the holes.
    d_cb : float
        Diameter of the crossbar.
    l_cb : float
        Length of the crossbar.
    desnity : float
        Density of the material.

    Returns
    -------
    float
        Weight of the jack in pounds.
    """
    # Volume of one diagonal member, subtracting the volume of the holes
    volume_d = l_d * (h * w - (w - 2 * t) * (h - t)) - pi * d_h**2 * t
    # Volume of the crossbar
    volume_cb = pi * (d_cb / 2) ** 2 * l_cb

    # 4 diagonal members, 1 crossbar
    return 4 * volume_d * density_d + volume_cb * density_cb  # lbs


def calc_cost(
    l_d: float,  # length of diagonal (inches)
    h: float,  # cross-section height (inches)
    w: float,  # cross-section width (inches)
    t: float,  # material thickness (inches)
    d_h: float,  # diameter of hole (inches)
    d_cb: float,  # diameter of crossbar (inches)
    l_cb: float,  # length of crossbar (inches)
    density_d: float,  # material density (lb/in^3)
    density_cb: float,  # material density (lb/in^3)
    cost_d: float,  # material cost ($/lb)
    cost_cb: float,  # material cost ($/lb)
) -> float:  # cost ($)
    """
    Calculates the cost of the jack.
    Parameters
    ----------
    l_d : float
        Length of the diagonal member.
    h : float
        Height of the cross-section.
    w : float
        Width of the cross-section.
    t : float
        Thickness of the material.
    d_h : float
        Diameter of the holes.
    d_cb : float
        Diameter of the crossbar.
    l_cb : float
        Length of the crossbar.
    density_d : float
        Density of the diagonal member material.
    density_cb : float
        Density of the crossbar material.
    cost_d : float
        Cost of the diagonal member material ($/lb).
    cost_cb : float
        Cost of the crossbar material ($/lb).
    Returns
    -------
    float
        Cost of the jack ($).
    """

    # Volume of one diagonal member, subtracting the volume of the holes
    volume_d = l_d * (h * w - (w - 2 * t) * (h - t)) - pi * d_h**2 * t
    # Volume of the crossbar
    volume_cb = pi * (d_cb / 2) ** 2 * l_cb

    # 4 diagonal members, 1 crossbar
    return 4 * volume_d * density_d * cost_d + volume_cb * density_cb * cost_cb  # $


def calc_length_crossbar(
    length_diagonal: float,  # inches
    start_height: float,  # inches
) -> float:  # inches
    """
    Calculates the length of the crossbar of the jack.
    Assumes that the crossbar is exactly the length needed when the jack is at the start height.
    """
    return sqrt(length_diagonal**2 - (start_height / 2) ** 2)