"""
Emptirical projections.
"""
import numpy as np


def compute_initial_projection_uk():
    """Compute projection from 21 March 2020 for 10 days."""
    # fixed numbers on March 21, one day after pubs, cafes etc
    # have been shut
    # reported cases
    b = 0.25  # exp rate
    y0 = 5018.  # no of reported cases
    x0 = 21.  # day: March 21
    y = y0 * np.exp(b * 10.)  # evolution (R=0.99)
    # deaths
    m = 0.37  # exp rate
    y0d = 233.  # no of reported deaths
    yd = y0d * np.exp(m * 10.)  # evolution (R=0.97)

    # allow for an immediate decrease in exp rates,
    # equivalent to some places where quarantines
    b_min = 0.2
    m_min = 0.2
    y_min = y0 * np.exp(b_min * 10.)
    yd_min = y0d * np.exp(m_min * 10.)

    return (x0, y0, y0d, y, yd, y_min, yd_min)
