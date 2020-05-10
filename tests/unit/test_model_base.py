from abc import ABC, abstractmethod
from unittest.mock import MagicMock

import pytest
from openscm_units import unit_registry as ur


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
