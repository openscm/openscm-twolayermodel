from abc import ABC, abstractmethod
from unittest.mock import MagicMock

import pytest
from openscm_units import unit_registry as ur


class ModelIntegrationTester(ABC):
    tmodel = None

    @abstractmethod
    def test_run_scenarios(self):
        """
        Test the model can run scenarios
        """
        pass
