import unittest
from unittest.mock import Mock, patch
from config import settings
from tools.code_processor import CodeProcessor
from utils.exceptions import UnsupportedFileTypeError, GitRepositoryError, NoRegionTagsError
from utils.data_classes import AnalysisResult

class TestCodeProcessor(unittest.TestCase):

    def setUp(self):
        self.processor = CodeProcessor(settings)

    @patch('tools.code_processor.get_strategy')
    def test_process_file_unsupported_type(self, mock_get_strategy):
        mock_get_strategy.return_value = None
        with self.assertRaises(UnsupportedFileTypeError):
            self.processor.process_file("test.txt")

    @patch('tools.code_processor.get_strategy')
    @patch.object(CodeProcessor, '_get_git_info')
    def test_process_file_not_in_git_repo(self, mock_get_git_info, mock_get_strategy):
        mock_get_strategy.return_value = Mock()
        mock_get_git_info.side_effect = GitRepositoryError
        with self.assertRaises(GitRepositoryError):
            self.processor.process_file("test.py")

    @patch('tools.code_processor.get_strategy')
    @patch.object(CodeProcessor, '_get_git_info')
    @patch.object(CodeProcessor, '_is_already_processed', return_value=True)
    @patch.object(CodeProcessor, '_analyze_file')
    def test_process_file_already_processed(self, mock_analyze_file, mock_is_already_processed, mock_get_git_info, mock_get_strategy):
        mock_get_strategy.return_value = Mock()
        mock_get_git_info.return_value = {"github_link": "some_link"}

        self.processor.process_file("test.py")

        mock_analyze_file.assert_not_called()

    @patch('tools.code_processor.get_strategy')
    @patch.object(CodeProcessor, '_get_git_info')
    @patch.object(CodeProcessor, 'bigquery_repo')
    @patch.object(CodeProcessor, '_analyze_file', return_value=AnalysisResult(git_info={}, region_tags=[], evaluation_data={}, raw_code=''))
    @patch.object(CodeProcessor, '_build_bigquery_row', return_value={})
    @patch.object(CodeProcessor, '_save_result')
    def test_process_file_with_regen(self, mock_save_result, mock_build_bigquery_row, mock_analyze_file, mock_bigquery_repo, mock_get_git_info, mock_get_strategy):
        mock_get_strategy.return_value = Mock()
        mock_get_git_info.return_value = {"github_link": "some_link", "last_updated": "2025-01-01"}
        
        self.processor.process_file("test.py", regen=True)

        mock_bigquery_repo.delete.assert_called_once_with("some_link", "2025-01-01")

    @patch('tools.code_processor.get_strategy')
    @patch.object(CodeProcessor, '_get_git_info')
    @patch.object(CodeProcessor, '_is_already_processed')
    @patch.object(CodeProcessor, '_analyze_file')
    @patch.object(CodeProcessor, '_save_result')
    def test_process_file_success(self, mock_save_result, mock_analyze_file, mock_is_already_processed, mock_get_git_info, mock_get_strategy):
        mock_get_strategy.return_value = Mock()
        mock_get_git_info.return_value = {"github_link": "some_link"}
        mock_is_already_processed.return_value = False
        mock_analyze_file.return_value = AnalysisResult(
            git_info={"github_link": "some_link"},
            region_tags=["tag1", "tag2"],
            evaluation_data={"style": "good"},
            raw_code="some code"
        )

        self.processor.process_file("test.py")

        mock_save_result.assert_called_once()

if __name__ == '__main__':
    unittest.main()
