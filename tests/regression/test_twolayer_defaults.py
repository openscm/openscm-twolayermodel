import os.path

import pytest
from openscm_units import unit_registry as ur

from openscm_twolayermodel import TwoLayerModel


def test_twolayer_defaults(
    update_expected_files,
    test_rcmip_forcings_scmrun,
    test_twolayer_output_dir,
    run_model_output_comparison,
):
    twolayer_default = TwoLayerModel()
    res = twolayer_default.run_scenarios(test_rcmip_forcings_scmrun)

    expected = os.path.join(test_twolayer_output_dir, "test_twolayer_defaults.csv")

    run_model_output_comparison(res, expected, update_expected_files)


def test_twolayer_plus_efficacy(
    update_expected_files,
    test_rcmip_forcings_scmrun,
    test_twolayer_output_dir,
    run_model_output_comparison,
):
    twolayer_plus_efficacy = TwoLayerModel(efficacy=1.2 * ur("dimensionless"))
    res = twolayer_plus_efficacy.run_scenarios(test_rcmip_forcings_scmrun)

    expected = os.path.join(test_twolayer_output_dir, "test_twolayer_plus_efficacy.csv")

    run_model_output_comparison(res, expected, update_expected_files)


@pytest.mark.filterwarnings("ignore:overflow encountered")
@pytest.mark.filterwarnings("ignore:invalid value encountered")
def test_twolayer_plus_state_dependence(
    update_expected_files,
    test_rcmip_forcings_scmrun,
    test_twolayer_output_dir,
    run_model_output_comparison,
):
    twolayer_plus_state_dependence = TwoLayerModel(a=0.05 * ur("W/m^2/delta_degC^2"))
    res = twolayer_plus_state_dependence.run_scenarios(test_rcmip_forcings_scmrun)

    expected = os.path.join(
        test_twolayer_output_dir, "test_twolayer_plus_state_dependence.csv"
    )

    run_model_output_comparison(res, expected, update_expected_files)
