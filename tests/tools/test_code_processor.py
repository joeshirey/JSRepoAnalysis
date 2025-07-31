import unittest
from unittest.mock import patch
from config import settings
from tools.code_processor import CodeProcessor
from utils.exceptions import (
    GitRepositoryError,
    APIError,
)


class TestCodeProcessor(unittest.TestCase):
    def setUp(self):
        self.processor = CodeProcessor(settings)

    @patch.object(CodeProcessor, "_get_git_info")
    def test_process_file_not_in_git_repo(self, mock_get_git_info):
        mock_get_git_info.side_effect = GitRepositoryError
        with self.assertRaises(GitRepositoryError):
            self.processor.process_file("test.py")

    @patch.object(CodeProcessor, "_get_git_info")
    @patch.object(CodeProcessor, "_is_already_processed", return_value=True)
    @patch.object(CodeProcessor, "_analyze_file")
    def test_process_file_already_processed(
        self,
        mock_analyze_file,
        mock_is_already_processed,
        mock_get_git_info,
    ):
        mock_get_git_info.return_value = {"github_link": "some_link"}

        self.processor.process_file("test.py")

        mock_analyze_file.assert_not_called()

    @patch.object(CodeProcessor, "_get_git_info")
    @patch.object(CodeProcessor, "bigquery_repo")
    @patch.object(
        CodeProcessor,
        "_analyze_file",
        return_value={"analysis": {"assessment": {}}},
    )
    @patch.object(CodeProcessor, "_build_bigquery_row", return_value={})
    @patch.object(CodeProcessor, "_save_result")
    def test_process_file_with_regen(
        self,
        mock_save_result,
        mock_build_bigquery_row,
        mock_analyze_file,
        mock_bigquery_repo,
        mock_get_git_info,
    ):
        mock_get_git_info.return_value = {
            "github_link": "some_link",
            "last_updated": "2025-01-01",
        }

        self.processor.process_file("test.py", regen=True)

        mock_bigquery_repo.delete.assert_called_once_with("some_link", "2025-01-01")

    @patch.object(CodeProcessor, "_get_git_info", side_effect=GitRepositoryError)
    def test_process_file_git_error(self, mock_get_git_info):
        with self.assertRaises(GitRepositoryError):
            self.processor.process_file("test.py")

    @patch.object(CodeProcessor, "_get_git_info")
    @patch.object(CodeProcessor, "_is_already_processed", return_value=False)
    @patch.object(CodeProcessor, "_call_analysis_api", side_effect=APIError)
    def test_process_file_api_error(
        self,
        mock_call_analysis_api,
        mock_is_already_processed,
        mock_get_git_info,
    ):
        mock_get_git_info.return_value = {"github_link": "some_link"}
        with self.assertRaises(APIError):
            self.processor.process_file("test.py")

    @patch.object(CodeProcessor, "_get_git_info")
    @patch.object(CodeProcessor, "_is_already_processed", return_value=False)
    @patch.object(CodeProcessor, "_analyze_file")
    @patch.object(CodeProcessor, "_save_result")
    def test_process_file_success(
        self,
        mock_save_result,
        mock_analyze_file,
        mock_is_already_processed,
        mock_get_git_info,
    ):
        mock_get_git_info.return_value = {"github_link": "some_link"}
        mock_analyze_file.return_value = {
            "git_info": {"github_link": "some_link"},
            "analysis": {
                "region_tags": ["tag1", "tag2"],
                "assessment": {"style": "good"},
            },
        }

        self.processor.process_file("test.py")

        mock_save_result.assert_called_once()

    @patch.object(CodeProcessor, "bigquery_repo")
    def test_is_already_processed_true(self, mock_bigquery_repo):
        mock_bigquery_repo.record_exists.return_value = True
        git_info = {"github_link": "some_link", "last_updated": "2025-01-01"}
        self.assertTrue(self.processor._is_already_processed(git_info))

    @patch.object(CodeProcessor, "bigquery_repo")
    def test_is_already_processed_false(self, mock_bigquery_repo):
        mock_bigquery_repo.record_exists.return_value = False
        git_info = {"github_link": "some_link", "last_updated": "2025-01-01"}
        self.assertFalse(self.processor._is_already_processed(git_info))

    @patch.object(CodeProcessor, "_get_git_info")
    @patch.object(CodeProcessor, "_call_analysis_api")
    def test_analyze_file_only(self, mock_call_analysis_api, mock_get_git_info):
        mock_get_git_info.return_value = {"github_link": "some_link"}
        mock_call_analysis_api.return_value = {"analysis": "good"}
        result = self.processor.analyze_file_only("test.py")
        self.assertEqual(result, {"analysis": "good"})


if __name__ == "__main__":
    unittest.main()
