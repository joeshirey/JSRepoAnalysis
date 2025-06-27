import unittest
from unittest.mock import Mock
from strategies.strategy_factory import get_strategy
from strategies.language_strategy import LanguageStrategy

class TestStrategyFactory(unittest.TestCase):

    def test_get_strategy_for_supported_languages(self):
        config = Mock()
        config.project_id = "test-project"
        config.vertexai_location = "us-central1"
        config.vertexai_model_name = "gemini-1.5-flash-001"
        test_cases = {
            "test.js": "JavaScript",
            "test.ts": "TypeScript",
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
                strategy = get_strategy(file_path, config)
                self.assertIsInstance(strategy, LanguageStrategy)
                self.assertEqual(strategy.language, expected_language)

    def test_get_strategy_for_unsupported_language(self):
        config = Mock()
        config.project_id = "test-project"
        config.vertexai_location = "us-central1"
        config.vertexai_model_name = "gemini-1.5-flash-001"
        strategy = get_strategy("test.txt", config)
        self.assertIsNone(strategy)

if __name__ == '__main__':
    unittest.main()
