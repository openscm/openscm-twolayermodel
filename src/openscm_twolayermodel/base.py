"""
Module containing the base for model implementations
"""
from abc import ABC, abstractmethod

import numpy as np
import pandas as pd
import pint
import pint.errors
import tqdm.autonotebook as tqdman
from openscm_units import unit_registry as ur
from scmdata.run import ScmRun
from scmdata.timeseries import TimeSeries

from .constants import DENSITY_WATER, HEAT_CAPACITY_WATER
from .errors import UnitError

# pylint: disable=invalid-name


class Model(ABC):
    """
    Base class for model implementations
    """

    _save_paras = tuple()  # parameters to save when doing a run

    _name = None  # model name

    @staticmethod
    def _assert_is_pint_quantity_with_units(quantity, name, model_units):
        if not isinstance(quantity, pint.Quantity):
            raise TypeError("{} must be a pint.Quantity".format(name))

        try:
            quantity.to(model_units)
        except pint.errors.DimensionalityError as exc:
            raise UnitError("Wrong units for `{}`. {}".format(name, exc))

    @abstractmethod
    def set_drivers(self, *args, **kwargs):
        """
        Set the model's drivers
        """

    def reset(self):
        """
        Reset everything so that a new run can be performed.

        Called as late as possible before :meth:`run`.
        """
        self._reset()

    @abstractmethod
    def _reset(self):
        pass

    def run(self):
        """
        Run the model.
        """
        self._run()

    @abstractmethod
    def _run(self):
        pass

    def step(self):
        """
        Do a single time step.
        """
        self._step()

    @abstractmethod
    def _step(self):
        pass


class TwoLayerVariant(Model):
    """
    Base for variations of implementations of the two-layer model
    """

    _delta_t_unit = "s"
    _erf_unit = "W/m^2"

    @property
    def delta_t(self):
        """
        :obj:`pint.Quantity`
            Time step for forward-differencing approximation
        """
        return self._delta_t

    @delta_t.setter
    def delta_t(self, val):
        self._assert_is_pint_quantity_with_units(val, "delta_t", self._delta_t_unit)
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
        self._assert_is_pint_quantity_with_units(val, "erf", self._erf_unit)
        self._erf = val
        self._erf_mag = val.to(self._erf_unit).magnitude

    def set_drivers(
        self, erf
    ):  # pylint: disable=arguments-differ # hmm need to think about this
        """
        Set drivers for a model run

        Parameters
        ----------
        erf : :obj:`pint.Quantity`
            Effective radiative forcing (W/m^2) to use to drive the model

        Raises
        ------
        AssertionError
            ``erf`` is not one-dimensional
        """
        if len(erf.shape) != 1:
            raise AssertionError("erf must be one-dimensional")

        self.erf = erf

    @staticmethod
    def _ensure_scenarios_are_scmrun(scenarios):
        if not isinstance(scenarios, ScmRun):
            driver = ScmRun(scenarios)
        else:
            driver = scenarios.copy()

        return driver

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

    def run_scenarios(  # pylint:disable=too-many-locals
        self, scenarios, driver_var="Effective Radiative Forcing"
    ):
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

        Raises
        ------
        ValueError
            No data is available for ``driver_var`` in the ``"World"`` region in
            ``scenarios``.
        """
        driver = self._ensure_scenarios_are_scmrun(scenarios)

        save_paras_meta = {
            "{} ({})".format(k, getattr(self, k).units): getattr(self, k).magnitude
            for k in self._save_paras
        }

        driver = driver.filter(variable=driver_var, region="World")
        if np.equal(driver.shape[0], 0):
            raise ValueError(
                "No World data available for driver_var `{}`".format(driver_var)
            )

        driver["climate_model"] = self._name
        for k, v in save_paras_meta.items():
            driver[k] = v

        timestep = self._select_timestep(driver)
        self.delta_t = timestep

        run_store = list()

        driver_ts = driver.timeseries()
        for i, (label, row) in tqdman.tqdm(
            enumerate(driver_ts.iterrows()), desc="scenarios", leave=False
        ):
            # TODO: ask Jared if there's  # pylint: disable=fixme
            # a way to do this without going via timeseries but that still
            # drops nans
            meta = dict(zip(driver_ts.index.names, label))

            row_no_nan = row.dropna()
            ts = TimeSeries(data=row_no_nan.values, time=row_no_nan.index, attrs=meta)

            self.set_drivers(ts.values * ur(ts.meta["unit"]))
            self.reset()
            self.run()

            out_run_tss = [ts]
            out_run_tss += self._get_run_output_tss(ts)

            # TODO: ask Jared how we can  # pylint: disable=fixme
            # handle this better
            out_run = ScmRun(row_no_nan, columns=meta)
            out_run._ts = out_run_tss  # pylint: disable=protected-access
            out_run = ScmRun(out_run.timeseries())
            out_run["run_idx"] = i

            run_store.append(out_run)

        idx = run_store[0].meta.columns.tolist()

        def get_ordered_timeseries(in_ts):
            in_ts = in_ts.reorder_levels(idx)

            return in_ts

        out = ScmRun(
            pd.concat(
                [get_ordered_timeseries(r.timeseries()) for r in run_store], axis=0
            )
        )

        return out

    @abstractmethod
    def _get_run_output_tss(self, ts_base):
        """Get the run output timeseries as a list"""


def _calculate_geoffroy_helper_parameters(  # pylint:disable=too-many-locals
    du, dl, lambda0, efficacy, eta
):
    C = du * HEAT_CAPACITY_WATER * DENSITY_WATER
    C_D = dl * HEAT_CAPACITY_WATER * DENSITY_WATER

    b_pt1 = (lambda0 + efficacy * eta) / (C)
    b_pt2 = (eta) / (C_D)
    b = b_pt1 + b_pt2
    b_star = b_pt1 - b_pt2
    delta = b ** 2 - (4 * lambda0 * eta) / (C * C_D)

    taucoeff = C * C_D / (2 * lambda0 * eta)
    tau1 = taucoeff * (b - delta ** 0.5)
    tau2 = taucoeff * (b + delta ** 0.5)

    phicoeff = C / (2 * efficacy * eta)
    phi1 = phicoeff * (b_star - delta ** 0.5)
    phi2 = phicoeff * (b_star + delta ** 0.5)

    adenom = C * (phi2 - phi1)
    a1 = tau1 * phi2 * lambda0 / adenom
    a2 = -tau2 * phi1 * lambda0 / adenom

    out = {
        "C": C,
        "C_D": C_D,
        "b": b,
        "b_star": b_star,
        "delta": delta,
        "tau1": tau1,
        "tau2": tau2,
        "phi1": phi1,
        "phi2": phi2,
        "a1": a1,
        "a2": a2,
    }

    return out
