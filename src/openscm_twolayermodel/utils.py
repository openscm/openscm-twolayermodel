"""
Utility functions
"""
import pint
from openscm_units import unit_registry


def convert_lambda_to_ecs(lambda_val, f2x=3.74 * unit_registry("W/m^2")):
    """
    Convert a lambda value to equilibrium climate sensitivity (ECS)

    Parameters
    ----------
    lambda_val : :obj:`pint.Quantity`
        Value of lambda to convert to ECS

    f2x : :obj:`pint.Quantity`
        Value of the forcing due to a doubling of atmospheric |CO2|
        to assume during the conversion

    Returns
    -------
    :obj:`pint.Quantity`
        ECS value

    Raises
    ------
    TypeError
        ``lambda_val`` or ``f2x`` is not a :obj:`pint.Quantity`.
    """
    if not isinstance(lambda_val, pint.Quantity):
        raise TypeError("lambda_val is not a pint.Quantity")

    if not isinstance(f2x, pint.Quantity):
        raise TypeError("f2x is not a pint.Quantity")

    return -f2x / lambda_val
