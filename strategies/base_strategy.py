from abc import ABC, abstractmethod

class BaseLanguageStrategy(ABC):
    """
    An abstract base class for language-specific strategies.
    """

    @abstractmethod
    def get_file_extensions(self):
        """
        Returns a list of file extensions for this language.
        """
        pass

    @abstractmethod
    def evaluate_code(self, file_path):
        """
        Evaluates the code in the given file.
        """
        pass
