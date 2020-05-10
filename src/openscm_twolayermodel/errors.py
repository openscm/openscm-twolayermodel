"""
Exceptions raised within ``openscm_twolayermodel``
"""


class UnitError(ValueError):
    """
    Exception raised if something has the wrong units
    """


class ModelStateError(ValueError):
    """
    Exception raised if a model's state is incompatible with the action
    """
