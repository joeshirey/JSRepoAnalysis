import os
import unittest
import json
from unittest.mock import patch, MagicMock
from google.api_core import exceptions

# Assuming the code under test is in a file named 'secret_manager_service_client_secrets_list.py'
import secret_manager_service_client_secrets_list


class TestListSecrets(unittest.TestCase):

    @patch('secret_manager_service_client_secrets_list.secretmanager_v1beta1.SecretManagerServiceClient')
    def test_list_secrets_success(self, mock_client):
        # Mock the client and its methods to simulate a successful API call.
        mock_secret = MagicMock()
        mock_secret.name = 'projects/test-project/secrets/test-secret'
        mock_secret.create_time = MagicMock()
        mock_secret.create_time.isoformat.return_value = '2023-10-26T00:00:00Z'
        mock_secret.labels = {'label1': 'value1', 'label2': 'value2'}

        mock_list_secrets = MagicMock()
        mock_list_secrets.return_value = [mock_secret]
        mock_client.return_value.list_secrets = mock_list_secrets

        # Call the function with a test project ID.
        project_id = 'test-project'
        secrets = secret_manager_service_client_secrets_list.list_secrets_sample(project_id)

        # Assert that the function returns the expected list of secrets.
        self.assertEqual(len(secrets), 1)
        self.assertEqual(secrets[0]['name'], 'projects/test-project/secrets/test-secret')
        self.assertEqual(secrets[0]['create_time'], '2023-10-26T00:00:00Z')
        self.assertEqual(secrets[0]['labels'], {'label1': 'value1', 'label2': 'value2'})

    @patch('secret_manager_service_client_secrets_list.secretmanager_v1beta1.SecretManagerServiceClient')
    def test_list_secrets_no_secrets(self, mock_client):
        # Mock the client to return an empty list of secrets.
        mock_list_secrets = MagicMock()
        mock_list_secrets.return_value = []
        mock_client.return_value.list_secrets = mock_list_secrets

        # Call the function with a test project ID.
        project_id = 'test-project'
        secrets = secret_manager_service_client_secrets_list.list_secrets_sample(project_id)

        # Assert that the function returns an empty list.
        self.assertEqual(len(secrets), 0)

    @patch('secret_manager_service_client_secrets_list.secretmanager_v1beta1.SecretManagerServiceClient')
    def test_list_secrets_api_error(self, mock_client):
        # Mock the client to raise a GoogleAPIError.
        mock_client.return_value.list_secrets.side_effect = exceptions.GoogleAPIError('API error')

        # Call the function with a test project ID.
        project_id = 'test-project'
        secrets = secret_manager_service_client_secrets_list.list_secrets_sample(project_id)

        # Assert that the function returns an empty list.
        self.assertEqual(len(secrets), 0)

    @patch('secret_manager_service_client_secrets_list.argparse.ArgumentParser.parse_args', return_value=MagicMock(project_id='test-project'))
    @patch('secret_manager_service_client_secrets_list.list_secrets_sample')
    @patch('sys.stdout')
    def test_main_success(self, mock_stdout, mock_list_secrets_sample, mock_parse_args):
        # Mock the list_secrets_sample function to return a list of secrets.
        mock_list_secrets_sample.return_value = [
            {
                'name': 'projects/test-project/secrets/test-secret',
                'create_time': '2023-10-26T00:00:00Z',
                'labels': {'label1': 'value1'}
            }
        ]

        # Call the main function.
        secret_manager_service_client_secrets_list.main()

        # Assert that the list_secrets_sample function was called with the correct project ID.
        mock_list_secrets_sample.assert_called_once_with('test-project')

        # Assert that the output is a JSON string containing the secret name.
        captured = mock_stdout.write.call_args_list[0][0][0]
        self.assertTrue('projects/test-project/secrets/test-secret' in captured)

    @patch('secret_manager_service_client_secrets_list.argparse.ArgumentParser.parse_args', return_value=MagicMock(project_id=None))
    @patch('sys.exit')
    @patch('sys.stdout')
    def test_main_no_project_id(self, mock_stdout, mock_exit, mock_parse_args):
        # Call the main function.
        secret_manager_service_client_secrets_list.main()

        # Assert that the program exits with an error code.
        mock_exit.assert_called_once_with(1)

        # Assert that an error message is printed to stdout.
        captured = mock_stdout.write.call_args_list[0][0][0]
        self.assertTrue('Error: --project-id argument or GCP_PROJECT_ID environment' in captured)


if __name__ == '__main__':
    unittest.main()
