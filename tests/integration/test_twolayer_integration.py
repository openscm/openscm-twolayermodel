import numpy as np
import numpy.testing as npt
import pytest
from openscm_units import unit_registry as ur
from scmdata import ScmRun
from test_model_integration_base import TwoLayerVariantIntegrationTester

from openscm_twolayermodel import TwoLayerModel


class TestTwoLayerModel(TwoLayerVariantIntegrationTester):

    tmodel = TwoLayerModel

    def test_run_scenarios_single(self):
        inp = self.tinp.copy()

        model = self.tmodel()

        res = model.run_scenarios(inp)

        model.set_drivers(
            inp.values.squeeze() * ur(inp.get_unique_meta("unit", no_duplicates=True))
        )
        model.reset()
        model.run()

        npt.assert_allclose(
            res.filter(variable="Surface Temperature|Upper").values.squeeze(),
            model._temp_upper_mag,
        )
        assert (
            res.filter(variable="Surface Temperature|Upper").get_unique_meta(
                "unit", no_duplicates=True
            )
            == "delta_degC"
        )

        npt.assert_allclose(
            res.filter(variable="Surface Temperature|Lower").values.squeeze(),
            model._temp_lower_mag,
        )
        assert (
            res.filter(variable="Surface Temperature|Lower").get_unique_meta(
                "unit", no_duplicates=True
            )
            == "delta_degC"
        )

        npt.assert_allclose(
            res.filter(variable="Heat Uptake").values.squeeze(), model._rndt_mag
        )
        assert (
            res.filter(variable="Heat Uptake").get_unique_meta(
                "unit", no_duplicates=True
            )
            == "W/m^2"
        )

    def test_run_scenarios_multiple(self):
        ts1_erf = np.linspace(0, 4, 101)
        ts2_erf = np.sin(np.linspace(0, 4, 101))

        inp = ScmRun(
            data=np.vstack([ts1_erf, ts2_erf]).T,
            index=np.linspace(1750, 1850, 101).astype(int),
            columns={
                "scenario": ["test_scenario_1", "test_scenario_2"],
                "model": "unspecified",
                "climate_model": "junk input",
                "variable": "Effective Radiative Forcing",
                "unit": "W/m^2",
                "region": "World",
            },
        )

        model = self.tmodel()

        res = model.run_scenarios(inp)

        for scenario_ts in inp.groupby("scenario"):
            scenario = scenario_ts.get_unique_meta("scenario", no_duplicates=True)

            model.set_drivers(
                scenario_ts.values.squeeze()
                * ur(inp.get_unique_meta("unit", no_duplicates=True))
            )
            model.reset()
            model.run()

            res_scen = res.filter(scenario=scenario)

            npt.assert_allclose(
                res_scen.filter(variable="Surface Temperature|Upper").values.squeeze(),
                model._temp_upper_mag,
            )
            assert (
                res.filter(variable="Surface Temperature|Upper").get_unique_meta(
                    "unit", no_duplicates=True
                )
                == "delta_degC"
            )

            npt.assert_allclose(
                res_scen.filter(variable="Surface Temperature|Lower").values.squeeze(),
                model._temp_lower_mag,
            )
            assert (
                res.filter(variable="Surface Temperature|Lower").get_unique_meta(
                    "unit", no_duplicates=True
                )
                == "delta_degC"
            )

            npt.assert_allclose(
                res_scen.filter(variable="Heat Uptake").values.squeeze(),
                model._rndt_mag,
            )
            assert (
                res.filter(variable="Heat Uptake").get_unique_meta(
                    "unit", no_duplicates=True
                )
                == "W/m^2"
            )

    @pytest.mark.parametrize(
        "driver_var",
        ("Effective Radiative Forcing", "Effective Radiative Forcing|CO2",),
    )
    def test_run_scenarios_multiple_drive_var(self, driver_var):
        ts1_erf = np.linspace(0, 4, 101)
        ts1_erf_co2 = 0.9 * ts1_erf
        ts2_erf = np.sin(np.linspace(0, 4, 101))
        ts2_erf_co2 = np.cos(np.linspace(0, 4, 101)) * ts2_erf

        inp = ScmRun(
            data=np.vstack([ts1_erf, ts1_erf_co2, ts2_erf, ts2_erf_co2]).T,
            index=np.linspace(1750, 1850, 101).astype(int),
            columns={
                "scenario": [
                    "test_scenario_1",
                    "test_scenario_1",
                    "test_scenario_2",
                    "test_scenario_2",
                ],
                "model": "unspecified",
                "climate_model": "junk input",
                "variable": [
                    "Effective Radiative Forcing",
                    "Effective Radiative Forcing|CO2",
                    "Effective Radiative Forcing",
                    "Effective Radiative Forcing|CO2",
                ],
                "unit": "W/m^2",
                "region": "World",
            },
        )

        model = self.tmodel()

        res = model.run_scenarios(inp, driver_var=driver_var)

        for scenario_ts in inp.groupby("scenario"):
            scenario = scenario_ts.get_unique_meta("scenario", no_duplicates=True)

            driver = scenario_ts.filter(variable=driver_var)
            model.set_drivers(
                driver.values.squeeze()
                * ur(inp.get_unique_meta("unit", no_duplicates=True))
            )
            model.reset()
            model.run()

            res_scen = res.filter(scenario=scenario)

            npt.assert_allclose(
                res_scen.filter(variable="Surface Temperature|Upper").values.squeeze(),
                model._temp_upper_mag,
            )
            assert (
                res.filter(variable="Surface Temperature|Upper").get_unique_meta(
                    "unit", no_duplicates=True
                )
                == "delta_degC"
            )

            npt.assert_allclose(
                res_scen.filter(variable="Surface Temperature|Lower").values.squeeze(),
                model._temp_lower_mag,
            )
            assert (
                res.filter(variable="Surface Temperature|Lower").get_unique_meta(
                    "unit", no_duplicates=True
                )
                == "delta_degC"
            )

            npt.assert_allclose(
                res_scen.filter(variable="Heat Uptake").values.squeeze(),
                model._rndt_mag,
            )
            assert (
                res.filter(variable="Heat Uptake").get_unique_meta(
                    "unit", no_duplicates=True
                )
                == "W/m^2"
            )

    def test_run_scenario_timestep_followed(self, check_equal_pint):
        inp = self.tinp.copy()

        model = self.tmodel()

        res = model.run_scenarios(inp)
        check_equal_pint(model.delta_t, 1 * ur("yr"))

        inp_monthly = inp.resample("MS")
        res_monthly = model.run_scenarios(inp_monthly)
        check_equal_pint(model.delta_t, 1 * ur("month"))

        comp_filter = {
            "variable": "Surface Temperature|Upper",
            "year": int(
                res["year"].iloc[-1]
            ),  # scmdata bug that you have to wrap this with int()
            "month": 1,
        }

        # running with two different timesteps should give approximately same results
        npt.assert_allclose(
            res.filter(**comp_filter).values.squeeze(),
            res_monthly.filter(**comp_filter).values.squeeze(),
            rtol=1e-3,
        )
        res.filter(variable="Surface Temperature|Upper")
