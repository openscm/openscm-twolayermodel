import numpy as np
import numpy.testing as npt
from openscm_units import unit_registry as ur
from test_model_base import TwoLayerVariantTester

from openscm_twolayermodel import ImpulseResponseModel


class TestImpulseResponseModel(TwoLayerVariantTester):
    tmodel = ImpulseResponseModel

    parameters = dict(
        q1=0.33 * ur("delta_degC/(W/m^2)"),
        q2=0.41 * ur("delta_degC/(W/m^2)"),
        d1=239.0 * ur("yr"),
        d2=4.1 * ur("yr"),
        delta_t=1 * ur("yr"),
    )

    def test_init(self):
        init_kwargs = dict(
            q1=0.3 * ur("delta_degC/(W/m^2)"),
            q2=0.4 * ur("delta_degC/(W/m^2)"),
            d1=250.0 * ur("yr"),
            d2=3 * ur("yr"),
            delta_t=1 / 12 * ur("yr"),
        )

        res = self.tmodel(**init_kwargs)

        for k, v in init_kwargs.items():
            assert getattr(res, k) == v, "{} not set properly".format(k)

        assert np.isnan(res.erf)
        assert np.isnan(res._temp1_mag)
        assert np.isnan(res._temp2_mag)
        assert np.isnan(res._rndt_mag)

    def test_calculate_next_temp(self, check_same_unit):
        tdelta_t = 30 * 24 * 60 * 60
        ttemp = 0.1
        tq = 0.4
        td = 35.0
        tf = 1.2

        res = self.tmodel._calculate_next_temp(tdelta_t, ttemp, tq, td, tf)

        expected = ttemp * np.exp(-tdelta_t / td) + tf * tq * (
            1 - np.exp(-tdelta_t / td)
        )

        npt.assert_equal(res, expected)

        check_same_unit(self.tmodel._temp1_unit, self.tmodel._temp2_unit)
        check_same_unit(self.tmodel._q1_unit, self.tmodel._q2_unit)
        check_same_unit(self.tmodel._delta_t_unit, self.tmodel._d1_unit)
        check_same_unit(self.tmodel._delta_t_unit, self.tmodel._d2_unit)
        check_same_unit(
            self.tmodel._temp1_unit,
            (1.0 * ur(self.tmodel._erf_unit) * 1.0 * ur(self.tmodel._q1_unit)).units,
        )

    def test_calculate_next_rndt(self, check_same_unit):
        ttemp = 1.1
        tq1 = 0.5
        tq2 = 0.3
        terf = 1.2

        res = self.tmodel._calculate_next_rndt(ttemp, terf, tq1, tq2,)

        # see notebook for discussion of why this is so
        expected = terf - ttemp / (tq1 + tq2)

        npt.assert_allclose(res, expected)

        # check internal units make sense
        check_same_unit(self.tmodel._q1_unit, self.tmodel._q2_unit)
        check_same_unit(
            self.tmodel._erf_unit,
            (
                (
                    1.0 * ur(self.tmodel._temp1_unit) / (1.0 * ur(self.tmodel._q1_unit))
                ).units
            ),
        )

    def test_step(self):
        # move to integration tests
        terf = np.array([3, 4, 5, 6, 7]) * ur("W/m^2")

        model = self.tmodel()
        model.set_drivers(terf)
        model.reset()

        model.step()
        assert model._timestep_idx == 0
        npt.assert_equal(model._temp1_mag[model._timestep_idx], 0)
        npt.assert_equal(model._temp2_mag[model._timestep_idx], 0)
        npt.assert_equal(model._rndt_mag[model._timestep_idx], 0)

        model.step()
        model.step()
        model.step()
        assert model._timestep_idx == 3

        npt.assert_equal(
            model._temp1_mag[model._timestep_idx],
            model._calculate_next_temp(
                model._delta_t_mag,
                model._temp1_mag[model._timestep_idx - 1],
                model._q1_mag,
                model._d1_mag,
                model._erf_mag[model._timestep_idx - 1],
            ),
        )

        npt.assert_equal(
            model._temp2_mag[model._timestep_idx],
            model._calculate_next_temp(
                model._delta_t_mag,
                model._temp2_mag[model._timestep_idx - 1],
                model._q2_mag,
                model._d2_mag,
                model._erf_mag[model._timestep_idx - 1],
            ),
        )

        npt.assert_equal(
            model._rndt_mag[model._timestep_idx],
            model._calculate_next_rndt(
                model._temp1_mag[model._timestep_idx - 1]
                + model._temp2_mag[model._timestep_idx - 1],
                model._erf_mag[model._timestep_idx - 1],
                model._q1_mag,
                model._q2_mag,
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
        assert_is_nan_and_erf_shape(model._temp1_mag)
        assert_is_nan_and_erf_shape(model._temp2_mag)
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
        assert_is_nan_and_erf_shape(model._temp1_mag)
        assert_is_nan_and_erf_shape(model._temp2_mag)
        assert_is_nan_and_erf_shape(model._rndt_mag)

        def assert_ge_zero_and_erf_shape(inp):
            assert not (inp < 0).any()
            assert inp.shape == terf.shape

        model.run()
        assert_ge_zero_and_erf_shape(model._temp1_mag)
        assert_ge_zero_and_erf_shape(model._temp2_mag)
        assert_ge_zero_and_erf_shape(model._rndt_mag)

        model.reset()
        assert_is_nan_and_erf_shape(model._temp1_mag)
        assert_is_nan_and_erf_shape(model._temp2_mag)
        assert_is_nan_and_erf_shape(model._rndt_mag)
