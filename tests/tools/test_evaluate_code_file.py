import unittest
from unittest.mock import patch, MagicMock, mock_open
from tools.evaluate_code_file import CodeEvaluator
from utils.exceptions import CodeEvaluatorError
from config import settings


class TestCodeEvaluator(unittest.TestCase):
    def setUp(self):
        self.settings = settings
        self.settings.VERTEXAI_MODEL_NAME = "test-model"

    @patch("google.genai.Client")
    @patch("builtins.open", new_callable=mock_open, read_data="system instructions")
    def test_init_success(self, mock_file, mock_genai_client):
        # Act
        evaluator = CodeEvaluator(self.settings)

        # Assert
        mock_genai_client.assert_called_once()
        mock_file.assert_called_with("./prompts/system_instructions.txt", "r")
        self.assertEqual(evaluator.system_instructions, ["system instructions"])

    @patch("google.genai.Client")
    def test_init_failure(self, mock_genai_client):
        # Arrange
        mock_genai_client.side_effect = Exception("Test Exception")

        # Act & Assert
        with self.assertRaises(CodeEvaluatorError):
            CodeEvaluator(self.settings)

    @patch("google.genai.Client")
    @patch("builtins.open", new_callable=mock_open, read_data='{"evaluation": "great"}')
    def test_execute_success(self, mock_file, mock_genai_client):
        # Arrange
        mock_client_instance = mock_genai_client.return_value
        mock_response = MagicMock()
        mock_response.text = '{"evaluation": "great"}'
        mock_client_instance.models.generate_content.return_value = mock_response

        evaluator = CodeEvaluator(self.settings)

        # Create a dummy file to read
        with patch("builtins.open", mock_open(read_data="print('hello')")):
            # Act
            result = evaluator.execute(
                "dummy_path.py", "Python", "test_tag", "http://github.com/test"
            )

            # Assert
            self.assertEqual(result, '{"evaluation": "great"}')
            self.assertEqual(mock_client_instance.models.generate_content.call_count, 2)

    @patch("google.genai.Client")
    def test_execute_file_not_found(self, mock_genai_client):
        # Arrange
        with patch("builtins.open", mock_open(read_data="system instructions")):
            evaluator = CodeEvaluator(self.settings)

        # Act & Assert
        with self.assertRaises(CodeEvaluatorError):
            evaluator.execute(
                "non_existent_path.py", "Python", "test_tag", "http://github.com/test"
            )


if __name__ == "__main__":
    unittest.main()
