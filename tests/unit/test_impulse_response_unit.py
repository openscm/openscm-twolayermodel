import numpy as np
import numpy.testing as npt
from openscm_units import unit_registry as ur
from test_model_base import TwoLayerVariantTester

from openscm_twolayermodel import ImpulseResponseModel, TwoLayerModel
from openscm_twolayermodel.constants import density_water, heat_capacity_water


class TestImpulseResponseModel(TwoLayerVariantTester):
    tmodel = ImpulseResponseModel

    parameters = dict(
        q1=0.33 * ur("delta_degC/(W/m^2)"),
        q2=0.41 * ur("delta_degC/(W/m^2)"),
        d1=239.0 * ur("yr"),
        d2=4.1 * ur("yr"),
        efficacy=1.0 * ur("dimensionless"),
        delta_t=1 * ur("yr"),
    )

    def test_init(self):
        init_kwargs = dict(
            q1=0.3 * ur("delta_degC/(W/m^2)"),
            q2=0.4 * ur("delta_degC/(W/m^2)"),
            d1=250.0 * ur("yr"),
            d2=3 * ur("yr"),
            efficacy=1.1 * ur("dimensionless"),
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
        ttemp_1 = 1.1
        ttemp_2 = 0.6
        tq1 = 0.5
        tq2 = 0.3
        td1 = 30
        td2 = 600
        terf = 1.2
        tefficacy = 1.13

        res = self.tmodel._calculate_next_rndt(ttemp_1, ttemp_2, terf, tq1, tq2, td1, td2, tefficacy)

        helper = self.tmodel(
            q1=tq1 * ur("delta_degC/(W/m^2)"),
            q2=tq2 * ur("delta_degC/(W/m^2)"),
            d1=td1 * ur("yr"),
            d2=td2 * ur("yr"),
            efficacy=tefficacy * ur("dimensionless"),
        )
        helper_twolayer = TwoLayerModel(**self.tmodel.get_two_layer_parameters())

        C = helper_twolayer.heat_capacity_upper
        C_D = helper_twolayer.heat_capacity_lower

        b_pt_1 = (helper_twolayer.lambda_0 + helper_twolayer.efficacy * helper_twolayer.eta) / (C)
        b_pt_2 = (helper_twolayer.eta) / (C_D)
        b = b_pt_1 + b_pt_2
        b_star = b_pt_1 - b_pt_2
        delta = b**2 - (4 * helper_twolayer.lambda_0 * helper_twolayer.eta) / (C * C_D)

        phicoeff = C / (2 * helper_twolayer.epsilon * helper_twolayer.eta)
        phi1 = phicoeff * (b_star - delta**0.5)
        phi2 = phicoeff * (b_star + delta**0.5)
        # see notebook for discussion of why this is so
        efficacy_term = (
            helper_twolayer.eta
            * (helper_twolayer.efficacy - 1)
            * (
                (1 - phi1) * ttemp_1 * ur("delta_degC")
                - (1 - phi2) * ttemp_2 * ur("delta_degC")
            )
        )
        expected = (
            terf
            - (ttemp_1 + ttemp_2) * helper_twolayer.lambda_0
            - efficacy_term
        ).magnitude

        npt.assert_allclose(res, expected)

        # check internal units make sense
        check_same_unit(self.tmodel._q1_unit, self.tmodel._q2_unit)
        check_same_unit(helper_twolayer._lambda_0_unit, self.tmodel._q2_unit)
        check_same_unit(
            self.tmodel._erf_unit,
            (
                (
                    1.0 * ur(self.tmodel._temp1_unit) / (1.0 * ur(self.tmodel._q1_unit))
                ).units
            ),
        )
        check_same_unit(
            self.tmodel._erf_unit,
            efficacy_term.units,
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

    def test_get_two_layer_model_parameters(self, check_equal_pint):
        tq1=0.3 * ur("delta_degC/(W/m^2)")
        tq2=0.4 * ur("delta_degC/(W/m^2)")
        td1=3 * ur("yr")
        td2=300.0 * ur("yr")
        tefficacy=1.2 * ur("dimensionless")

        start_paras = dict(
            d1=td1,
            d2=td2,
            q1=tq1,
            q2=tq2,
            efficacy=tefficacy,
        )

        mod_instance = self.tmodel(**start_paras)

        # for explanation of what is going on, see
        # impulse-response-equivalence.ipynb
        efficacy = tefficacy
        lambda_0 = 1 / (tq1 + tq2)
        C = (td1 * td2) / (tq1 * td2 + tq2 * td1)

        a1 = lambda_0 * tq1
        a2 = lambda_0 * tq2
        tau1 = td1
        tau2 = td2

        C_D = (lambda_0 * (tau1 * a1 + tau2 * a2) - C) / efficacy
        eta = C_D / (tau1 * a2 + tau2 * a1)

        expected = {
            "lambda_0": lambda_0,
            "du": C / (density_water * heat_capacity_water),
            "dl": C_D / (density_water * heat_capacity_water),
            "eta": eta,
            "efficacy": efficacy,
        }

        res = mod_instance.get_two_layer_parameters()

        assert res == expected

        # check circularity
        circular_params = TwoLayerModel(**res).get_impulse_response_parameters()
        for k, v in circular_params.items():
            check_equal_pint(v, start_paras[k])
