from .base_strategy import BaseLanguageStrategy
from tools.evaluate_code_file import evaluate_code

class PythonStrategy(BaseLanguageStrategy):
    """
    A strategy for handling Python files.
    """

    def get_file_extensions(self):
        return [".py"]

    def evaluate_code(self, file_path):
        return evaluate_code(file_path, "Python")
