import numpy as np
import numpy.testing as npt
import pytest
from openscm_units import unit_registry
from scmdata.run import ScmRun

from openscm_twolayermodel import ImpulseResponseModel, TwoLayerModel


@pytest.mark.parametrize(
    "two_layer_config",
    (
        {},
        {"efficacy": 1.2 * unit_registry("dimensionless")},
        {"lambda_0": 3.74 / 5 * unit_registry("W/m^2/delta_degC")},
    ),
)
def test_two_layer_impulse_response_equivalence(two_layer_config):
    time = np.arange(1750, 2501)
    forcing = 0.3 * np.sin(time / 15 * 2 * np.pi) + 3.0 * time / time.max()

    inp = ScmRun(
        data=forcing,
        index=time,
        columns={
            "scenario": "test_scenario",
            "model": "unspecified",
            "climate_model": "junk input",
            "variable": "Effective Radiative Forcing",
            "unit": "W/m^2",
            "region": "World",
        },
    )

    twolayer = TwoLayerModel(**two_layer_config)
    res_twolayer = twolayer.run_scenarios(inp)

    impulse_response = ImpulseResponseModel(
        **twolayer.get_impulse_response_parameters()
    )
    res_impulse_response = impulse_response.run_scenarios(inp)

    assert (res_twolayer["time"] == res_impulse_response["time"]).all()

    npt.assert_allclose(
        res_twolayer.filter(variable="Effective Radiative Forcing").values,
        res_impulse_response.filter(variable="Effective Radiative Forcing").values,
    )
    npt.assert_allclose(
        res_twolayer.filter(variable="Heat Uptake").values,
        res_impulse_response.filter(variable="Heat Uptake").values,
        atol=0.1,  # numerical errors?
    )
    npt.assert_allclose(
        res_twolayer.filter(variable="Surface Temperature|Upper").values,
        res_impulse_response.filter(variable="Surface Temperature").values,
        atol=0.1,  # numerical errors?
    )
