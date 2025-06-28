import unittest
from unittest.mock import patch, MagicMock
from tools.code_processor import CodeProcessor
from utils.data_classes import AnalysisResult
from config import settings

class TestCodeProcessorHappyPath(unittest.TestCase):

    def setUp(self):
        self.settings = settings
        self.processor = CodeProcessor(self.settings)

    @patch('tools.code_processor.get_strategy')
    @patch.object(CodeProcessor, '_get_git_info')
    @patch.object(CodeProcessor, '_is_already_processed', return_value=False)
    @patch.object(CodeProcessor, '_analyze_file')
    @patch.object(CodeProcessor, '_save_result')
    def test_process_file_success(self, mock_save_result, mock_analyze_file, mock_is_already_processed, mock_get_git_info, mock_get_strategy):
        # Arrange
        mock_strategy = MagicMock()
        mock_get_strategy.return_value = mock_strategy

        mock_git_info = {"github_link": "https://github.com/test/repo/blob/main/test.py"}
        mock_get_git_info.return_value = mock_git_info

        mock_analysis_result = AnalysisResult(
            git_info=mock_git_info,
            region_tags=["test_tag"],
            evaluation_data={"evaluation": "great"},
            raw_code="print('hello')"
        )
        mock_analyze_file.return_value = mock_analysis_result

        # Act
        self.processor.process_file("test.py")

        # Assert
        mock_get_strategy.assert_called_once_with("test.py", self.settings)
        mock_get_git_info.assert_called_once_with("test.py")
        mock_is_already_processed.assert_called_once()
        mock_analyze_file.assert_called_once_with("test.py", mock_strategy, mock_git_info)
        mock_save_result.assert_called_once_with(
            mock_strategy.language,
            "https___github_com_test_repo_blob_main_test_py",
            mock_analysis_result
        )

if __name__ == '__main__':
    unittest.main()
