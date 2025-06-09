import os
import unittest
from unittest.mock import MagicMock, patch
import json
from typing import List, Dict, Any

# Assuming the code under test is in 'secret_manager_service_client_secret_versions_list.py'
import secret_manager_service_client_secret_versions_list as target

class TestListSecretVersions(unittest.TestCase):

    @patch('secret_manager_service_client_secret_versions_list.secretmanager_v1beta2.SecretManagerServiceClient')
    def test_list_secret_versions_success(self, MockClient):
        # Mock the SecretManagerServiceClient and its methods
        mock_client = MagicMock()
        MockClient.return_value = mock_client

        # Mock the list_secret_versions method to return a list of mock versions
        mock_version1 = MagicMock(name='version1', state=MagicMock(name='ENABLED'), create_time=MagicMock(isoformat=lambda: '2023-01-01T00:00:00'), destroy_time=MagicMock(isoformat=lambda: '2023-01-02T00:00:00'))
        mock_version2 = MagicMock(name='version2', state=MagicMock(name='DISABLED'), create_time=MagicMock(isoformat=lambda: '2023-01-03T00:00:00'), destroy_time=None)
        mock_client.list_secret_versions.return_value = [mock_version1, mock_version2]

        # Call the function with mock data
        project_id = 'test-project'
        secret_id = 'test-secret'
        result = target.list_secret_versions_sample(project_id, secret_id)

        # Assert that the client was called with the correct parent
        mock_client.list_secret_versions.assert_called_once_with(parent=f'projects/{project_id}/secrets/{secret_id}')

        # Assert that the result is a list of dictionaries with the expected data
        expected_result = [
            {
                'name': 'version1',
                'state': 'ENABLED',
                'create_time': '2023-01-01T00:00:00',
                'destroy_time': '2023-01-02T00:00:00'
            },
            {
                'name': 'version2',
                'state': 'DISABLED',
                'create_time': '2023-01-03T00:00:00',
                'destroy_time': None
            }
        ]
        self.assertEqual(result, expected_result)

    @patch('secret_manager_service_client_secret_versions_list.secretmanager_v1beta2.SecretManagerServiceClient')
    def test_list_secret_versions_exception(self, MockClient):
        # Mock the SecretManagerServiceClient to raise an exception
        mock_client = MagicMock()
        MockClient.return_value = mock_client
        mock_client.list_secret_versions.side_effect = Exception('Test Exception')

        # Call the function with mock data and assert that it raises the exception
        project_id = 'test-project'
        secret_id = 'test-secret'
        with self.assertRaises(Exception) as context:
            target.list_secret_versions_sample(project_id, secret_id)

        self.assertEqual(str(context.exception), 'Test Exception')

    @patch('secret_manager_service_client_secret_versions_list.os.environ.get')
    @patch('secret_manager_service_client_secret_versions_list.list_secret_versions_sample')
    @patch('secret_manager_service_client_secret_versions_list.argparse.ArgumentParser.parse_args')
    @patch('secret_manager_service_client_secret_versions_list.json.dumps')
    def test_main_success(self, mock_json_dumps, mock_parse_args, mock_list_secret_versions_sample, mock_os_environ_get):
        # Mock the environment variable, arguments, and the list_secret_versions_sample function
        mock_os_environ_get.return_value = 'test-project'
        mock_parse_args.return_value.secret_id = 'test-secret'
        mock_list_secret_versions_sample.return_value = [{'name': 'version1'}]
        mock_json_dumps.return_value = 'json_output'

        # Patch stdout to capture the output
        with patch('secret_manager_service_client_secret_versions_list.os.sys.stdout') as mock_stdout:
            # Call the main function
            target.main()

            # Assert that the list_secret_versions_sample function was called with the correct arguments
            mock_list_secret_versions_sample.assert_called_once_with('test-project', 'test-secret')

            # Assert that json.dumps was called with the result
            mock_json_dumps.assert_called_once_with([{'name': 'version1'}], indent=2)

            # Assert that the output was printed to stdout
            mock_stdout.write.assert_called_once_with('json_output\n')

    @patch('secret_manager_service_client_secret_versions_list.os.environ.get')
    def test_main_no_project_id(self, mock_os_environ_get):
        # Mock the environment variable to return None (project ID not set)
        mock_os_environ_get.return_value = None

        # Patch os._exit to prevent the test from exiting
        with patch('secret_manager_service_client_secret_versions_list.os._exit') as mock_exit,
             patch('secret_manager_service_client_secret_versions_list.os.sys.stderr') as mock_stderr:
            # Call the main function
            target.main()

            # Assert that os._exit was called with 1
            mock_exit.assert_called_once_with(1)
            mock_stderr.write.assert_called_once_with('Error: GCP_PROJECT_ID environment variable not set.\n')

    @patch('secret_manager_service_client_secret_versions_list.os.environ.get')
    @patch('secret_manager_service_client_secret_versions_list.list_secret_versions_sample')
    @patch('secret_manager_service_client_secret_versions_list.argparse.ArgumentParser.parse_args')
    def test_main_exception(self, mock_parse_args, mock_list_secret_versions_sample, mock_os_environ_get):
        # Mock the environment variable, arguments, and the list_secret_versions_sample function to raise an exception
        mock_os_environ_get.return_value = 'test-project'
        mock_parse_args.return_value.secret_id = 'test-secret'
        mock_list_secret_versions_sample.side_effect = Exception('Test Exception')

        # Patch os._exit to prevent the test from exiting
        with patch('secret_manager_service_client_secret_versions_list.os._exit') as mock_exit:
            # Call the main function
            target.main()

            # Assert that os._exit was called with 1
            mock_exit.assert_called_once_with(1)

if __name__ == '__main__':
    unittest.main()
