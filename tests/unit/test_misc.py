import warnings

import numpy as np
import pytest
from conftest import assert_pint_equal, assert_same_unit
from openscm_units import unit_registry


def test_pint_array_comparison():
    a = np.array([0, 2]) * unit_registry("GtC")
    b = np.array([0, 2]) * unit_registry("MtC")

    # no error but does raise warning about stripping units
    with warnings.catch_warnings(record=True):
        np.testing.assert_allclose(a, b)

    # actually gives an error as we want
    with pytest.raises(AssertionError):
        assert_pint_equal(a, b)


@pytest.mark.parametrize(
    "unit_1,unit_2,error",
    (("g", "kg", True), ("W", "J/yr", True), ("W", "J/s", False),),
)
@pytest.mark.parametrize("unit_1_type", (str, "pint_unit"))
@pytest.mark.parametrize("unit_2_type", (str, "pint_unit"))
def test_assert_same_unit(unit_1, unit_2, error, unit_1_type, unit_2_type):
    if unit_1_type == "pint_unit":
        unit_1 = unit_registry(unit_1)

    if unit_2_type == "pint_unit":
        unit_2 = unit_registry(unit_2)

    if error:
        with pytest.raises(AssertionError):
            assert_same_unit(unit_1, unit_2)
    else:
        assert_same_unit(unit_1, unit_2)
