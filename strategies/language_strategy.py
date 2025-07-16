from tools.evaluate_code_file import CodeEvaluator


class LanguageStrategy:
    """
    A strategy for handling language-specific evaluation.
    """

    def __init__(self, config, language):
        self.evaluator = CodeEvaluator(config)
        self.language = language

    def evaluate_code(self, file_path, region_tag, github_link):
        """
        Evaluates the code in the given file.
        """
        return self.evaluator.execute(file_path, self.language, region_tag, github_link)
