import unittest
from unittest.mock import patch
import os
import subprocess
import tempfile
import shutil
from tools.git_file_processor import GitFileProcessor
from utils.exceptions import GitProcessorError


class TestGitFileProcessor(unittest.TestCase):
    @patch("subprocess.check_output")
    @patch("os.stat")
    def test_execute_success(self, mock_stat, mock_check_output):
        # Arrange
        mock_stat.return_value = os.stat_result((0, 0, 0, 0, 0, 0, 123, 0, 0, 0))
        mock_check_output.side_effect = [
            b"true",  # git rev-parse --is-inside-work-tree
            b"git@github.com:test/repo.git",  # git config --get remote.origin.url
            b"main",  # git rev-parse --abbrev-ref HEAD
            b"/path/to/repo",  # git rev-parse --show-toplevel
            b"/path/to/repo",  # git rev-parse --show-toplevel
            b"12345\x00author\x00email\x00Fri Jun 27 12:00:00 2025 +0000\x00message\x1e",  # git log
        ]
        processor = GitFileProcessor()

        # Act
        try:
            result = processor.execute("/path/to/repo/test.py")
        except Exception as e:
            self.fail(f"GitFileProcessor.execute raised an exception unexpectedly: {e}")

        # Assert
        self.assertEqual(result["github_owner"], "test")
        self.assertEqual(result["github_repo"], "repo")
        self.assertEqual(result["branch_name"], "main")
        self.assertEqual(
            result["github_link"], "https://github.com/test/repo/blob/main/test.py"
        )
        self.assertEqual(len(result["commit_history"]), 1)
        self.assertEqual(result["commit_history"][0]["hash"], "12345")

    @patch("subprocess.check_output")
    def test_execute_not_a_git_repo(self, mock_check_output):
        # Arrange
        mock_check_output.side_effect = subprocess.CalledProcessError(1, "git")
        processor = GitFileProcessor()

        # Act & Assert
        with self.assertRaises(GitProcessorError):
            processor.execute("/path/to/some/file.py")

    @patch("subprocess.check_output")
    @patch("os.stat")
    def test_execute_no_remote(self, mock_stat, mock_check_output):
        # Arrange
        mock_stat.return_value = os.stat_result((0, 0, 0, 0, 0, 0, 123, 0, 0, 0))
        # The second call to check_output is for the remote url
        mock_check_output.side_effect = [
            b"true",
            subprocess.CalledProcessError(1, "git"),  # This will be for the remote
            b"main",
            b"/path/to/repo",
            b"/path/to/repo",
            b"12345\x00author\x00email\x00Fri Jun 27 12:00:00 2025 +0000\x00message\x1e",
        ]
        processor = GitFileProcessor()

        # Act
        result = processor.execute("/path/to/repo/test.py")

        # Assert
        self.assertIsNone(result["github_owner"])
        self.assertIsNone(result["github_repo"])
        self.assertIsNone(result["github_link"])

    @patch("subprocess.check_output")
    @patch("os.stat")
    def test_execute_no_commit_history(self, mock_stat, mock_check_output):
        # Arrange
        mock_stat.return_value = os.stat_result((0, 0, 0, 0, 0, 0, 123, 0, 0, 0))
        mock_check_output.side_effect = [
            b"true",
            b"git@github.com:test/repo.git",
            b"main",
            b"/path/to/repo",
            b"/path/to/repo",
            b"",  # Empty git log
        ]
        processor = GitFileProcessor()

        # Act
        result = processor.execute("/path/to/repo/test.py")

        # Assert
        self.assertEqual(result["commit_history"], [])
        self.assertIsNone(result["last_updated"])


class TestGitFileProcessorIntegration(unittest.TestCase):
    def setUp(self):
        self.repo_dir = tempfile.mkdtemp()
        subprocess.check_call(["git", "init", self.repo_dir])
        subprocess.check_call(
            ["git", "-C", self.repo_dir, "config", "user.name", "Test User"]
        )
        subprocess.check_call(
            ["git", "-C", self.repo_dir, "config", "user.email", "test@example.com"]
        )
        subprocess.check_call(
            [
                "git",
                "-C",
                self.repo_dir,
                "remote",
                "add",
                "origin",
                "https://github.com/test_owner/test_repo.git",
            ]
        )

        self.file_path = os.path.join(self.repo_dir, "test_file.py")
        with open(self.file_path, "w") as f:
            f.write('print("hello world")')
        subprocess.check_call(["git", "-C", self.repo_dir, "add", "test_file.py"])
        subprocess.check_call(
            ["git", "-C", self.repo_dir, "commit", "-m", "Initial commit"]
        )

    def tearDown(self):
        shutil.rmtree(self.repo_dir)

    def test_execute_in_real_repo(self):
        processor = GitFileProcessor()
        result = processor.execute(self.file_path)

        self.assertEqual(result["github_owner"], "test_owner")
        self.assertEqual(result["github_repo"], "test_repo")
        self.assertTrue(result["branch_name"])
        self.assertTrue(
            result["github_link"].endswith(
                f"test_owner/test_repo/blob/{result['branch_name']}/test_file.py"
            )
        )
        self.assertEqual(len(result["commit_history"]), 1)
        self.assertEqual(
            result["commit_history"][0]["message"].strip(), "Initial commit"
        )
        self.assertEqual(result["commit_history"][0]["author_name"], "Test User")
        self.assertEqual(
            result["commit_history"][0]["author_email"], "test@example.com"
        )
