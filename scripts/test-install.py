"""
Test that all of our modules can be imported

Also test that associated constants are set correctly

Thanks https://stackoverflow.com/a/25562415/10473080
"""
import importlib
import pkgutil

import openscm_twolayermodel


def import_submodules(package_name):
    """
    Test import of submodules
    """
    package = importlib.import_module(package_name)

    for _, name, is_pkg in pkgutil.walk_packages(package.__path__):
        full_name = package.__name__ + "." + name
        importlib.import_module(full_name)
        if is_pkg:
            import_submodules(full_name)


import_submodules("openscm_twolayermodel")
print(openscm_twolayermodel.__version__)
