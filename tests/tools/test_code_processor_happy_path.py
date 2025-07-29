import unittest
from unittest.mock import patch, MagicMock
from tools.code_processor import CodeProcessor
from config import settings


class TestCodeProcessorHappyPath(unittest.TestCase):
    def setUp(self):
        self.settings = settings
        self.processor = CodeProcessor(self.settings)

    @patch("tools.code_processor.CodeProcessor._build_bigquery_row")
    @patch("tools.code_processor.CodeProcessor._save_result")
    @patch("tools.code_processor.CodeProcessor._analyze_file")
    @patch(
        "tools.code_processor.CodeProcessor._is_already_processed", return_value=False
    )
    @patch("tools.code_processor.CodeProcessor._get_git_info")
    def test_process_file_success(
        self,
        mock_get_git_info,
        mock_is_already_processed,
        mock_analyze_file,
        mock_save_result,
        mock_build_bigquery_row,
    ):
        # Arrange
        file_path = "test.py"
        mock_git_info = {
            "github_link": "https://github.com/test/repo/blob/main/test.py"
        }
        mock_get_git_info.return_value = mock_git_info

        mock_analysis_result = {
            "git_info": mock_git_info,
            "analysis": {
                "assessment": {"evaluation": "great"},
                "language": "Python",
            },
        }
        mock_analyze_file.return_value = mock_analysis_result

        mock_bq_row = {"github_link": "some_link"}
        mock_build_bigquery_row.return_value = mock_bq_row

        # Act
        self.processor.process_file(file_path)

        # Assert
        mock_get_git_info.assert_called_once_with(file_path)
        mock_is_already_processed.assert_called_once_with(mock_git_info)
        mock_analyze_file.assert_called_once_with(
            file_path, mock_git_info
        )
        mock_build_bigquery_row.assert_called_once_with(
            mock_analysis_result, file_path
        )
        mock_save_result.assert_called_once_with(mock_bq_row)


if __name__ == "__main__":
    unittest.main()
