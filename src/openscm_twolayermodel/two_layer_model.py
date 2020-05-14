"""
Module containing the two-layer model
"""
import numpy as np
from openscm_units import unit_registry as ur

from .base import TwoLayerVariant, _calculate_geoffroy_helper_parameters
from .constants import DENSITY_WATER, HEAT_CAPACITY_WATER
from .errors import ModelStateError

# pylint: disable=invalid-name


class TwoLayerModel(TwoLayerVariant):  # pylint: disable=too-many-instance-attributes
    """
    TODO: top line and paper references

    This implementation uses a forward-differencing approach. This means that
    temperature and ocean heat uptake values are start of timestep values. For
    example, temperature[i] is only affected by drivers from the i-1 timestep.
    In practice, this means that the first temperature and ocean heat uptake
    values will always be zero and the last value in the input drivers has no
    effect on model output.
    """

    _du_unit = "m"
    _heat_capacity_upper_unit = "J/delta_degC/m^2"
    _heat_capacity_lower_unit = "J/delta_degC/m^2"
    _dl_unit = "m"
    _lambda0_unit = "W/m^2/delta_degC"
    _a_unit = "W/m^2/delta_degC^2"
    _efficacy_unit = "dimensionless"
    _eta_unit = "W/m^2/delta_degC"
    _delta_t_unit = "s"

    _erf_unit = "W/m^2"

    _temp_upper_unit = "delta_degC"
    _temp_lower_unit = "delta_degC"
    _rndt_unit = "W/m^2"

    _save_paras = (  # parameters to save when doing a run
        "du",
        "dl",
        "lambda0",
        "a",
        "efficacy",
        "eta",
    )

    _name = "two_layer"  # model name

    def __init__(
        self,
        du=50 * ur("m"),
        dl=1200 * ur("m"),
        lambda0=3.74 / 3 * ur("W/m^2/delta_degC"),
        a=0.0 * ur("W/m^2/delta_degC^2"),
        efficacy=1.0 * ur("dimensionless"),
        eta=0.8 * ur("W/m^2/delta_degC"),
        delta_t=ur("yr").to("s"),
    ):  # pylint: disable=too-many-arguments
        """
        Initialise
        """
        self.du = du
        self.dl = dl
        self.lambda0 = lambda0
        self.a = a
        self.efficacy = efficacy
        self.eta = eta
        self.delta_t = delta_t

        self._erf = np.zeros(1) * np.nan
        self._temp_upper_mag = np.zeros(1) * np.nan
        self._temp_lower_mag = np.zeros(1) * np.nan
        self._rndt_mag = np.zeros(1) * np.nan
        self._timestep_idx = np.nan

    @property
    def du(self):
        """
        :obj:`pint.Quantity`
            Depth of upper layer
        """
        return self._du

    @du.setter
    def du(self, val):
        self._assert_is_pint_quantity_with_units(val, "du", self._du_unit)
        self._du = val
        self._du_mag = val.to(self._du_unit).magnitude
        self._heat_capacity_upper_mag = self.heat_capacity_upper.to(
            self._heat_capacity_upper_unit
        ).magnitude

    @property
    def heat_capacity_upper(self):
        """
        :obj:`pint.Quantity`
            Heat capacity of upper layer
        """
        return self.du * DENSITY_WATER * HEAT_CAPACITY_WATER

    @property
    def dl(self):
        """
        :obj:`pint.Quantity`
            Depth of lower layer
        """
        return self._dl

    @dl.setter
    def dl(self, val):
        self._assert_is_pint_quantity_with_units(val, "dl", self._dl_unit)
        self._dl = val
        self._dl_mag = val.to(self._dl_unit).magnitude
        self._heat_capacity_lower_mag = self.heat_capacity_lower.to(
            self._heat_capacity_lower_unit
        ).magnitude

    @property
    def heat_capacity_lower(self):
        """
        :obj:`pint.Quantity`
            Heat capacity of lower layer
        """
        return self.dl * DENSITY_WATER * HEAT_CAPACITY_WATER

    @property
    def lambda0(self):
        """
        :obj:`pint.Quantity`
            Initial climate feedback factor
        """
        return self._lambda0

    @lambda0.setter
    def lambda0(self, val):
        self._assert_is_pint_quantity_with_units(val, "lambda0", self._lambda0_unit)
        self._lambda0 = val
        self._lambda0_mag = val.to(self._lambda0_unit).magnitude

    @property
    def a(self):
        """
        :obj:`pint.Quantity`
            Dependence of climate feedback factor on temperature
        """
        return self._a

    @a.setter
    def a(self, val):
        self._assert_is_pint_quantity_with_units(val, "a", self._a_unit)
        self._a = val
        self._a_mag = val.to(self._a_unit).magnitude

    @property
    def efficacy(self):
        """
        :obj:`pint.Quantity`
            Efficacy factor
        """
        return self._efficacy

    @efficacy.setter
    def efficacy(self, val):
        self._assert_is_pint_quantity_with_units(val, "efficacy", self._efficacy_unit)
        self._efficacy = val
        self._efficacy_mag = val.to(self._efficacy_unit).magnitude

    @property
    def eta(self):
        """
        :obj:`pint.Quantity`
            Heat transport efficiency
        """
        return self._eta

    @eta.setter
    def eta(self, val):
        self._assert_is_pint_quantity_with_units(val, "eta", self._eta_unit)
        self._eta = val
        self._eta_mag = val.to(self._eta_unit).magnitude

    def _reset(self):
        if np.isnan(self.erf).any():
            raise ModelStateError(
                "The model's drivers have not been set yet, call "
                ":meth:`self.set_drivers` first."
            )

        self._timestep_idx = np.nan
        self._temp_upper_mag = np.zeros_like(self._erf_mag) * np.nan
        self._temp_lower_mag = np.zeros_like(self._erf_mag) * np.nan
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
            self._temp_upper_mag[self._timestep_idx] = 0.0
            self._temp_lower_mag[self._timestep_idx] = 0.0
            self._rndt_mag[self._timestep_idx] = 0.0

        else:
            self._temp_upper_mag[self._timestep_idx] = self._calculate_next_temp_upper(
                self._delta_t_mag,
                self._temp_upper_mag[self._timestep_idx - 1],
                self._temp_lower_mag[self._timestep_idx - 1],
                self._erf_mag[self._timestep_idx - 1],
                self._lambda0_mag,
                self._a_mag,
                self._efficacy_mag,
                self._eta_mag,
                self._heat_capacity_upper_mag,
            )

            self._temp_lower_mag[self._timestep_idx] = self._calculate_next_temp_lower(
                self._delta_t_mag,
                self._temp_lower_mag[self._timestep_idx - 1],
                self._temp_upper_mag[self._timestep_idx - 1],
                self._eta_mag,
                self._heat_capacity_lower_mag,
            )

            self._rndt_mag[self._timestep_idx] = self._calculate_next_rndt(
                self._delta_t_mag,
                self._temp_lower_mag[self._timestep_idx],
                self._temp_lower_mag[self._timestep_idx - 1],
                self._heat_capacity_lower_mag,
                self._temp_upper_mag[self._timestep_idx],
                self._temp_upper_mag[self._timestep_idx - 1],
                self._heat_capacity_upper_mag,
            )

    @staticmethod
    def _calculate_next_temp_upper(  # pylint: disable=too-many-arguments
        delta_t, t_upper, t_lower, erf, lambda0, a, efficacy, eta, heat_capacity_upper
    ):
        lambda_now = lambda0 - a * t_upper
        heat_exchange = efficacy * eta * (t_upper - t_lower)
        dT_dt = (erf - lambda_now * t_upper - heat_exchange) / heat_capacity_upper

        return t_upper + delta_t * dT_dt

    @staticmethod
    def _calculate_next_temp_lower(
        delta_t, t_lower, t_upper, eta, heat_capacity_lower
    ):  # pylint: disable=too-many-arguments
        heat_exchange = eta * (t_upper - t_lower)
        dT_dt = heat_exchange / heat_capacity_lower

        return t_lower + delta_t * dT_dt

    @staticmethod
    def _calculate_next_rndt(  # pylint: disable=too-many-arguments
        delta_t,
        t_lower_now,
        t_lower_prev,
        heat_capacity_lower,
        t_upper_now,
        t_upper_prev,
        heat_capacity_upper,
    ):
        uptake_lower = heat_capacity_lower * (t_lower_now - t_lower_prev) / delta_t
        uptake_upper = heat_capacity_upper * (t_upper_now - t_upper_prev) / delta_t

        return uptake_upper + uptake_lower

    def _get_run_output_tss(self, ts_base):
        out_run_tss = []

        out_run_tss.append(
            self._create_ts(
                base=ts_base,
                unit=self._temp_upper_unit,
                variable="Surface Temperature|Upper",
                values=self._temp_upper_mag,
            )
        )
        out_run_tss.append(
            self._create_ts(
                base=ts_base,
                unit=self._temp_lower_unit,
                variable="Surface Temperature|Lower",
                values=self._temp_lower_mag,
            )
        )
        out_run_tss.append(
            self._create_ts(
                base=ts_base,
                unit=self._rndt_unit,
                variable="Heat Uptake",
                values=self._rndt_mag,
            )
        )

        return out_run_tss

    def get_impulse_response_parameters(self):  # pylint:disable=missing-return-doc
        """
        Get equivalent two-timescale impulse response model parameters

        For details on how the equivalence is calculated, please see the notebook
        ``impulse-response-equivalence.ipynb`` in the `OpenSCM Two Layer model
        repository <github.com/openscm/openscm-twolayermodel>`_.

        Returns
        -------
        dict of str : :obj:`pint.Quantity`
            Input arguments to initialise an
            :obj:`openscm_twolayermodel.ImpulseResponseModel` with the same
            temperature response as ``self``

        Raises
        ------
        ValueError
            ``self.a`` is non-zero, the two-timescale model does not support
            state-dependence.
        """
        if not np.equal(self.a.magnitude, 0):
            raise ValueError(
                "Cannot calculate impulse response parameters with "
                "non-zero a={}".format(self.a)
            )

        gh = _calculate_geoffroy_helper_parameters(
            self.du, self.dl, self.lambda0, self.efficacy, self.eta
        )

        d1 = gh["tau1"]
        d2 = gh["tau2"]

        qdenom = gh["C"] * (gh["phi2"] - gh["phi1"])
        q1 = gh["tau1"] * gh["phi2"] / qdenom
        q2 = -gh["tau2"] * gh["phi1"] / qdenom

        out = {
            "d1": d1,
            "d2": d2,
            "q1": q1,
            "q2": q2,
            "efficacy": self.efficacy,
        }

        return out
