"""
Module containing the impulse response model

The 2-timescale impulse response model is mathematically equivalent to the
two-layer model without state dependence.
"""
import numpy as np
from openscm_units import unit_registry as ur

from .base import TwoLayerVariant
from .errors import ModelStateError


class ImpulseResponseModel(TwoLayerVariant):
    """
    TODO: top line and paper references

    This implementation uses a forward-differencing approach. This means that
    temperature and ocean heat uptake values are start of timestep values. For
    example, temperature[i] is only affected by drivers from the i-1 timestep.
    In practice, this means that the first temperature and ocean heat uptake
    values will always be zero and the last value in the input drivers has no
    effect on model output.
    """
    _d1_unit = "yr"
    _d2_unit = "yr"
    _q1_unit = "delta_degC/(W/m^2)"
    _q2_unit = "delta_degC/(W/m^2)"
    _delta_t_unit = "yr"

    _erf_unit = "W/m^2"

    _temp1_unit = "delta_degC"
    _temp2_unit = "delta_degC"
    _rndt_unit = "W/m^2"

    def __init__(
        self,
        q1=0.3 * ur("delta_degC/(W/m^2)"),
        q2=0.4 * ur("delta_degC/(W/m^2)"),
        d1=250.0 * ur("yr"),
        d2=3 * ur("yr"),
        delta_t=1/12 * ur("yr"),
    ):  # pylint: disable=too-many-arguments
        """
        Initialise
        """
        self.q1 = q1
        self.q2 = q2
        self.d1 = d1
        self.d2 = d2
        self.delta_t = delta_t

        self._erf = np.zeros(1) * np.nan
        self._temp1_mag = np.zeros(1) * np.nan
        self._temp2_mag = np.zeros(1) * np.nan
        self._rndt_mag = np.zeros(1) * np.nan

    @property
    def d1(self):
        """
        :obj:`pint.Quantity`
            Response timescale of first box
        """
        return self._d1

    @d1.setter
    def d1(self, val):
        self._check_is_pint_quantity(val, "d1", self._d1_unit)
        self._d1 = val
        self._d1_mag = val.to(self._d1_unit).magnitude

    @property
    def d2(self):
        """
        :obj:`pint.Quantity`
            Response timescale of second box
        """
        return self._d2

    @d2.setter
    def d2(self, val):
        self._check_is_pint_quantity(val, "d2", self._d2_unit)
        self._d2 = val
        self._d2_mag = val.to(self._d2_unit).magnitude

    @property
    def q1(self):
        """
        :obj:`pint.Quantity`
            Sensitivity of first box response to radiative forcing
        """
        return self._q1

    @q1.setter
    def q1(self, val):
        self._check_is_pint_quantity(val, "q1", self._q1_unit)
        self._q1 = val
        self._q1_mag = val.to(self._q1_unit).magnitude

    @property
    def q2(self):
        """
        :obj:`pint.Quantity`
            Sensitivity of second box response to radiative forcing
        """
        return self._q2

    @q2.setter
    def q2(self, val):
        self._check_is_pint_quantity(val, "q2", self._q2_unit)
        self._q2 = val
        self._q2_mag = val.to(self._q2_unit).magnitude

    def _reset(self):
        if np.isnan(self.erf).any():
            raise ModelStateError(
                "The model's drivers have not been set yet, call "
                ":meth:`self.set_drivers` first."
            )

        self._timestep_idx = np.nan
        self._temp1_mag = np.zeros_like(self._erf_mag) * np.nan
        self._temp2_mag = np.zeros_like(self._erf_mag) * np.nan
        self._rndt_mag = np.zeros_like(self._erf_mag) * np.nan

    def _run(self):
        for _ in self.erf:
            self.step()

    def _step(self):
        if np.isnan(self._timestep_idx):
            self._timestep_idx = 0

        else:
            self._timestep_idx += 1

        if np.equal(self._timestep_idx, 0):
            self._temp1_mag[self._timestep_idx] = 0.0
            self._temp2_mag[self._timestep_idx] = 0.0
            self._rndt_mag[self._timestep_idx] = 0.0

        else:
            self._temp1_mag[self._timestep_idx] = self._calculate_next_temp(
                self._delta_t_mag,
                self._temp1_mag[self._timestep_idx - 1],
                self._q1_mag,
                self._d1_mag,
                self._erf_mag[self._timestep_idx - 1],
            )

            self._temp2_mag[self._timestep_idx] = self._calculate_next_temp(
                self._delta_t_mag,
                self._temp2_mag[self._timestep_idx - 1],
                self._q2_mag,
                self._d2_mag,
                self._erf_mag[self._timestep_idx - 1],
            )

            self._rndt_mag[self._timestep_idx] = self._calculate_next_rndt(
                self._temp1_mag[self._timestep_idx - 1] + self._temp2_mag[self._timestep_idx - 1],
                self._erf_mag[self._timestep_idx - 1],
                self._q1_mag,
                self._q2_mag,
            )

    @staticmethod
    def _calculate_next_temp(delta_t, t, q, d, erf):
        decay_factor = np.exp(-delta_t / d)
        rise = erf * q * (1 - np.exp(-delta_t / d))

        return t * decay_factor + rise

    @staticmethod
    def _calculate_next_rndt(t, erf, q1, q2):
        return erf - t / (q1 + q2)
