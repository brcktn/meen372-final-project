"""
todo:
- calculate n_tensile
- calculate n_shear
- calculate n_bearing
- calculate weight
- calculate cost

- minimize cost using scipy
"""

from numpy import pi, sqrt, sin, cos, tan, radians, degrees, arcsin, abs


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
        - Shear safety factor
        - Bearing stress safety factor
        - Weight (lbs)
        - Cost ($)
    """

    # Constants
    material_dict = {  # density in lb/in^3, cost in $/lb, Young's modulus in psi, yield strength in psi, ultimate tensile strength in psi
        "aluminum": {
            "density": 2700,
            "cost": 2.5,
            "E": 10e6,
            "S_y": 40000,
            "S_UT": 45000,
        },
        "steel": {"density": 7850, "cost": 1.5, "E": 30e6, "S_y": 50000, "S_UT": 65000},
    }
    HEIGHT_LIFTED = 6.0  # inches
    FORCE = 3000  # lbs

    # Calculated values
    start_angle = degrees(arcsin(start_height / 2 / length_diagonal)) # (degrees)

    F_d = calc_diagonal_force(FORCE, start_angle) # (lbs)
    F_cb = calc_crossbar_force(FORCE, start_angle) # (lbs)
    E = material_dict[material]["E"] # (psi)
    S_y = material_dict[material]["S_y"] # (psi)
    S_UT = material_dict[material]["S_UT"] # (psi)
    density = material_dict[material]["density"] # (lb/in^3)
    cost = material_dict[material]["cost"] # ($/lb)

    P_cr = calc_critical_buckling_load(
        E,
        length_diagonal,
        cross_section_height,
        cross_section_width,
        material_thickness,
        hole_offset,
    )
    
    n_buckling = P_cr / F_d
    n_tensile = None
    n_tearout = S_y / tearoutStress(
        hole_offset,
        material_thickness,
        F_d,
    )
    n_shear = None
    n_bearing = None
    weight = None
    cost = None

    return (
        n_buckling,
        n_tensile,
        n_tearout,
        n_shear,
        n_bearing,
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
    I_yy = h*w**3/12 - 2*h*(-t + w/2)**3/3 + 2*t*(-t + w/2)**3/3
    
    return I_xx, I_yy


def calc_critical_buckling_load(
    E: float,  # Young's modulus (psi)
    length_diagonal: float,  # (inches)
    h: float,  # height of the cross section (inches)
    w: float,  # Width of the cross section (inches)
    t: float,  # Thickness of the cross section (inches)
    hole_offset: float, # distance from end of diagonal to hole (inches)
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
    min_I = min(calc_moments_of_inertia(h, w, t)) # smaller of the two moments of inertia
    l = length_diagonal - 2 * hole_offset  # length of the diagonal between the two pins 
    C = 1.2  # end condition factor for pinned-pinned

    P_cr = C * pi**2 * E * min_I / l**2
    return P_cr

def tearoutStress(
    de: float, #distance from center of bolt to edge of member (inches)
    t: float,   #thickness of member (inches)
    fd: float,  #tearout force (lbs)
) -> float: #tearout stress
    return sqrt(3)*fd/(4*de*t)

def diagAxialStress(
    dh:float, #diameter of bolt hole
    t:float,   #thickness of member
    h:float,   #height of channel
    fd:float,  #tearout force
) -> float: #tearout stress
    return abs(fd/(2*t*(h-dh)))

def diagBearingStress(
    dh:float, #diameter of bolt hole
    t:float,   #thickness of member
    fd:float,  #tearout force
) -> float: #tearout stress
    return abs(fd/(2*t*dh))


