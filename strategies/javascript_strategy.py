from .base_strategy import BaseLanguageStrategy
from tools.evaluate_code_file import CodeEvaluator

class JavascriptStrategy(BaseLanguageStrategy):
    """
    A strategy for handling JavaScript and TypeScript files.
    """

    def __init__(self, config):
        self.evaluator = CodeEvaluator(config)

    def get_file_extensions(self):
        return [".js", ".ts"]

    def evaluate_code(self, file_path):
        return self.evaluator.execute(file_path, "Javascript")
