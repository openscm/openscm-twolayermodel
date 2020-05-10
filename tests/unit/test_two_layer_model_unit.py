import re

from openscm_units import unit_registry as ur
from test_model_base import ModelTester

import numpy as np
import numpy.testing as npt
import pint.errors
import pytest

from openscm_twolayermodel import TwoLayerModel
from openscm_twolayermodel.errors import UnitsError


class TestTwoLayerModel(ModelTester):
    tmodel = TwoLayerModel

    parameters = dict(
        du=40 * ur("m"),
        dl=1300 * ur("m"),
        lambda_0=-3.4 / 3 * ur("W/m^2/delta_degC"),
        a=0.01 * ur("W/m^2/delta_degC^2"),
        efficacy=1.1 * ur("dimensionless"),
        eta=0.7 * ur("W/m^2/K"),
        delta_t=1 * ur("yr")
    )

    def test_init(self):
        init_kwargs = dict(
            du=10 * ur("m"),
            dl=2200 * ur("m"),
            lambda_0=-4 / 3 * ur("W/m^2/delta_degC"),
            a=0.1 * ur("W/m^2/delta_degC^2"),
            efficacy=1.1 * ur("dimensionless"),
            eta=0.7 * ur("W/m^2/K"),
            delta_t=1/12 * ur("yr")
        )

        res = self.tmodel(**init_kwargs)

        for k, v in init_kwargs.items():
            assert getattr(res, k) == v, "{} not set properly".format(k)

        assert np.isnan(res.erf)

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

    def test_init_bad_units(self):
        helper = self.tmodel()

        for parameter in self.parameters.keys():
            tinp = 34.3 * ur("kg")
            default = getattr(helper, parameter)

            try:
                tinp.to(default.units)
            except pint.errors.DimensionalityError as e:
                pint_msg = str(e)

            error_msg = re.escape("Wrong units for `{}`. {}".format(parameter, pint_msg))
            with pytest.raises(UnitsError, match=error_msg):
                self.tmodel(**{parameter: tinp})
