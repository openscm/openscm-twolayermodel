def convert_lambda_to_ecs(lambda_val, f2x=3.74):
    """
    Convert a lambda value to equilibrium climate sensitivity (ECS)

    Parameters
    ----------
    lambda_val : float
        Value of lambda to convert to ECS

    f2x : float
        Value of the forcing due to a doubling of atmospheric |CO2| (TODO: add |CO2 shortcut to docs)
        to assume during the conversion

    Returns
    -------
    float
        ECS value
    """
    return -f2x / lambda_val
