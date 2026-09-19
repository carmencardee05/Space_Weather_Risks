"""
Functions for converting satellite mean motion into
semi-major axis and approximate orbital altitude.
"""

import numpy as np


# Earth's standard gravitational parameter (km^3/s^2)
MU_EARTH = 398600.4418

# Earth's equatorial radius (km)
R_EARTH = 6378.137


def mean_motion_to_altitude_km(mean_motion_rev_per_day):
    """
    Convert mean motion from revolutions per day to orbital altitude.

    Parameters:

    mean_motion_rev_per_day : float or array-like
        Mean motion in revolutions per day.

    Returns:
    
    semi_major_axis_km : float or array-like
        Semi-major axis in kilometers.
    altitude_km : float or array-like
        Approximate altitude above Earth's equatorial radius in kilometers.
    """

    # Convert revolutions/day to radians/second
    n_rad_s = mean_motion_rev_per_day * 2.0 * np.pi / 86400.0

    # Kepler's third law: a = (mu / n^2)^(1/3)
    semi_major_axis_km = (MU_EARTH / n_rad_s**2) ** (1.0 / 3.0)

    # Approximate altitude above Earth
    altitude_km = semi_major_axis_km - R_EARTH

    return semi_major_axis_km, altitude_km
