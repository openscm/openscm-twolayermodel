import re
from abc import ABC, abstractmethod
from unittest.mock import MagicMock

import numpy as np
import pint.errors
import pytest
from openscm_units import unit_registry as ur

from openscm_twolayermodel.errors import UnitError


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
            error_msg = "{} must be a pint.Quantity".format(parameter)
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
            error_msg = "{} units must be {}".format(parameter, value.units)
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
            except pint.errors.DimensionalityError as e:
                pint_msg = str(e)

            error_msg = re.escape(
                "Wrong units for `{}`. {}".format(parameter, pint_msg)
            )
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
