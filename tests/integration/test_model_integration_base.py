from abc import ABC, abstractmethod


class ModelIntegrationTester(ABC):
    tmodel = None

    @abstractmethod
    def test_run_scenarios_single(self):
        """
        Test the model can run a single scenario correctly
        """
        pass

    @abstractmethod
    def test_run_scenarios_multiple(self):
        """
        Test the model can run multiple scenarios correctly
        """
        pass
