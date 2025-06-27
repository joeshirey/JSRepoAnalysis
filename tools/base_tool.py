from abc import ABC, abstractmethod

class BaseTool(ABC):
    """
    An abstract base class for tools that perform a specific action.
    """

    @abstractmethod
    def execute(self, *args, **kwargs):
        """
        Executes the tool's action.
        """
        pass
