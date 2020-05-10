from abc import abstractmethod

import pint
import pint.errors

from .errors import UnitError


class Model:
    @staticmethod
    def _check_is_pint_quantity(quantity, name, model_units):
        if not isinstance(quantity, pint.Quantity):
            raise TypeError("{} must be a pint.Quantity".format(name))

        try:
            quantity.to(model_units)
        except pint.errors.DimensionalityError as e:
            raise UnitError("Wrong units for `{}`. {}".format(name, e))

    @abstractmethod
    def set_drivers(self, *args, **kwargs):
        """
        Set the model's drivers
        """
        pass

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
