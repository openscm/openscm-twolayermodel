from openscm_units import unit_registry
from test_model_base import ModelTester

from openscm_twolayermodel import TwoLayerModel


class TestTwoLayerModel(ModelTester):
    tmodel = TwoLayerModel

    parameters = dict(
        du=40 * unit_registry("m"),
        dl=1300 * unit_registry("m"),
        lambda_0=-3.4 / 3 * unit_registry("W/m^2/delta_degC"),
        a=0.01 * unit_registry("W/m^2/delta_degC^2"),
        efficacy=1.1 * unit_registry("dimensionless"),
        eta=0.7 * unit_registry("W/m^2/K"),
    )

    def test_init(self):
        init_kwargs = dict(
            du=10 * unit_registry("m"),
            dl=2200 * unit_registry("m"),
            lambda_0=-4 / 3 * unit_registry("W/m^2/delta_degC"),
            a=0.1 * unit_registry("W/m^2/delta_degC^2"),
            efficacy=1.1 * unit_registry("dimensionless"),
            eta=0.7 * unit_registry("W/m^2/K"),
        )

        res = self.tmodel(**init_kwargs)

        for k, v in init_kwargs.items():
            assert getattr(res, k) == v, "{} not set properly".format(k)
