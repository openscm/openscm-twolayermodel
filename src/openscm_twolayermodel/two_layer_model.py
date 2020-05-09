from openscm_units import unit_registry

from .base import Model


class TwoLayerModel(Model):
    def __init__(
        self,
        du=50 * unit_registry("m"),
        dl=1200 * unit_registry("m"),
        lambda_0=-3.74 / 3 * unit_registry("W/m^2/delta_degC"),
        a=0.0 * unit_registry("W/m^2/delta_degC^2"),
        efficacy=1.0 * unit_registry("dimensionless"),
        eta=0.8 * unit_registry("W/m^2/K"),
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
        self.du = du
        self.dl = dl
        self.lambda_0 = lambda_0
        self.a = a
        self.efficacy = efficacy
        self.eta = eta

    @property
    def du(self):
        return self._du

    @du.setter
    def du(self, val):
        self._check_is_pint_quantity(val, "du")
        self._du = val

    @property
    def dl(self):
        return self._dl

    @dl.setter
    def dl(self, val):
        self._check_is_pint_quantity(val, "dl")
        self._dl = val

    @property
    def lambda_0(self):
        return self._lambda_0

    @lambda_0.setter
    def lambda_0(self, val):
        self._check_is_pint_quantity(val, "lambda_0")
        self._lambda_0 = val

    @property
    def a(self):
        return self._a

    @a.setter
    def a(self, val):
        self._check_is_pint_quantity(val, "a")
        self._a = val

    @property
    def efficacy(self):
        return self._efficacy

    @efficacy.setter
    def efficacy(self, val):
        self._check_is_pint_quantity(val, "efficacy")
        self._efficacy = val

    @property
    def eta(self):
        return self._eta

    @eta.setter
    def eta(self, val):
        self._check_is_pint_quantity(val, "eta")
        self._eta = val
