import unittest
import os
import json
from unittest.mock import patch, mock_open
from google.api_core import exceptions
from google.cloud import secretmanager_v1

# Assuming the code under test is in 'secret_manager_service_client_secrets_list.py'
import secret_manager_service_client_secrets_list

class TestListSecrets(unittest.TestCase):

    @patch('secret_manager_service_client_secrets_list.secretmanager_v1.SecretManagerServiceClient')
    def test_list_secrets_success(self, mock_client):
        # Mock the client and its methods to simulate a successful API call.
        mock_secret = secretmanager_v1.Secret()
        mock_secret.name = 'projects/test-project/secrets/test-secret'
        mock_secret.create_time = None  # Simulate no creation time
        mock_secret.labels = {}

        mock_list_secrets = mock_client.return_value.list_secrets
        mock_list_secrets.return_value = [mock_secret]

        # Call the function with a test project ID
        project_id = 'test-project'
        secrets = secret_manager_service_client_secrets_list.list_secrets_sample(project_id)

        # Assert that the client's list_secrets method was called with the correct parent.
        mock_list_secrets.assert_called_once_with(parent=f'projects/{project_id}')

        # Assert that the function returns the expected data.
        self.assertEqual(len(secrets), 1)
        self.assertEqual(secrets[0]['name'], 'projects/test-project/secrets/test-secret')
        self.assertEqual(secrets[0]['project_id'], 'test-project')
        self.assertEqual(secrets[0]['secret_id'], 'test-secret')
        self.assertEqual(secrets[0]['create_time'], None)
        self.assertEqual(secrets[0]['labels'], {})

    @patch('secret_manager_service_client_secrets_list.secretmanager_v1.SecretManagerServiceClient')
    def test_list_secrets_api_error(self, mock_client):
        # Mock the client to raise an exception.
        mock_list_secrets = mock_client.return_value.list_secrets
        mock_list_secrets.side_effect = exceptions.GoogleAPIError('API error')

        # Call the function and assert that it raises the same exception.
        project_id = 'test-project'
        with self.assertRaises(exceptions.GoogleAPIError):
            secret_manager_service_client_secrets_list.list_secrets_sample(project_id)

    @patch('secret_manager_service_client_secrets_list.os.getenv', return_value='test-project')
    @patch('secret_manager_service_client_secrets_list.list_secrets_sample')
    @patch('secret_manager_service_client_secrets_list.json.dumps')
    @patch('sys.stdout.write')
    def test_main_success(self, mock_stdout, mock_json_dumps, mock_list_secrets_sample, mock_getenv):
        # Mock the environment variable and the list_secrets_sample function.
        mock_list_secrets_sample.return_value = [{'name': 'test-secret'}]
        mock_json_dumps.return_value = '["test-secret"]'

        # Call the main function.
        secret_manager_service_client_secrets_list.main()

        # Assert that the list_secrets_sample function was called with the correct project ID.
        mock_list_secrets_sample.assert_called_once_with('test-project')

        # Assert that json.dumps was called with the result from list_secrets_sample
        mock_json_dumps.assert_called_once_with([{'name': 'test-secret'}], indent=2)

        # Assert that the result was printed to stdout.
        mock_stdout.assert_called()

    @patch('secret_manager_service_client_secrets_list.os.getenv', return_value=None)
    @patch('sys.stderr')
    @patch('sys.exit')
    def test_main_no_project_id(self, mock_exit, mock_stderr, mock_getenv):
        # Mock the environment variable to return None.

        # Call the main function.
        secret_manager_service_client_secrets_list.main()

        # Assert that an error message was printed to stderr.
        mock_stderr.write.assert_called()

        # Assert that the program exited with an error code.
        mock_exit.assert_called_once_with(1)

    @patch('secret_manager_service_client_secrets_list.os.getenv', return_value='test-project')
    @patch('secret_manager_service_client_secrets_list.list_secrets_sample')
    @patch('sys.stderr')
    @patch('sys.exit')
    def test_main_exception(self, mock_exit, mock_stderr, mock_list_secrets_sample, mock_getenv):
        # Mock the list_secrets_sample function to raise an exception.
        mock_list_secrets_sample.side_effect = Exception('Unexpected error')

        # Call the main function.
        secret_manager_service_client_secrets_list.main()

        # Assert that an error message was printed to stderr.
        mock_stderr.write.assert_called()

        # Assert that the program exited with an error code.
        mock_exit.assert_called_once_with(1)

if __name__ == '__main__':
    unittest.main()
