# OpenSCM Two Layer Model

<!---
Can use start-after and end-before directives in docs, see
https://myst-parser.readthedocs.io/en/latest/syntax/organising_content.html#inserting-other-documents-directly-into-the-current-document
-->

<!--- sec-begin-description -->

Implementations of the two layer radiative forcing driven models by [Held et al.](https://journals.ametsoc.org/doi/full/10.1175/2009JCLI3466.1) and [Geoffroy et al.](https://journals.ametsoc.org/doi/pdf/10.1175/JCLI-D-12-00195.1)



[![CI](https://github.com/openscm/openscm-twolayermodel/actions/workflows/ci.yaml/badge.svg?branch=main)](https://github.com/openscm/openscm-twolayermodel/actions/workflows/ci.yaml)
[![Coverage](https://codecov.io/gh/openscm/openscm-twolayermodel/branch/main/graph/badge.svg)](https://codecov.io/gh/openscm/openscm-twolayermodel)
[![Docs](https://readthedocs.org/projects/openscm-twolayermodel/badge/?version=latest)](https://openscm-twolayermodel.readthedocs.io)

**PyPI :**
[![PyPI](https://img.shields.io/pypi/v/openscm-twolayermodel.svg)](https://pypi.org/project/openscm-twolayermodel/)
[![PyPI: Supported Python versions](https://img.shields.io/pypi/pyversions/openscm-twolayermodel.svg)](https://pypi.org/project/openscm-twolayermodel/)
[![PyPI install](https://github.com/openscm/openscm-twolayermodel/actions/workflows/install.yaml/badge.svg?branch=main)](https://github.com/openscm/openscm-twolayermodel/actions/workflows/install.yaml)

**Other info :**
[![Licence](https://img.shields.io/github/license/openscm/openscm-twolayermodel.svg)](https://github.com/openscm/openscm-twolayermodel/blob/main/LICENCE)
[![Last Commit](https://img.shields.io/github/last-commit/openscm/openscm-twolayermodel.svg)](https://github.com/openscm/openscm-twolayermodel/commits/main)
[![Contributors](https://img.shields.io/github/contributors/openscm/openscm-twolayermodel.svg)](https://github.com/openscm/openscm-twolayermodel/graphs/contributors)


<!--- sec-end-description -->

Full documentation can be found at:
[openscm-twolayermodel.readthedocs.io](https://openscm-twolayermodel.readthedocs.io/en/latest/).
We recommend reading the docs there because the internal documentation links
don't render correctly on GitHub's viewer.

## Installation

<!--- sec-begin-installation -->

OpenSCM Two Layer Model can be installed with pip, mamba or conda:

```bash
pip install openscm-twolayermodel
mamba install -c conda-forge openscm-twolayermodel
conda install -c conda-forge openscm-twolayermodel
```

Additional dependencies can be installed using

```bash
# To add notebook dependencies
pip install openscm-twolayermodel[notebooks]

# If you are installing with conda, we recommend
# installing the extras by hand because there is no stable
# solution yet (issue here: https://github.com/conda/conda/issues/7502)
```

<!--- sec-end-installation -->

### For developers

<!--- sec-begin-installation-dev -->

For development, we rely on [poetry](https://python-poetry.org) for all our
dependency management. To get started, you will need to make sure that poetry
is installed
([instructions here](https://python-poetry.org/docs/#installing-with-the-official-installer),
we found that pipx and pip worked better to install on a Mac).

For all of work, we use our `Makefile`.
You can read the instructions out and run the commands by hand if you wish,
but we generally discourage this because it can be error prone.
In order to create your environment, run `make virtual-environment`.

If there are any issues, the messages from the `Makefile` should guide you
through. If not, please raise an issue in the
[issue tracker](https://github.com/openscm/openscm-twolayermodel/issues).

For the rest of our developer docs, please see [](development-reference).

<!--- sec-end-installation-dev -->
