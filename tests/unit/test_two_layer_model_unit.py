import re

import numpy as np
import numpy.testing as npt
import pint.errors
import pytest
from openscm_units import unit_registry as ur
from test_model_base import TwoLayerVariantTester

from openscm_twolayermodel import TwoLayerModel
from openscm_twolayermodel.errors import ModelStateError, UnitError


class TestTwoLayerModel(TwoLayerVariantTester):
    tmodel = TwoLayerModel

    parameters = dict(
        du=40 * ur("m"),
        dl=1300 * ur("m"),
        lambda_0=-3.4 / 3 * ur("W/m^2/delta_degC"),
        a=0.01 * ur("W/m^2/delta_degC^2"),
        efficacy=1.1 * ur("dimensionless"),
        eta=0.7 * ur("W/m^2/delta_degC"),
        delta_t=1 * ur("yr"),
    )

    def test_init(self):
        init_kwargs = dict(
            du=10 * ur("m"),
            dl=2200 * ur("m"),
            lambda_0=-4 / 3 * ur("W/m^2/delta_degC"),
            a=0.1 * ur("W/m^2/delta_degC^2"),
            efficacy=1.1 * ur("dimensionless"),
            eta=0.7 * ur("W/m^2/delta_degC"),
            delta_t=1 / 12 * ur("yr"),
        )

        res = self.tmodel(**init_kwargs)

        for k, v in init_kwargs.items():
            assert getattr(res, k) == v, "{} not set properly".format(k)

        assert np.isnan(res.erf)
        assert np.isnan(res._temp_upper_mag)
        assert np.isnan(res._temp_lower_mag)
        assert np.isnan(res._rndt_mag)

    def test_heat_capacity_upper(self, check_equal_pint):
        model = self.tmodel(du=50000 * ur("mm"))

        expected = model.du * model.density_water * model.heat_capacity_water

        res = model.heat_capacity_upper

        check_equal_pint(res, expected)
        assert (
            model._heat_capacity_upper_mag
            == res.to(model._heat_capacity_upper_unit).magnitude
        )

    def test_heat_capacity_upper_no_setter(self):
        model = self.tmodel()
        with pytest.raises(AttributeError, match="can't set attribute"):
            model.heat_capacity_upper = 4

    def test_heat_capacity_lower(self, check_equal_pint):
        model = self.tmodel(dl=2.5 * ur("km"))

        expected = model.dl * model.density_water * model.heat_capacity_water

        res = model.heat_capacity_lower

        check_equal_pint(res, expected)
        assert (
            model._heat_capacity_lower_mag
            == res.to(model._heat_capacity_lower_unit).magnitude
        )

    def test_heat_capacity_lower_no_setter(self):
        model = self.tmodel()
        with pytest.raises(AttributeError, match="can't set attribute"):
            model.heat_capacity_lower = 4

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

    def test_calculate_next_temp_upper(self, check_same_unit):
        tdelta_t = 30 * 24 * 60 * 60
        ttemp_upper = 0.1
        ttemp_lower = 0.2
        terf = 1.1
        tlambda_0 = -3.7 / 3
        ta = 0.02
        tefficacy = 0.9
        teta = 0.78
        theat_capacity_upper = 10 ** 10

        res = self.tmodel._calculate_next_temp_upper(
            tdelta_t,
            ttemp_upper,
            ttemp_lower,
            terf,
            tlambda_0,
            ta,
            tefficacy,
            teta,
            theat_capacity_upper,
        )

        expected = (
            ttemp_upper
            + tdelta_t
            * (
                terf
                + (tlambda_0 + ta * ttemp_upper) * ttemp_upper
                - (tefficacy * teta * (ttemp_upper - ttemp_lower))
            )
            / theat_capacity_upper
        )

        npt.assert_equal(res, expected)

        # check internal units make sense
        check_same_unit(
            self.tmodel._lambda_0_unit,
            (
                1.0 * ur(self.tmodel._a_unit) * 1.0 * ur(self.tmodel._temp_upper_unit)
            ).units,
        )

        check_same_unit(
            self.tmodel._erf_unit,
            (
                1.0
                * ur(self.tmodel._lambda_0_unit)
                * 1.0
                * ur(self.tmodel._temp_upper_unit)
            ).units,
        )

        check_same_unit(
            self.tmodel._erf_unit,
            (
                1.0
                * ur(self.tmodel._efficacy_unit)
                * 1.0
                * ur(self.tmodel._eta_unit)
                * 1.0
                * ur(self.tmodel._temp_upper_unit)
            ).units,
        )

        check_same_unit(
            self.tmodel._temp_upper_unit,
            (
                1.0
                * ur(self.tmodel._delta_t_unit)
                * 1.0
                * ur(self.tmodel._erf_unit)
                / (1.0 * ur(self.tmodel._heat_capacity_upper_unit))
            ).units,
        )

    def test_calculate_next_temp_lower(self, check_same_unit):
        tdelta_t = 30 * 24 * 60 * 60
        ttemp_upper = 0.1
        ttemp_lower = 0.2
        teta = 0.78
        theat_capacity_lower = 10 ** 8

        res = self.tmodel._calculate_next_temp_lower(
            tdelta_t, ttemp_lower, ttemp_upper, teta, theat_capacity_lower
        )

        expected = ttemp_lower + (
            tdelta_t * teta * (ttemp_upper - ttemp_lower) / theat_capacity_lower
        )

        npt.assert_equal(res, expected)

        # check internal units make sense
        check_same_unit(
            self.tmodel._temp_upper_unit, self.tmodel._temp_lower_unit,
        )
        check_same_unit(
            self.tmodel._temp_lower_unit,
            (
                1.0
                * ur(self.tmodel._delta_t_unit)
                * 1.0
                * ur(self.tmodel._eta_unit)
                * 1.0
                * ur(self.tmodel._temp_upper_unit)
                / (1.0 * ur(self.tmodel._heat_capacity_upper_unit))
            ).units,
        )

    def test_calculate_next_rndt(self, check_same_unit):
        tdelta_t = 30 * 24 * 60 * 60
        ttemp_upper_t = 0.1
        ttemp_lower_t = 0.2
        ttemp_upper_t_prev = 0.09
        ttemp_lower_t_prev = 0.18
        theat_capacity_upper = 10 ** 10
        theat_capacity_lower = 10 ** 8

        res = self.tmodel._calculate_next_rndt(
            tdelta_t,
            ttemp_lower_t,
            ttemp_lower_t_prev,
            theat_capacity_lower,
            ttemp_upper_t,
            ttemp_upper_t_prev,
            theat_capacity_upper,
        )

        expected = (
            theat_capacity_upper * (ttemp_upper_t - ttemp_upper_t_prev)
            + theat_capacity_lower * (ttemp_lower_t - ttemp_lower_t_prev)
        ) / tdelta_t

        npt.assert_allclose(res, expected)

        # check internal units make sense
        check_same_unit(
            self.tmodel._temp_upper_unit, self.tmodel._temp_lower_unit,
        )
        check_same_unit(
            (
                (
                    1.0
                    * ur(self.tmodel._heat_capacity_lower_unit)
                    * 1.0
                    * ur(self.tmodel._temp_lower_unit)
                ).units
            ),
            (
                1.0
                * ur(self.tmodel._heat_capacity_upper_unit)
                * 1.0
                * ur(self.tmodel._temp_upper_unit)
            ).units,
        )
        check_same_unit(
            self.tmodel._rndt_unit,
            (
                1.0
                * ur(self.tmodel._heat_capacity_upper_unit)
                * 1.0
                * ur(self.tmodel._temp_upper_unit)
                / (1.0 * ur(self.tmodel._delta_t_unit))
            ).units,
        )

    def test_step(self):
        # move to integration tests
        terf = np.array([3, 4, 5, 6, 7]) * ur("W/m^2")

        model = self.tmodel()
        model.set_drivers(terf)
        model.reset()

        model.step()
        assert model._timestep_idx == 0
        npt.assert_equal(model._temp_upper_mag[model._timestep_idx], 0)
        npt.assert_equal(model._temp_lower_mag[model._timestep_idx], 0)
        npt.assert_equal(model._rndt_mag[model._timestep_idx], 0)

        model.step()
        model.step()
        model.step()
        assert model._timestep_idx == 3

        npt.assert_equal(
            model._temp_upper_mag[model._timestep_idx],
            model._calculate_next_temp_upper(
                model._delta_t_mag,
                model._temp_upper_mag[model._timestep_idx - 1],
                model._temp_lower_mag[model._timestep_idx - 1],
                model._erf_mag[model._timestep_idx - 1],
                model._lambda_0_mag,
                model._a_mag,
                model._efficacy_mag,
                model._eta_mag,
                model._heat_capacity_upper_mag,
            ),
        )

        npt.assert_equal(
            model._temp_lower_mag[model._timestep_idx],
            model._calculate_next_temp_lower(
                model._delta_t_mag,
                model._temp_lower_mag[model._timestep_idx - 1],
                model._temp_upper_mag[model._timestep_idx - 1],
                model._eta_mag,
                model._heat_capacity_lower_mag,
            ),
        )

        npt.assert_equal(
            model._rndt_mag[model._timestep_idx],
            model._calculate_next_rndt(
                model._delta_t_mag,
                model._temp_lower_mag[model._timestep_idx],
                model._temp_lower_mag[model._timestep_idx - 1],
                model._heat_capacity_lower_mag,
                model._temp_upper_mag[model._timestep_idx],
                model._temp_upper_mag[model._timestep_idx - 1],
                model._heat_capacity_upper_mag,
            ),
        )

    def test_reset(self):
        terf = np.array([0, 1, 2]) * ur("W/m^2")

        model = self.tmodel()
        model.set_drivers(terf)

        def assert_is_nan_and_erf_shape(inp):
            assert np.isnan(inp).all()
            assert inp.shape == terf.shape

        model.reset()
        # after reset, we are not in any timestep
        assert np.isnan(model._timestep_idx)
        assert_is_nan_and_erf_shape(model._temp_upper_mag)
        assert_is_nan_and_erf_shape(model._temp_lower_mag)
        assert_is_nan_and_erf_shape(model._rndt_mag)

    def test_reset_run_reset(self):
        # move to integration tests
        terf = np.array([0, 1, 2, 3, 4, 5]) * ur("W/m^2")

        model = self.tmodel()
        model.set_drivers(terf)

        def assert_is_nan_and_erf_shape(inp):
            assert np.isnan(inp).all()
            assert inp.shape == terf.shape

        model.reset()
        assert_is_nan_and_erf_shape(model._temp_upper_mag)
        assert_is_nan_and_erf_shape(model._temp_lower_mag)
        assert_is_nan_and_erf_shape(model._rndt_mag)

        def assert_ge_zero_and_erf_shape(inp):
            assert not (inp < 0).any()
            assert inp.shape == terf.shape

        model.run()
        assert_ge_zero_and_erf_shape(model._temp_upper_mag)
        assert_ge_zero_and_erf_shape(model._temp_lower_mag)
        assert_ge_zero_and_erf_shape(model._rndt_mag)

        model.reset()
        assert_is_nan_and_erf_shape(model._temp_upper_mag)
        assert_is_nan_and_erf_shape(model._temp_lower_mag)
        assert_is_nan_and_erf_shape(model._rndt_mag)

    def test_reset_not_set_error(self):
        error_msg = "The model's drivers have not been set yet, call :meth:`self.set_drivers` first."
        with pytest.raises(ModelStateError, match=error_msg):
            self.tmodel().reset()
