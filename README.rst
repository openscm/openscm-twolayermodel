OpenSCM Two Layer Model
==============

+----------------+-----------------+
| |CI CD|        | |PyPI Install|  |
+----------------+-----------------+
| |PyPI|         | |PyPI Version|  |
+----------------+-----------------+

Work in progress.

Brief summary
+++++++++++++

.. sec-begin-long-description
.. sec-begin-index

OpenSCM two layer model contains implementations of the two layer radiative forcing driven models by `Held et al. <https://journals.ametsoc.org/doi/full/10.1175/2009JCLI3466.1>`_ and `Geoffroy et al. <https://journals.ametsoc.org/doi/pdf/10.1175/JCLI-D-12-00195.1>`_.
[TODO, find reference which has the state-dependent feedback factor..]

.. sec-end-index

License
-------

.. sec-begin-license

OpenSCM two layer model is free software under a BSD 3-Clause License, see
`LICENSE <https://github.com/openscm/openscm-twolayermodel/blob/master/LICENSE>`_.

.. sec-end-license
.. sec-end-long-description

.. sec-begin-installation

Installation
------------

OpenSCM two layer model can be installed with pip

.. code:: bash

    pip install openscm-twolayermodel

If you also want to run the example notebooks install additional
dependencies using

.. code:: bash

    pip install openscm-twolayermodel[notebooks]

**Coming soon** OpenSCM two layer model can also be installed with conda

.. code:: bash

    conda install -c conda-forge openscm-twolayermodel

.. sec-end-installation

Documentation
-------------

Documentation can be found at our `documentation pages <https://openscm-twolayermodel.readthedocs.io/en/latest/>`_
(we are thankful to `Read the Docs <https://readthedocs.org/>`_ for hosting us).

Contributing
------------

Please see the `Development section of the docs <https://openscm-twolayermodel.readthedocs.io/en/latest/development.html>`_.

.. sec-begin-links

.. |CI CD| image:: https://github.com/openscm/openscm-twolayermodel/workflows/openscm-twolayermodel%20CI-CD/badge.svg
    :target: https://github.com/openscm/openscm-twolayermodel/actions?query=workflow%3A%22OpenSCM two layer model+CI-CD%22
.. |PyPI Install| image:: https://github.com/openscm/openscm-twolayermodel/workflows/Test%20PyPI%20install/badge.svg
    :target: https://github.com/openscm/openscm-twolayermodel/actions?query=workflow%3A%22Test+PyPI+install%22
.. |PyPI| image:: https://img.shields.io/pypi/pyversions/openscm-twolayermodel.svg
    :target: https://pypi.org/project/openscm-twolayermodel/
.. |PyPI Version| image:: https://img.shields.io/pypi/v/openscm-twolayermodel.svg
    :target: https://pypi.org/project/openscm-twolayermodel/

.. sec-end-links
