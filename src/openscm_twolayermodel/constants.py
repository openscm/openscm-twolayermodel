"""
Physical constants used in calculations
"""
from openscm_units import unit_registry as ur

DENSITY_WATER = 1000 * ur("kg/m^3")
""":obj:`pint.Quantity` : density of water"""

HEAT_CAPACITY_WATER = 4181 * ur("J/delta_degC/kg")
""":obj:`pint.Quantity` : heat capacity of water"""
