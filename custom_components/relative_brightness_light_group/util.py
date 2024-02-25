"""Utility functions."""


def coerce_in(value, minimum, maximum):
    """Coerce value in range given by minimum and maximum."""
    return max(minimum, min(value, maximum))
