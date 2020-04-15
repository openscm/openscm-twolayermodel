import re

import numpy.testing as npt
import pytest
from openscm_units import unit_registry

from openscm_twolayermodel.utils import convert_lambda_to_ecs


@pytest.mark.parametrize("ecs", (1.1, 2, 3, 5.4))
@pytest.mark.parametrize("f2x", (3, 3.5, 4))
@pytest.mark.parametrize("test_units", ("delta_degC", "mdelta_degC"))
def test_convert_lambda_to_ecs_with_units(ecs, f2x, test_units):
    ecs = ecs * unit_registry("delta_degC")
    f2x = f2x * unit_registry("W/m^2")
    default_f2x = 3.74 * unit_registry("W/m^2")

    call_kwargs = {}
    if f2x is None:
        f2x_expected = default_f2x
    else:
        f2x_expected = f2x
        call_kwargs["f2x"] = f2x

    in_lambda = -f2x_expected / ecs
    npt.assert_allclose(
        convert_lambda_to_ecs(in_lambda, **call_kwargs).to(test_units).magnitude,
        ecs.to(test_units).magnitude,
    )


def test_convert_lambda_to_ecs_no_units_error_lambda_val():
    with pytest.raises(TypeError, match=re.escape("lambda_val is not a pint.Quantity")):
        convert_lambda_to_ecs(-1.1)


def test_convert_lambda_to_ecs_no_units_error_f2x():
    with pytest.raises(TypeError, match=re.escape("f2x is not a pint.Quantity")):
        convert_lambda_to_ecs(-1.1 * unit_registry("W/m^2/delta_degC"), f2x=3)
