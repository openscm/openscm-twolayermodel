from abc import ABC, abstractmethod

import numpy as np
import pytest
from scmdata import ScmRun

from openscm_twolayermodel.errors import UnitError


class ModelIntegrationTester(ABC):
    tmodel = None

    @abstractmethod
    def test_run_scenarios_single(self):
        """
        Test the model can run a single scenario correctly
        """
        pass

    @abstractmethod
    def test_run_scenarios_multiple(self):
        """
        Test the model can run multiple scenarios correctly
        """
        pass


class TwoLayerVariantIntegrationTester(ModelIntegrationTester):

    tinp = ScmRun(
        data=np.linspace(0, 4, 101),
        index=np.linspace(1750, 1850, 101).astype(int),
        columns={
            "scenario": "test_scenario",
            "model": "unspecified",
            "climate_model": "junk input",
            "variable": "Effective Radiative Forcing",
            "unit": "W/m^2",
            "region": "World",
        },
    )

    def test_run_unit_handling(self, check_scmruns_allclose):
        inp = self.tinp.copy()

        model = self.tmodel()

        res = model.run_scenarios(inp)

        # scmdata bug
        # inp.convert_unit("kW/m^2") blows up
        inp_other_unit = inp.copy()
        inp_other_unit *= 10 ** -3
        inp_other_unit["unit"] = "kW/m^2"
        res_other_unit = model.run_scenarios(inp_other_unit)

        assert res.get_unique_meta("climate_model", no_duplicates=True) == model._name

        check_scmruns_allclose(
            res.filter(variable="Effective Radiative Forcing", keep=False),
            res_other_unit.filter(variable="Effective Radiative Forcing", keep=False),
        )

    def test_run_wrong_units(self):
        inp = self.tinp.copy()
        inp["unit"] = "W"

        model = self.tmodel()

        with pytest.raises(UnitError):
            model.run_scenarios(inp)

    def test_run_wrong_region(self):
        inp = self.tinp.copy()
        inp["region"] = "World|R5LAM"

        model = self.tmodel()

        error_msg = (
            "No World data available for driver_var `Effective Radiative Forcing`"
        )

        with pytest.raises(ValueError, match=error_msg):
            model.run_scenarios(inp)

    def test_run_wrong_driver(self):
        inp = self.tinp.copy()

        model = self.tmodel()

        error_msg = (
            "No World data available for driver_var `Effective Radiative Forcing|CO2`"
        )

        with pytest.raises(ValueError, match=error_msg):
            model.run_scenarios(inp, driver_var="Effective Radiative Forcing|CO2")
