from .base_strategy import BaseLanguageStrategy
from tools.evaluate_code_file import CodeEvaluator

class PythonStrategy(BaseLanguageStrategy):
    """
    A strategy for handling Python files.
    """

    def __init__(self, config):
        self.evaluator = CodeEvaluator(config)

    def get_file_extensions(self):
        return [".py"]

    def evaluate_code(self, file_path):
        return self.evaluator.execute(file_path, "Python")
