from abc import ABC, abstractmethod

import pytest
from openscm_units import unit_registry


class ModelTester:
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
