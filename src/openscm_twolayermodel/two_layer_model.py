import numpy as np
import pandas as pd
import pint.errors
import tqdm.autonotebook as tqdman
from openscm_units import unit_registry as ur
from scmdata.run import ScmRun
from scmdata.timeseries import TimeSeries

from .base import Model
from .errors import ModelStateError, UnitError


class TwoLayerModel(Model):
    """
    TODO: top line

    This implementation uses a forward-differencing approach. This means that
    temperature and ocean heat uptake values are start of timestep values. For
    example, temperature[i] is only affected by drivers from the i-1 timestep.
    In practice, this means that the first temperature and ocean heat uptake
    values will always be zero and the last value in the input drivers has no
    effect on model output.
    """

    density_water = 1000 * ur("kg/m^3")
    """:obj:`pint.Quantity` : density of water"""

    heat_capacity_water = 4181 * ur("J/delta_degC/kg")
    """:obj:`pint.Quantity` : heat capacity of water"""

    _du_unit = "m"
    _heat_capacity_upper_unit = "J/delta_degC/m^2"
    _heat_capacity_lower_unit = "J/delta_degC/m^2"
    _dl_unit = "m"
    _lambda_0_unit = "W/m^2/delta_degC"
    _a_unit = "W/m^2/delta_degC^2"
    _efficacy_unit = "dimensionless"
    _eta_unit = "W/m^2/delta_degC"
    _delta_t_unit = "s"

    _erf_unit = "W/m^2"

    _temp_upper_unit = "delta_degC"
    _temp_lower_unit = "delta_degC"
    _rndt_unit = "W/m^2"

    def __init__(
        self,
        du=50 * ur("m"),
        dl=1200 * ur("m"),
        lambda_0=-3.74 / 3 * ur("W/m^2/delta_degC"),
        a=0.0 * ur("W/m^2/delta_degC^2"),
        efficacy=1.0 * ur("dimensionless"),
        eta=0.8 * ur("W/m^2/delta_degC"),
        delta_t=ur("yr").to("s"),
    ):
        """
        Initialise
        """
        self.du = du
        self.dl = dl
        self.lambda_0 = lambda_0
        self.a = a
        self.efficacy = efficacy
        self.eta = eta
        self.delta_t = delta_t

        self._erf = np.zeros(1) * np.nan
        self._temp_upper_mag = np.zeros(1) * np.nan
        self._temp_lower_mag = np.nan
        self._rndt_mag = np.zeros(1) * np.nan

    @property
    def du(self):
        """
        :obj:`pint.Quantity`
            Depth of upper layer
        """
        return self._du

    @du.setter
    def du(self, val):
        self._check_is_pint_quantity(val, "du", self._du_unit)
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
        return self.du * self.density_water * self.heat_capacity_water

    @property
    def dl(self):
        """
        :obj:`pint.Quantity`
            Depth of lower layer
        """
        return self._dl

    @dl.setter
    def dl(self, val):
        self._check_is_pint_quantity(val, "dl", self._dl_unit)
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
        return self.dl * self.density_water * self.heat_capacity_water

    @property
    def lambda_0(self):
        """
        :obj:`pint.Quantity`
            Initial climate feedback factor
        """
        return self._lambda_0

    @lambda_0.setter
    def lambda_0(self, val):
        self._check_is_pint_quantity(val, "lambda_0", self._lambda_0_unit)
        self._lambda_0 = val
        self._lambda_0_mag = val.to(self._lambda_0_unit).magnitude

    @property
    def a(self):
        """
        :obj:`pint.Quantity`
            Dependence of climate feedback factor on temperature
        """
        return self._a

    @a.setter
    def a(self, val):
        self._check_is_pint_quantity(val, "a", self._a_unit)
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
        self._check_is_pint_quantity(val, "efficacy", self._efficacy_unit)
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
        self._check_is_pint_quantity(val, "eta", self._eta_unit)
        self._eta = val
        self._eta_mag = val.to(self._eta_unit).magnitude

    @property
    def delta_t(self):
        """
        :obj:`pint.Quantity`
            Time step for forward-differencing approximation
        """
        return self._delta_t

    @delta_t.setter
    def delta_t(self, val):
        self._check_is_pint_quantity(val, "delta_t", self._delta_t_unit)
        self._delta_t = val
        self._delta_t_mag = val.to(self._delta_t_unit).magnitude

    @property
    def erf(self):
        """
        :obj:`pint.Quantity`
            Effective radiative forcing
        """
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
        if len(erf.shape) != 1:
            raise AssertionError("erf must be one-dimensional")

        self.erf = erf

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
                self._lambda_0_mag,
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
    def _calculate_next_temp_upper(
        delta_t, t_upper, t_lower, erf, lambda_0, a, efficacy, eta, heat_capacity_upper
    ):
        lambda_now = lambda_0 + a * t_upper
        heat_exchange = efficacy * eta * (t_upper - t_lower)
        dT_dt = (erf + lambda_now * t_upper - heat_exchange) / heat_capacity_upper

        return t_upper + delta_t * dT_dt

    @staticmethod
    def _calculate_next_temp_lower(delta_t, t_lower, t_upper, eta, heat_capacity_lower):
        heat_exchange = eta * (t_upper - t_lower)
        dT_dt = heat_exchange / heat_capacity_lower

        return t_lower + delta_t * dT_dt

    @staticmethod
    def _calculate_next_rndt(
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

    def run_scenarios(self, scenarios, driver_var="Effective Radiative Forcing"):
        """
        Run scenarios.

        The model timestep is automatically adjusted based on the timestep used in ``scenarios``.
        The timestep used in ``scenarios`` must be constant because this implementation
        has a constant timestep. Pull requests to upgrade the implementation to support
        variable timesteps are welcome `<https://github.com/openscm/openscm-twolayermodel/pulls>`_.

        Parameters
        ----------
        scenarios : :obj:`ScmDataFrame` or :obj:`ScmRun` or :obj:`pyam.IamDataFrame` or :obj:`pd.DataFrame` or :obj:`np.ndarray` or str
            Scenarios to run. The input will be converted to an :obj:`ScmRun` before
            the run takes place.

        driver_var : str
            The variable in ``scenarios`` to use as the driver of the model

        Returns
        -------
        :obj:`ScmRun`
            Results of the run (including drivers)
        """
        # TODO: put something like this in base
        if not isinstance(scenarios, ScmRun):
            driver = ScmRun(scenarios)
        else:
            driver = scenarios.copy()

        save_paras = (
            "du",
            "dl",
            "lambda_0",
            "a",
            "efficacy",
            "eta",
        )
        save_paras_meta = {
            "{} ({})".format(k, getattr(self, k).units): getattr(self, k).magnitude
            for k in save_paras
        }

        driver = driver.filter(variable=driver_var, region="World")
        if np.equal(driver.shape[0], 0):
            raise ValueError(
                "No World data available for driver_var `{}`".format(driver_var)
            )

        driver.set_meta("two_layer", "climate_model")
        for k, v in save_paras_meta.items():
            driver.set_meta(v, k)

        timestep = self._select_timestep(driver)
        self.delta_t = timestep

        out = []

        driver_ts = driver.timeseries()
        for i, (label, row) in tqdman.tqdm(enumerate(driver_ts.iterrows())):
            # TODO: ask Jared if there's a way to do this without going via
            #       timeseries but that still drops nans
            meta = {k: v for k, v in zip(driver_ts.index.names, label)}

            row_no_nan = row.dropna()
            ts = TimeSeries(data=row_no_nan.values, time=row_no_nan.index, attrs=meta)

            self.set_drivers(ts.values * ur(ts.meta["unit"]))
            self.reset()
            self.run()

            # TODO: ask Jared how we can handle this better
            out_run_tss = [ts]

            out_run_tss.append(
                self._create_ts(
                    base=ts,
                    unit=self._temp_upper_unit,
                    variable="Surface Temperature|Upper",
                    values=self._temp_upper_mag,
                )
            )
            out_run_tss.append(
                self._create_ts(
                    base=ts,
                    unit=self._temp_lower_unit,
                    variable="Surface Temperature|Lower",
                    values=self._temp_lower_mag,
                )
            )
            out_run_tss.append(
                self._create_ts(
                    base=ts,
                    unit=self._rndt_unit,
                    variable="Heat Uptake",
                    values=self._rndt_mag,
                )
            )

            out_run = ScmRun(row_no_nan, columns=meta)
            out_run._ts = out_run_tss
            out_run = ScmRun(out_run.timeseries())
            out_run.set_meta(i, "run_idx")
            out.append(out_run)

        idx = out[0].meta.columns.tolist()

        def get_ordered_timeseries(in_ts):
            in_ts = in_ts.reorder_levels(idx)

            return in_ts

        out = ScmRun(
            pd.concat([get_ordered_timeseries(r.timeseries()) for r in out], axis=0)
        )

        return out

    @staticmethod
    def _create_ts(base, unit, variable, values):
        out = base.copy()
        out.meta["unit"] = unit
        out.meta["variable"] = variable
        out[:] = values

        return out

    @staticmethod
    def _select_timestep(driver):
        year_diff = driver["year"].diff().dropna()
        if (year_diff == 1).all():
            # assume yearly timesteps
            return 1 * ur("yr")

        time_diff = driver["time"].diff().dropna()
        if all(
            np.logical_and(
                time_diff <= np.timedelta64(31, "D"),
                time_diff >= np.timedelta64(28, "D"),
            )
        ):
            # Assume constant monthly timesteps. This is clearly an approximation but
            # while we have constant internal timesteps it's the best we can do.
            return 1 * ur("month")

        raise NotImplementedError(
            "Could not decide on timestep for time axis: {}".format(driver["time"])
        )