"""
Module containing the impulse response model

The 2-timescale impulse response model is mathematically equivalent to the
two-layer model without state dependence.
"""
import numpy as np
from openscm_units import unit_registry as ur

from .base import TwoLayerVariant, _calculate_geoffroy_helper_parameters
from .constants import DENSITY_WATER, HEAT_CAPACITY_WATER
from .errors import ModelStateError

# pylint: disable=invalid-name


class ImpulseResponseModel(
    TwoLayerVariant
):  # pylint: disable=too-many-instance-attributes
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
    _efficacy_unit = "dimensionless"
    _delta_t_unit = "yr"

    _erf_unit = "W/m^2"

    _temp1_unit = "delta_degC"
    _temp2_unit = "delta_degC"
    _rndt_unit = "W/m^2"

    _save_paras = (  # parameters to save when doing a run
        "d1",
        "d2",
        "q1",
        "q2",
        "efficacy",
    )

    _name = "two_timescale_impulse_response"  # model name

    def __init__(
        self,
        q1=0.3 * ur("delta_degC/(W/m^2)"),
        q2=0.4 * ur("delta_degC/(W/m^2)"),
        d1=9.0 * ur("yr"),
        d2=400.0 * ur("yr"),
        efficacy=1.0 * ur("dimensionless"),
        delta_t=1 / 12 * ur("yr"),
    ):  # pylint: disable=too-many-arguments
        """
        Initialise

        Raises
        ------
        ValueError
            d1 >= d2, d1 must be the short-timescale
        """
        self.q1 = q1
        self.q2 = q2
        self.d1 = d1
        self.d2 = d2
        self.efficacy = efficacy
        self.delta_t = delta_t

        if d1 >= d2:
            raise ValueError("The short-timescale must be d1")

        self._erf = np.zeros(1) * np.nan
        self._temp1_mag = np.zeros(1) * np.nan
        self._temp2_mag = np.zeros(1) * np.nan
        self._rndt_mag = np.zeros(1) * np.nan
        self._timestep_idx = np.nan

    @property
    def d1(self):
        """
        :obj:`pint.Quantity`
            Response timescale of first box
        """
        return self._d1

    @d1.setter
    def d1(self, val):
        self._assert_is_pint_quantity_with_units(val, "d1", self._d1_unit)
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
        self._assert_is_pint_quantity_with_units(val, "d2", self._d2_unit)
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
        self._assert_is_pint_quantity_with_units(val, "q1", self._q1_unit)
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
        self._assert_is_pint_quantity_with_units(val, "q2", self._q2_unit)
        self._q2 = val
        self._q2_mag = val.to(self._q2_unit).magnitude

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
                self._temp1_mag[self._timestep_idx - 1],
                self._temp2_mag[self._timestep_idx - 1],
                self._erf_mag[self._timestep_idx - 1],
                self._efficacy_mag,
            )

    @staticmethod
    def _calculate_next_temp(delta_t, t, q, d, erf):
        decay_factor = np.exp(-delta_t / d)
        rise = erf * q * (1 - np.exp(-delta_t / d))

        return t * decay_factor + rise

    def _calculate_next_rndt(self, t1, t2, erf, efficacy):
        two_layer_paras = self.get_two_layer_parameters()
        lambda0 = two_layer_paras["lambda0"]

        if np.equal(efficacy, 1):
            efficacy_term = 0 * ur(self._erf_unit)
        else:
            gh = _calculate_geoffroy_helper_parameters(
                two_layer_paras["du"],
                two_layer_paras["dl"],
                two_layer_paras["lambda0"],
                two_layer_paras["efficacy"],
                two_layer_paras["eta"],
            )

            t1_h = t1 * ur(self._temp1_unit)
            t2_h = t2 * ur(self._temp2_unit)
            efficacy_term = (
                two_layer_paras["eta"]
                * (efficacy - 1)
                * ((1 - gh["phi1"]) * t1_h + (1 - gh["phi2"]) * t2_h)
            )

            if str(efficacy_term.units) != "watt / meter ** 2":
                raise AssertionError("units should have come out as W/m^2")

        out = erf - lambda0.magnitude * (t1 + t2) - efficacy_term.magnitude

        return out

    def _get_run_output_tss(self, ts_base):
        out_run_tss = []

        out_run_tss.append(
            self._create_ts(
                base=ts_base,
                unit=self._temp1_unit,
                variable="Surface Temperature|Box 1",
                values=self._temp1_mag,
            )
        )
        out_run_tss.append(
            self._create_ts(
                base=ts_base,
                unit=self._temp2_unit,
                variable="Surface Temperature|Box 2",
                values=self._temp2_mag,
            )
        )
        out_run_tss.append(
            self._create_ts(
                base=ts_base,
                unit=self._temp1_unit,
                variable="Surface Temperature",
                values=self._temp1_mag + self._temp2_mag,
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

    def get_two_layer_parameters(
        self,
    ):  # pylint:disable=missing-return-doc,missing-return-type-doc
        """
        Get equivalent two-layer model parameters

        For details on how the equivalence is calculated, please see the notebook
        ``impulse-response-equivalence.ipynb`` in the `OpenSCM Two Layer model
        repository <github.com/openscm/openscm-twolayermodel>`_.

        Returns
        -------
        dict of str : :obj:`pint.Quantity`
            Input arguments to initialise an
            :obj:`openscm_twolayermodel.TwoLayerModel` with the same
            temperature response as ``self``
        """
        lambda0 = 1 / (self.q1 + self.q2)
        C = (self.d1 * self.d2) / (self.q1 * self.d2 + self.q2 * self.d1)

        a1 = lambda0 * self.q1
        a2 = lambda0 * self.q2

        C_D = (lambda0 * (self.d1 * a1 + self.d2 * a2) - C) / self.efficacy
        eta = C_D / (self.d1 * a2 + self.d2 * a1)

        du = C / (DENSITY_WATER * HEAT_CAPACITY_WATER)
        dl = C_D / (DENSITY_WATER * HEAT_CAPACITY_WATER)

        out = {
            "lambda0": lambda0,
            "du": du,
            "dl": dl,
            "eta": eta,
            "efficacy": self.efficacy,
        }

        return out
