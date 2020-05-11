"""
Module containing the base for model implementations
"""
from abc import ABC, abstractmethod

import pint
import pint.errors

from .errors import UnitError


class Model(ABC):
    """
    Base class for model implementations
    """

    @staticmethod
    def _check_is_pint_quantity(quantity, name, model_units):
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
        self._check_is_pint_quantity(val, "delta_t", self._delta_t_unit)
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
        self._check_is_pint_quantity(val, "erf", self._erf_unit)
        self._erf = val
        self._erf_mag = val.to(self._erf_unit).magnitude

    @property
    def erf(self):
        """
        :obj:`pint.Quantity`
            Effective radiative forcing
        """
        return self._erf

    @erf.setter
    def erf(self, val):
        self._check_is_pint_quantity(val, "erf", self._erf_unit)
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
