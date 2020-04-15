import numpy.testing as npt
import pytest


from openscm_twolayermodel.utils import convert_lambda_to_ecs


@pytest.mark.parametrize("ecs", (1.1, 2, 3, 5.4))
@pytest.mark.parametrize("f2x", (None, 3, 3.5, 4))
def test_convert_lambda_to_ecs(ecs, f2x):
    default_f2x = 3.74

    call_kwargs = {}
    if f2x is None:
        f2x_expected = default_f2x
    else:
        f2x_expected = f2x
        call_kwargs["f2x"] = f2x

    test_ecs = 3

    npt.assert_allclose(convert_lambda_to_ecs(-f2x_expected / ecs, **call_kwargs), ecs)
