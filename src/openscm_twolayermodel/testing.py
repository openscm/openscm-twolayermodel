import re
from abc import ABC, abstractmethod
from unittest.mock import MagicMock

import numpy as np
import pint.errors
import pytest
from openscm_units import unit_registry as ur
from scmdata import ScmRun

from openscm_twolayermodel.errors import ModelStateError, UnitError


class ModelTester(ABC):
    tmodel = None

    parameters = None

    @abstractmethod
    def test_init(self):
        """
        Test the model initialises as intended
        """
        pass

    def test_init_no_units(self):
        """
        Test error thrown if the model is initiliased with a unitless
        quantity
        """
        for parameter in self.parameters.keys():
            error_msg = f"{parameter} must be a pint.Quantity"
            with pytest.raises(TypeError, match=error_msg):
                self.tmodel(**{parameter: 34.3})

    @abstractmethod
    def test_init_wrong_units(self):
        """
        Test error thrown if the model is initiliased with wrong units
        for a quantity
        """
        # e.g.
        for parameter, value in self.parameters.items():
            error_msg = f"{parameter} units must be {value.units}"
            with pytest.raises(TypeError, match=error_msg):
                self.tmodel(**{parameter: 34.3 * ur("kg")})

    def test_run(self):
        test = self.tmodel()
        test.step = MagicMock()
        test.run()

        test.step.assert_called()


class TwoLayerVariantTester(ModelTester):
    def test_init_wrong_units(self):
        helper = self.tmodel()

        for parameter in self.parameters.keys():
            tinp = 34.3 * ur("kg")
            default = getattr(helper, parameter)

            try:
                tinp.to(default.units)
            except pint.errors.DimensionalityError:
                pass

            error_msg = re.escape(f"Wrong units for `{parameter}`")
            with pytest.raises(UnitError, match=error_msg):
                self.tmodel(**{parameter: tinp})

    def test_set_erf(self, check_equal_pint):
        terf = np.array([0, 1, 2]) * ur("W/m^2")

        res = self.tmodel()
        res.erf = terf

        check_equal_pint(res.erf, terf)

    def test_set_erf_unitless_error(self, check_equal_pint):
        terf = np.array([0, 1, 2])

        res = self.tmodel()
        with pytest.raises(TypeError, match="erf must be a pint.Quantity"):
            res.erf = terf

    def test_reset_not_set_error(self):
        error_msg = "The model's drivers have not been set yet, call :meth:`self.set_drivers` first."
        with pytest.raises(ModelStateError, match=error_msg):
            self.tmodel().reset()


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
        inp_other_unit *= 10**-3
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
