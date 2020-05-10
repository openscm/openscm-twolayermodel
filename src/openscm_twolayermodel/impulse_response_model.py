"""
Module containing the impulse response model

The 2-timescale impulse response model is mathematically equivalent to the
two-layer model without state dependence.
"""
from .base import Model


class ImpulseResponseModel(Model):
    """
    TODO: top line and paper references

    This implementation uses a forward-differencing approach. This means that
    temperature and ocean heat uptake values are start of timestep values. For
    example, temperature[i] is only affected by drivers from the i-1 timestep.
    In practice, this means that the first temperature and ocean heat uptake
    values will always be zero and the last value in the input drivers has no
    effect on model output.
    """
