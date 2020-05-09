"""
OpenSCM Two Layer Model, implementations of the two layer radiative forcing driven models by `Held et al. <https://journals.ametsoc.org/doi/full/10.1175/2009JCLI3466.1>`_ and `Geoffroy et al. <https://journals.ametsoc.org/doi/pdf/10.1175/JCLI-D-12-00195.1>`_.

See README and docs for more info.
"""

from ._version import get_versions
from .impulse_response_model import ImpulseResponseModel  # noqa
from .two_layer_model import TwoLayerModel  # noqa

__version__ = get_versions()["version"]
del get_versions
