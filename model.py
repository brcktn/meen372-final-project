"""
todo:
- calculate n_buckling
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

def model(
    length_diagonal: float,  # inches
    cross_section_height: float,  # inches
    cross_section_width: float,  # inches
    material_thickness: float,  # inches
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
        "Aluminum": {"density": 2700, "cost": 2.5, "E": 10e6, "S_y": 40000, "S_UT": 45000},
        "Steel": {"density": 7850, "cost": 1.5, "E": 30e6, "S_y": 50000, "S_UT": 65000},
    }
    height_lifted = 6.0  # inches
    crossbar_diameter = 1.0  # inches

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


def calc_centeroid(
    cross_section_height: float,  # inches
    cross_section_width: float,  # inches
    thickness: float,  # inches
) -> tuple[float, float]:
    """
    Calculates the centroid of a given cross section
    Parameters. Viewing the C beam in the "U" orientation
    x is measured from the left, y is measured from the bottom
    ----------
    cross_section_height : float
        The length of the cross section of the jack.
    cross_section_width : float
        The width of the cross section of the jack.
    thickness : float
        The thickness of the material.
    
    Returns
    -------
    tuple of floats
        - x coordinate of the centroid
        - y coordinate of the centroid
    """
    x_bar = cross_section_height / 2
    y_bar = (
        thickness * cross_section_width - 2 * thickness**2 + 2 * cross_section_height**2
    ) / (4 * cross_section_height + 2 * cross_section_width - 4 * thickness)

    return x_bar, y_bar


def calc_moment_of_inertia(
    cross_section_height: float,  # inches
    cross_section_width: float,  # inches
) -> tuple[float, float]:  # inches^4
    """
    Calculates the second moments of area for a given cross section
    Parameters. Viewing the C beam in the "U" orientation
    x is the horizontal axis, y is the vertical axis

    Parameters
    ----------
    cross_section_height : float
        The length of the cross section of the jack.
    cross_section_width : float
        The width of the cross section of the jack.

    Returns
    -------
    Returns:
        A tuple of floats
            - Moment of inertia about the x-axis (in inches^4).
            - Moment of inertia about the y-axis (in inches^4).
    """
    return None
