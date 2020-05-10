import numpy as np
from openscm_units import unit_registry as ur

from .base import Model


class TwoLayerModel(Model):

    _du_unit = "m"
    _dl_unit = "m"
    _lambda_0_unit = "W/m^2/delta_degC"
    _a_unit = "W/m^2/delta_degC^2"
    _efficacy_unit = "dimensionless"
    _eta_unit = "W/m^2/K"
    _delta_t_unit = "s"
    _erf_unit = "W/m^2"

    def __init__(
        self,
        du=50 * ur("m"),
        dl=1200 * ur("m"),
        lambda_0=-3.74 / 3 * ur("W/m^2/delta_degC"),
        a=0.0 * ur("W/m^2/delta_degC^2"),
        efficacy=1.0 * ur("dimensionless"),
        eta=0.8 * ur("W/m^2/K"),
        delta_t=ur("yr").to("s")
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

        delta_t : :obj:`pint.Quantity`
            Time step for forward-differencing approximation
        """
        self.du = du
        self.dl = dl
        self.lambda_0 = lambda_0
        self.a = a
        self.efficacy = efficacy
        self.eta = eta
        self.delta_t = delta_t

        self._erf = np.nan

    # must be a better way to handle this property creation...
    @property
    def du(self):
        return self._du

    @du.setter
    def du(self, val):
        self._check_is_pint_quantity(val, "du", self._du_unit)
        self._du = val
        self._du_mag = val.to(self._du_unit).magnitude

    @property
    def dl(self):
        return self._dl

    @dl.setter
    def dl(self, val):
        self._check_is_pint_quantity(val, "dl", self._dl_unit)
        self._dl = val
        self._dl_mag = val.to(self._dl_unit).magnitude

    @property
    def lambda_0(self):
        return self._lambda_0

    @lambda_0.setter
    def lambda_0(self, val):
        self._check_is_pint_quantity(val, "lambda_0", self._lambda_0_unit)
        self._lambda_0 = val
        self._lambda_0_mag = val.to(self._lambda_0_unit).magnitude

    @property
    def a(self):
        return self._a

    @a.setter
    def a(self, val):
        self._check_is_pint_quantity(val, "a", self._a_unit)
        self._a = val
        self._a_mag = val.to(self._a_unit).magnitude

    @property
    def efficacy(self):
        return self._efficacy

    @efficacy.setter
    def efficacy(self, val):
        self._check_is_pint_quantity(val, "efficacy", self._efficacy_unit)
        self._efficacy = val
        self._efficacy_mag = val.to(self._efficacy_unit).magnitude

    @property
    def eta(self):
        return self._eta

    @eta.setter
    def eta(self, val):
        self._check_is_pint_quantity(val, "eta", self._eta_unit)
        self._eta = val
        self._eta_mag = val.to(self._eta_unit).magnitude

    @property
    def delta_t(self):
        return self._delta_t

    @delta_t.setter
    def delta_t(self, val):
        self._check_is_pint_quantity(val, "delta_t", self._delta_t_unit)
        self._delta_t = val
        self._delta_t_mag = val.to(self._delta_t_unit).magnitude

    @property
    def erf(self):
        return self._erf

    @erf.setter
    def erf(self, val):
        self._check_is_pint_quantity(val, "erf", self._erf_unit)
        self._erf = val
        self._erf_mag = val.to(self._erf_unit).magnitude

    def set_drivers(self, erf):
        """
        Set drivers for a model run

        Parameters
        ----------
        erf : :obj:`pint.Quantity`
            Effective radiative forcing (W/m^2) to use to drive the model
        """
        self.erf = erf
