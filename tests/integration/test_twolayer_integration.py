import numpy as np
import numpy.testing as npt
from openscm_units import unit_registry as ur
from scmdata import ScmRun
from test_model_integration_base import ModelIntegrationTester

from openscm_twolayermodel import TwoLayerModel


class TestTwoLayerModel(ModelIntegrationTester):

    tmodel = TwoLayerModel

    def test_run_scenarios(self):
        inp = ScmRun(
            data=np.linspace(0, 4, 100),
            index=np.linspace(1750, 1850, 100).astype(int),
            columns={
                "scenario": "test_scenario",
                "model": "unspecified",
                "climate_model": "junk input",
                "variable": "Effective Radiative Forcing",
                "unit": "W/m^2",
                "region": "World",
            }
        )

        model = self.tmodel()

        res = model.run_scenarios(inp)

        model.set_drivers(inp.values * ur(inp.get_unique_meta("unit", no_duplicates=True)))
        model.reset()
        model.run()

        npt.assert_allclose(
            res.filter(variable="Surface Temperature|Upper"),
            model._temp_upper_mag
        )
        assert res.filter(variable="Surface Temperature|Upper").get_unique_meta("unit", no_duplicates=True) == "delta_degC"

        npt.assert_allclose(
            res.filter(variable="Surface Temperature|Lower"),
            model._temp_lower_mag
        )
        assert res.filter(variable="Surface Temperature|Lower").get_unique_meta("unit", no_duplicates=True) == "delta_degC"

        npt.assert_allclose(
            res.filter(variable="Heat Uptake"),
            model._rndt_mag
        )
        assert res.filter(variable="Heat Uptake").get_unique_meta("unit", no_duplicates=True) == "W/m^2"


# tests:
# - error if not World
# - error if bad units
# - error if variable not correctly pointed to (give option to specify run_variable)
