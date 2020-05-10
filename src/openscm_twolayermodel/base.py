from abc import abstractmethod

import pint
import pint.errors

from .errors import UnitsError

class Model:
    @staticmethod
    def _check_is_pint_quantity(quantity, name, model_units):
        if not isinstance(quantity, pint.Quantity):
            raise TypeError("{} must be a pint.Quantity".format(name))

        try:
            quantity.to(model_units)
        except pint.errors.DimensionalityError as e:
            raise UnitsError("Wrong units for `{}`. {}".format(name, e))

    @abstractmethod
    def set_drivers(self, *args, **kwargs):
        """
        Set the model's drivers
        """
        pass
