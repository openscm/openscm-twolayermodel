OpenSCM Two Layer Model
=======================

+----------------+-----------------+
| |CI CD|        | |PyPI Install|  |
+----------------+-----------------+
| |PyPI|         | |PyPI Version|  |
+----------------+-----------------+
| |JOSS|         |                 |
+----------------+-----------------+


Brief summary
+++++++++++++

.. sec-begin-long-description
.. sec-begin-index

OpenSCM two layer model contains implementations of the two layer radiative forcing driven models by `Held et al. <https://journals.ametsoc.org/doi/full/10.1175/2009JCLI3466.1>`_, `Geoffroy et al. <https://journals.ametsoc.org/doi/pdf/10.1175/JCLI-D-12-00195.1>`_ and `Bloch-Johnson et al. <https://agupubs.onlinelibrary.wiley.com/doi/abs/10.1002/2015GL064240>`_

OpenSCM Two Layer Model was designed to provide a clean, modularised, extensible interface for one of the most commonly used simple climate models.
It was used in `Phase 1 of the Reduced Complexity Model Intercomparison Project <https://doi.org/10.5194/gmd-13-5175-2020>`_ as a point of comparison for the other participating models.

The `FaIR model <https://github.com/OMS-NetZero/FAIR>`_ implements a mathematically equivalent model (under certain assumptions) but does not provide as clear a conversion between the two-layer model and the two-timescale response as is provided here.
We hope that this implementation could interface with other simple climate models like FaIR to allow simpler exploration of the combined behaviour of interacting climate components with minimal coupling headaches.

As implemented here, the "OpenSCM Two Layer Model" interface is target at researchers and as an education tool.
Users from other fields are of course encouraged to use it if they find it helpful.

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

    pip install "openscm-twolayermodel[notebooks]"

**Coming soon** OpenSCM two layer model can also be installed with conda

.. code:: bash

    conda install -c conda-forge openscm-twolayermodel

We do not ship our tests with the packages.
If you wish to run the tests, you must install from source (or download the tests separately and run them on your installation).

Installing from source
~~~~~~~~~~~~~~~~~~~~~~

To install from source, simply clone the repository and then install it using pip e.g. ``pip install .``.
Having done this, the tests can be run with ``pytest tests`` or using the ``Makefile`` (``make test`` will run only the code tests, ``make checks`` will run the code tests and all other tests e.g. linting, notebooks, documentation).

.. sec-end-installation

For more details, see the `development section of the docs <https://openscm-two-layer-model.readthedocs.io/en/latest/development.html>`_.

Documentation
-------------

Documentation can be found at our `documentation pages <https://openscm-two-layer-model.readthedocs.io/en/latest/>`_
(we are thankful to `Read the Docs <https://readthedocs.org/>`_ for hosting us).

Contributing
------------

Please see the `Development section of the docs <https://openscm-two-layer-model.readthedocs.io/en/latest/development.html>`_.

.. sec-begin-links

.. |CI CD| image:: https://github.com/openscm/openscm-twolayermodel/workflows/OpenSCM%20Two%20Layer%20Model%20CI-CD/badge.svg
    :target: https://github.com/openscm/openscm-twolayermodel/actions?query=workflow%3A%22OpenSCM+Two+Layer+Model+CI-CD%22
.. |PyPI Install| image:: https://github.com/openscm/openscm-twolayermodel/workflows/Test%20PyPI%20install/badge.svg
    :target: https://github.com/openscm/openscm-twolayermodel/actions?query=workflow%3A%22Test+PyPI+install%22
.. |PyPI| image:: https://img.shields.io/pypi/pyversions/openscm-twolayermodel.svg
    :target: https://pypi.org/project/openscm-twolayermodel/
.. |PyPI Version| image:: https://img.shields.io/pypi/v/openscm-twolayermodel.svg
    :target: https://pypi.org/project/openscm-twolayermodel/
.. |JOSS| image:: https://joss.theoj.org/papers/94a3759c9ea117499b90c56421ef4857/status.svg
    :target: https://joss.theoj.org/papers/94a3759c9ea117499b90c56421ef4857

.. sec-end-links
