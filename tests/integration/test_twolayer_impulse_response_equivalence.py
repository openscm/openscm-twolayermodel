import numpy as np
import numpy.testing as npt
import pytest
from openscm_units import unit_registry

from openscm_twolayermodel import ImpulseResponseModel, TwoLayerModel


@pytest.mark.parametrize("two_layer_config", (
    {},
    {"efficacy": 1.2},
    {"gamma": 3.4},
))
def test_two_layer_impulse_response_equivalence(two_layer_config):
    time = np.arange(1750, 2501)
    forcing = (
        0.3 * np.sin(time / 15 * 2 * np.pi)
        + 3.0 * time / time.max()
    ) * unit_registry("W/m^2")

    twolayer = TwoLayerModel(**two_layer_config)
    res_twolayer = twolayer.run(forcing)

    impulse_response = ImpulseResponseModel(
        nboxes=2,
        **twolayer.get_impulse_response_values()
    )
    res_impulse_response = impulse_response.run(forcing)

    npt.assert_allclose(res_twolayer, res_impulse_response)



# To test:
# - can't get impulse response parameters if you have non-zero state-dependence
