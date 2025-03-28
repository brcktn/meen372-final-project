"""
todo:
- calculate n_buckling (brock)
    - calculate the moment of inertia
    - calculate the critical buckling load
- calculate n_tensile
    - calculate force in the crossbar
- calculate n_tearout
- calculate n_shear
- calculate n_bearing
- calculate weight
- calculate cost

- minimize cost using scipy
"""

from numpy import pi, sqrt, sin, cos, radians


def model(
    length_diagonal: float,  # inches
    cross_section_height: float,  # inches
    cross_section_width: float,  # inches
    material_thickness: float,  # inches
    crossbar_diameter: float,  # inches
    hole_offset: float,  # inches
    start_angle: float,  # degrees
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
    start_angle : float
        The angle at which the jack is started.
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
        "Aluminum": {
            "density": 2700,
            "cost": 2.5,
            "E": 10e6,
            "S_y": 40000,
            "S_UT": 45000,
        },
        "Steel": {"density": 7850, "cost": 1.5, "E": 30e6, "S_y": 50000, "S_UT": 65000},
    }
    height_lifted = 6.0  # inches
    force = 3000  # lbs

    n_buckling = None
    n_tensile = None
    n_tearout = None
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
    Calculates the compressive force in the diagonal of the jack.

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
    return I_xx, None
