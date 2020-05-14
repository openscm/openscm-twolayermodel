"""
Physical constants used in calculations
"""
from openscm_units import unit_registry as ur

density_water = 1000 * ur("kg/m^3")
""":obj:`pint.Quantity` : density of water"""

heat_capacity_water = 4181 * ur("J/delta_degC/kg")
""":obj:`pint.Quantity` : heat capacity of water"""
