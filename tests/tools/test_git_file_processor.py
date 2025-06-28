import unittest
from unittest.mock import patch
import os
from tools.git_file_processor import GitFileProcessor

class TestGitFileProcessor(unittest.TestCase):

    @patch('subprocess.check_output')
    @patch('os.stat')
    def test_execute_success(self, mock_stat, mock_check_output):
        # Arrange
        mock_stat.return_value = os.stat_result((0, 0, 0, 0, 0, 0, 123, 0, 0, 0))
        mock_check_output.side_effect = [
            b'true',  # git rev-parse --is-inside-work-tree
            b'git@github.com:test/repo.git',  # git config --get remote.origin.url
            b'main',  # git rev-parse --abbrev-ref HEAD
            b'/path/to/repo',  # git rev-parse --show-toplevel
            b'/path/to/repo',  # git rev-parse --show-toplevel
            b'12345\nauthor\nemail\nFri Jun 27 12:00:00 2025 +0000\nmessage'  # git log
        ]
        processor = GitFileProcessor()

        # Act
        try:
            result = processor.execute('/path/to/repo/test.py')
        except Exception as e:
            self.fail(f"GitFileProcessor.execute raised an exception unexpectedly: {e}")

        # Assert
        self.assertEqual(result['github_owner'], 'test')
        self.assertEqual(result['github_repo'], 'repo')
        self.assertEqual(result['branch_name'], 'main')
        self.assertEqual(result['github_link'], 'https://github.com/test/repo/blob/main/test.py')
        self.assertEqual(len(result['commit_history']), 1)
        self.assertEqual(result['commit_history'][0]['hash'], '12345')

if __name__ == '__main__':
    unittest.main()

