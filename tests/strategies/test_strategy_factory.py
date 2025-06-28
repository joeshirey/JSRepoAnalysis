import unittest
from config import settings
from strategies.strategy_factory import get_strategy
from strategies.language_strategy import LanguageStrategy

class TestStrategyFactory(unittest.TestCase):

    def test_get_strategy_for_supported_languages(self):
        test_cases = {
            "test.js": "Javascript",
            "test.ts": "Typescript",
            "test.py": "Python",
            "test.java": "Java",
            "test.go": "Go",
            "test.rs": "Rust",
            "test.rb": "Ruby",
            "test.cs": "C#",
            "test.cpp": "C++",
            "test.h": "C++",
            "test.hpp": "C++",
            "test.php": "PHP",
        }

        for file_path, expected_language in test_cases.items():
            with self.subTest(file_path=file_path):
                strategy = get_strategy(file_path, settings)
                self.assertIsInstance(strategy, LanguageStrategy)
                self.assertEqual(strategy.language, expected_language)

    def test_get_strategy_for_unsupported_language(self):
        strategy = get_strategy("test.txt", settings)
        self.assertIsNone(strategy)

if __name__ == '__main__':
    unittest.main()
