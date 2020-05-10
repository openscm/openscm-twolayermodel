import os.path

import numpy as np
import numpy.testing as npt
import pandas as pd
import pytest
from openscm_units import unit_registry as ur
from scmdata.run import ScmRun

TEST_DATA_ROOT_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "test-data"
)


@pytest.fixture
def test_data_root_dir():
    if not os.path.isdir(TEST_DATA_ROOT_DIR):
        pytest.skip("test data required")

    return TEST_DATA_ROOT_DIR


@pytest.fixture
def test_rcmip_forcings(test_data_root_dir):
    return os.path.join(
        test_data_root_dir, "rcmip-radiative-forcing-annual-means-v4-0-0.csv"
    )


@pytest.fixture
def test_rcmip_forcings_scmrun(test_rcmip_forcings):
    return ScmRun(test_rcmip_forcings)


@pytest.fixture
def test_twolayer_output_dir(test_data_root_dir):
    return os.path.join(test_data_root_dir, "two-layer-output")


def pytest_addoption(parser):
    parser.addoption(
        "--update-expected-files",
        action="store_true",
        default=False,
        help="Overwrite expected files",
    )


@pytest.fixture
def update_expected_files(request):
    return request.config.getoption("--update-expected-files")


def assert_scmruns_allclose(res, expected):
    exp_df = expected.timeseries().sort_index()
    meta_cols = exp_df.index.names

    res_df = res.timeseries()
    res_df.index = res_df.index.reorder_levels(meta_cols)
    res_df = res_df.sort_index()

    pd.testing.assert_frame_equal(res_df, exp_df, check_like=True)


@pytest.fixture
def run_model_output_comparison(tmpdir):
    def _do_comparison(res, expected, update=False):
        """
        Run test that results match expected output

        Parameters
        ----------
        res : :obj:`ScmRun`
            Output from model run

        expected : str
            Path containing expected output

        update : bool
            If True, don't perform the test and instead simply
            overwrite ``expected`` with ``res``

        Raises
        ------
        AssertionError
            If ``update`` is ``False`` and ``res`` and ``expected``
            are not identical.
        """
        if update:
            print("Updating {}".format(expected))
            res.to_csv(expected, index=False)
        else:
            # scmdata bug: the saving and loading process mangles the column
            # names so we have to save to disk before checking
            tmpfile = os.path.join(tmpdir, "res.csv")
            res.to_csv(tmpfile, index=False)
            assert_scmruns_allclose(ScmRun(tmpfile), ScmRun(expected))

        if update:
            pytest.skip("Updated {}".format(expected))

    return _do_comparison


# temporary workaround until this is in Pint itself and can be imported
def assert_pint_equal(a, b, **kwargs):
    c = b.to(a.units)
    try:
        npt.assert_allclose(a.magnitude, c.magnitude, **kwargs)

    except AssertionError as e:
        original_msg = "{}".format(e)
        note_line = "Note: values above have been converted to {}".format(a.units)
        units_lines = "Input units:\n" "x: {}\n" "y: {}".format(a.units, b.units)

        numerical_lines = (
            "Numerical values with units:\n" "x: {}\n" "y: {}".format(a, b)
        )

        error_msg = (
            "{}\n"
            "\n"
            "{}\n"
            "\n"
            "{}\n"
            "\n"
            "{}".format(original_msg, note_line, units_lines, numerical_lines)
        )

        raise AssertionError(error_msg)


@pytest.fixture
def check_equal_pint():
    return assert_pint_equal


# temporary workaround until this is in Pint itself and can be imported
def assert_same_unit(unit_1, unit_2):
    """
    Check that conversion factor between two units is 1
    """
    assert np.equal(1 * ur(str(unit_1)).to(unit_2).magnitude, 1)


@pytest.fixture
def check_same_unit():
    return assert_same_unit
