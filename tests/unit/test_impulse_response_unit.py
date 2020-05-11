import numpy as np
from openscm_units import unit_registry as ur
from test_model_base import TwoLayerVariantTester

from openscm_twolayermodel import ImpulseResponseModel
from openscm_twolayermodel.errors import ModelStateError, UnitError


class TestImpulseResponseModel(TwoLayerVariantTester):
    tmodel = ImpulseResponseModel

    parameters = dict(
        q1=0.33 * ur("delta_degC/W/m^2"),
        q2=0.41 * ur("delta_degC/W/m^2"),
        d1=239.0 * ur("yr"),
        d2=4.1 * ur("yr"),
        delta_t=1 * ur("yr"),
    )

    def test_init(self):
        init_kwargs = dict(
            q1=0.3 * ur("delta_degC/W/m^2"),
            q2=0.4 * ur("delta_degC/W/m^2"),
            d1=250.0 * ur("yr"),
            d2=3 * ur("yr"),
            delta_t=1/12 * ur("yr"),
        )

        res = self.tmodel(**init_kwargs)

        for k, v in init_kwargs.items():
            assert getattr(res, k) == v, "{} not set properly".format(k)

        assert np.isnan(res.erf)
        assert np.isnan(res._temp1_mag)
        assert np.isnan(res._temp2_mag)
        assert np.isnan(res._rndt_mag)
