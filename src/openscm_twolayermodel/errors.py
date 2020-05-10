class UnitsError(ValueError):
    """
    Exception raised if something has the wrong units
    """
    pass


class ModelStateError(ValueError):
    """
    Exception raised if a model's state is incompatible with the action
    """
    pass
