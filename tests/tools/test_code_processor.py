import unittest
from unittest.mock import Mock, patch
from config import settings
from tools.code_processor import CodeProcessor
from utils.exceptions import (
    UnsupportedFileTypeError,
    GitRepositoryError,
    NoRegionTagsError,
)
from utils.data_classes import AnalysisResult
import json


class TestCodeProcessor(unittest.TestCase):
    def setUp(self):
        self.processor = CodeProcessor(settings)

    @patch("tools.code_processor.get_strategy")
    def test_process_file_unsupported_type(self, mock_get_strategy):
        mock_get_strategy.return_value = None
        with self.assertRaises(UnsupportedFileTypeError):
            self.processor.process_file("test.txt")

    @patch("tools.code_processor.get_strategy")
    @patch.object(CodeProcessor, "_get_git_info")
    def test_process_file_not_in_git_repo(self, mock_get_git_info, mock_get_strategy):
        mock_get_strategy.return_value = Mock()
        mock_get_git_info.side_effect = GitRepositoryError
        with self.assertRaises(GitRepositoryError):
            self.processor.process_file("test.py")

    @patch("tools.code_processor.get_strategy")
    @patch.object(CodeProcessor, "_get_git_info")
    @patch.object(CodeProcessor, "_is_already_processed", return_value=True)
    @patch.object(CodeProcessor, "_analyze_file")
    def test_process_file_already_processed(
        self,
        mock_analyze_file,
        mock_is_already_processed,
        mock_get_git_info,
        mock_get_strategy,
    ):
        mock_get_strategy.return_value = Mock()
        mock_get_git_info.return_value = {"github_link": "some_link"}

        self.processor.process_file("test.py")

        mock_analyze_file.assert_not_called()

    @patch("tools.code_processor.get_strategy")
    @patch.object(CodeProcessor, "_get_git_info")
    @patch.object(CodeProcessor, "bigquery_repo")
    @patch.object(
        CodeProcessor,
        "_analyze_file",
        return_value=AnalysisResult(
            git_info={}, region_tags=[], evaluation_data={}, raw_code=""
        ),
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
        mock_get_strategy,
    ):
        mock_get_strategy.return_value = Mock()
        mock_get_git_info.return_value = {
            "github_link": "some_link",
            "last_updated": "2025-01-01",
        }

        self.processor.process_file("test.py", regen=True)

        mock_bigquery_repo.delete.assert_called_once_with("some_link", "2025-01-01")

    @patch("tools.code_processor.get_strategy")
    @patch.object(CodeProcessor, "_get_git_info", side_effect=GitRepositoryError)
    def test_process_file_git_error(self, mock_get_git_info, mock_get_strategy):
        mock_get_strategy.return_value = Mock()
        with self.assertRaises(GitRepositoryError):
            self.processor.process_file("test.py")

    @patch("tools.code_processor.get_strategy")
    @patch.object(CodeProcessor, "_get_git_info")
    @patch.object(CodeProcessor, "_is_already_processed", return_value=False)
    def test_process_file_no_region_tags(
        self, mock_is_already_processed, mock_get_git_info, mock_get_strategy
    ):
        mock_get_strategy.return_value = Mock()
        mock_get_git_info.return_value = {"github_link": "some_link"}
        with patch.object(self.processor, "tag_extractor") as mock_tag_extractor:
            mock_tag_extractor.execute.return_value = []
            with self.assertRaises(NoRegionTagsError):
                self.processor.process_file("test.py")

    @patch("tools.code_processor.get_strategy")
    @patch.object(CodeProcessor, "_get_git_info")
    @patch.object(CodeProcessor, "_is_already_processed", return_value=False)
    @patch.object(
        CodeProcessor,
        "_evaluate_code",
        side_effect=json.JSONDecodeError("msg", "doc", 0),
    )
    def test_process_file_evaluate_code_json_error(
        self,
        mock_evaluate_code,
        mock_is_already_processed,
        mock_get_git_info,
        mock_get_strategy,
    ):
        mock_get_strategy.return_value = Mock()
        mock_get_git_info.return_value = {"github_link": "some_link"}
        with patch.object(self.processor, "tag_extractor") as mock_tag_extractor:
            mock_tag_extractor.execute.return_value = ["tag1"]
            with self.assertRaises(json.JSONDecodeError):
                self.processor.process_file("test.py")

    @patch("tools.code_processor.get_strategy")
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
        mock_get_strategy,
    ):
        mock_get_strategy.return_value = Mock()
        mock_get_git_info.return_value = {"github_link": "some_link"}
        mock_analyze_file.return_value = AnalysisResult(
            git_info={"github_link": "some_link"},
            region_tags=["tag1", "tag2"],
            evaluation_data={"style": "good"},
            raw_code="some code",
        )

        self.processor.process_file("test.py")

        mock_save_result.assert_called_once()

    @patch.object(CodeProcessor, "bigquery_repo")
    def test_is_already_processed_true(self, mock_bigquery_repo):
        mock_bigquery_repo.read.return_value = {"last_updated": "2025-01-01"}
        git_info = {"github_link": "some_link", "last_updated": "2025-01-01"}
        self.assertTrue(self.processor._is_already_processed(git_info))

    @patch.object(CodeProcessor, "bigquery_repo")
    def test_is_already_processed_false(self, mock_bigquery_repo):
        mock_bigquery_repo.read.return_value = {"last_updated": "2024-01-01"}
        git_info = {"github_link": "some_link", "last_updated": "2025-01-01"}
        self.assertFalse(self.processor._is_already_processed(git_info))

    @patch("demjson3.decode")
    def test_evaluate_code_lenient_parsing(self, mock_demjson_decode):
        mock_demjson_decode.return_value = {"key": "value"}
        strategy = Mock()
        strategy.evaluate_code.return_value = "{'key': 'value'}"
        result = self.processor._evaluate_code(strategy, "file.py", "tag", "link")
        self.assertEqual(result, {"key": "value"})

    @patch("tools.code_processor.get_strategy")
    @patch.object(CodeProcessor, "_get_git_info")
    @patch.object(CodeProcessor, "_analyze_file")
    def test_analyze_file_only(
        self, mock_analyze_file, mock_get_git_info, mock_get_strategy
    ):
        mock_get_strategy.return_value = Mock()
        mock_get_git_info.return_value = {"github_link": "some_link"}
        mock_analyze_file.return_value = AnalysisResult(
            git_info={"github_link": "some_link"},
            region_tags=["tag1", "tag2"],
            evaluation_data={"style": "good"},
            raw_code="some code",
        )
        result = self.processor.analyze_file_only("test.py")
        self.assertIn("evaluation_data", result)


if __name__ == "__main__":
    unittest.main()
