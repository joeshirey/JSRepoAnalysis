from .base_strategy import BaseLanguageStrategy
from tools.evaluate_code_file import evaluate_code

class JavascriptStrategy(BaseLanguageStrategy):
    """
    A strategy for handling JavaScript and TypeScript files.
    """

    def get_file_extensions(self):
        return [".js", ".ts"]

    def evaluate_code(self, file_path):
        return evaluate_code(file_path, "Javascript")
