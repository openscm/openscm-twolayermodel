from openscm_units import unit_registry

from .base import Model


class TwoLayerModel(Model):
    def __init__(
        self,
        du=50 * unit_registry("m"),
        dl=1200 * unit_registry("m"),
        lambda_0=-3.74/3 * unit_registry("W/m^2/delta_degC"),
        a=0.0 * unit_registry("W/m^2/delta_degC^2"),
        efficacy=1.0 * unit_registry("dimensionless"),
        eta=0.8 * unit_registry("W/m^2/K")
    ):
        """
        Initialise

        Parameters
        ----------
        du : :obj:`pint.Quantity`
            Depth of upper layer

        dl : :obj:`pint.Quantity`
            Depth of lower layer

        lambda_0 : :obj:`pint.Quantity`
            Initial climate feedback factor

        a : :obj:`pint.Quantity`
            Dependence of climate feedback factor on temperature

        efficacy : :obj:`pint.Quantity`
            Efficacy factor

        eta : :obj:`pint.Quantity`
            Heat transport efficiecny
        """
