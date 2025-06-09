import unittest
import os
import json
from unittest.mock import patch
from google.api_core import exceptions

# Assuming your script is named 'secret_manager_service_client_secrets_list.py'
import secret_manager_service_client_secrets_list


class TestListSecretsSample(unittest.TestCase):

    @patch('secret_manager_service_client_secrets_list.secretmanager_v1.SecretManagerServiceClient')
    def test_list_secrets_success(self, mock_client):
        # Mock the client and its methods to simulate a successful API call.
        mock_secret = type('obj', (object,), {'name': 'projects/test-project/secrets/test-secret'})
        mock_list_secrets = mock_client.return_value.list_secrets
        mock_list_secrets.return_value = [mock_secret()]

        # Call the function with a test project ID.
        project_id = 'test-project'
        secrets = secret_manager_service_client_secrets_list.list_secrets_sample(project_id)

        # Assert that the function returns the expected list of secrets.
        self.assertEqual(secrets, ['projects/test-project/secrets/test-secret'])
        mock_list_secrets.assert_called_once_with(parent=f'projects/{project_id}')

    @patch('secret_manager_service_client_secrets_list.secretmanager_v1.SecretManagerServiceClient')
    def test_list_secrets_api_error(self, mock_client):
        # Mock the client to raise an exception during the API call.
        mock_list_secrets = mock_client.return_value.list_secrets
        mock_list_secrets.side_effect = exceptions.PermissionDenied('API error')

        # Call the function and assert that it raises a RuntimeError.
        project_id = 'test-project'
        with self.assertRaises(RuntimeError) as context:
            secret_manager_service_client_secrets_list.list_secrets_sample(project_id)

        self.assertTrue('Error listing secrets' in str(context.exception))

    def test_main_no_project_id(self):
        # Test the main function when the GCP_PROJECT_ID environment variable is not set.
        with patch.dict(os.environ, {'GCP_PROJECT_ID': ''}, clear=True):
            with patch('secret_manager_service_client_secrets_list.print') as mock_print:
                with self.assertRaises(SystemExit) as context:
                    secret_manager_service_client_secrets_list.main()

                self.assertEqual(context.exception.code, 1)
                mock_print.assert_called_once()
                printed_output = mock_print.call_args[0][0]
                self.assertIn('Google Cloud project ID not provided', printed_output)

    @patch('secret_manager_service_client_secrets_list.list_secrets_sample')
    def test_main_success(self, mock_list_secrets_sample):
        # Test the main function with a valid project ID and successful API call.
        mock_list_secrets_sample.return_value = ['secret1', 'secret2']
        with patch.dict(os.environ, {'GCP_PROJECT_ID': 'test-project'}):
            with patch('secret_manager_service_client_secrets_list.print') as mock_print:
                secret_manager_service_client_secrets_list.main()

                mock_print.assert_called_once()
                printed_output = mock_print.call_args[0][0]
                self.assertIn('secret_names', printed_output)
                self.assertIn('secret1', printed_output)
                self.assertIn('secret2', printed_output)

    @patch('secret_manager_service_client_secrets_list.list_secrets_sample')
    def test_main_api_error(self, mock_list_secrets_sample):
        # Test the main function when the API call raises an exception.
        mock_list_secrets_sample.side_effect = RuntimeError('API error')
        with patch.dict(os.environ, {'GCP_PROJECT_ID': 'test-project'}):
            with patch('secret_manager_service_client_secrets_list.print') as mock_print:
                with self.assertRaises(SystemExit) as context:
                    secret_manager_service_client_secrets_list.main()

                self.assertEqual(context.exception.code, 1)
                mock_print.assert_called_once()
                printed_output = mock_print.call_args[0][0]
                self.assertIn('error', printed_output)
                self.assertIn('API error', printed_output)


if __name__ == '__main__':
    unittest.main()
