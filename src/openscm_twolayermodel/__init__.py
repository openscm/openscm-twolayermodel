"""
Implementations of the two layer radiative forcing driven models by [Held et al.](https://journals.ametsoc.org/doi/full/10.1175/2009JCLI3466.1) and [Geoffroy et al.](https://journals.ametsoc.org/doi/pdf/10.1175/JCLI-D-12-00195.1)
"""
import importlib.metadata

__version__ = importlib.metadata.version("openscm_twolayermodel")

from .impulse_response_model import ImpulseResponseModel  # noqa: F401
from .two_layer_model import TwoLayerModel  # noqa: F401
