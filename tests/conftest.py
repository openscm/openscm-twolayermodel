import os.path

import pandas as pd
import pytest
from scmdata.run import ScmRun


TEST_DATA_ROOT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test-data")


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
    res_df = res.timeseries().sort_index()
    assert not res_df.isnull().any().any(), "Failed sanity check"

    exp_df = expected.timeseries().sort_index()
    pd.testing.assert_frame_equal(res_df, exp_df, check_like=True)


@pytest.fixture
def run_model_output_comparison():
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
            res.to_csv(expected)
        else:
            assert_scmruns_allclose(res, ScmRun(expected))

        if update:
            pytest.skip("Updated {}".format(expected))

    return _do_comparison
