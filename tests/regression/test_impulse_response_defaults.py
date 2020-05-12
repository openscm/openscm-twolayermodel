import os.path

from openscm_twolayermodel import ImpulseResponseModel


def test_impulse_response_defaults(
    update_expected_files,
    test_rcmip_forcings_scmrun,
    test_twolayer_output_dir,
    run_model_output_comparison,
):
    impulse_response_default = ImpulseResponseModel()
    res = impulse_response_default.run_scenarios(test_rcmip_forcings_scmrun)

    expected = os.path.join(
        test_twolayer_output_dir, "test_impulse_response_defaults.csv"
    )

    run_model_output_comparison(res, expected, update_expected_files)
