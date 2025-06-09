import os
import unittest
from unittest.mock import patch
import json

from google.cloud import secretmanager_v1

# Import the module containing the function to test
import secret_manager_service_client_secret_version_get as secret_version


class TestGetSecretVersion(unittest.TestCase):

    @patch('google.cloud.secretmanager_v1.SecretManagerServiceClient')
    def test_get_secret_version_success(self, mock_client):
        # Configure the mock client to return a mock secret version.
        mock_response = secretmanager_v1.SecretVersion()
        mock_client.return_value.get_secret_version.return_value = mock_response

        # Set environment variables
        os.environ['GOOGLE_CLOUD_PROJECT'] = 'test-project'

        # Call the function with test values.
        project_id = 'test-project'
        secret_id = 'test-secret'
        version_id = 'test-version'

        result = secret_version.get_secret_version_sample(project_id, secret_id, version_id)

        # Assert that the client's get_secret_version method was called with the correct arguments.
        mock_client.return_value.get_secret_version.assert_called_once_with(
            name=f'projects/{project_id}/secrets/{secret_id}/versions/{version_id}',
        )

        # Assert that the function returns the mock secret version.
        self.assertEqual(result, mock_response)

    @patch('google.cloud.secretmanager_v1.SecretManagerServiceClient')
    def test_get_secret_version_failure(self, mock_client):
        # Configure the mock client to raise an exception.
        mock_client.return_value.get_secret_version.side_effect = Exception('API error')

        # Set environment variables
        os.environ['GOOGLE_CLOUD_PROJECT'] = 'test-project'

        # Call the function with test values and assert that it raises an exception.
        project_id = 'test-project'
        secret_id = 'test-secret'
        version_id = 'test-version'

        with self.assertRaises(Exception) as context:
            secret_version.get_secret_version_sample(project_id, secret_id, version_id)

        self.assertEqual(str(context.exception), 'API error')

    @patch('google.cloud.secretmanager_v1.SecretManagerServiceClient')
    def test_main_success(self, mock_client):
        # Mock command line arguments and environment variables
        with patch('argparse.ArgumentParser.parse_args') as mock_argparse,
             patch.dict(os.environ, {'GOOGLE_CLOUD_PROJECT': 'test-project'}):

            # Configure mock command line arguments
            mock_argparse.return_value.secret_id = 'test-secret'
            mock_argparse.return_value.version_id = 'test-version'

            # Configure the mock client to return a mock secret version.
            mock_response = secretmanager_v1.SecretVersion()
            mock_client.return_value.get_secret_version.return_value = mock_response

            # Mock the to_dict method to avoid errors during JSON serialization
            with patch.object(secretmanager_v1.SecretVersion, 'to_dict', return_value={})
 as mock_to_dict,
                    patch('sys.stdout') as mock_stdout:

                # Call the main part of the script
                try:
                    secret_version.main()
                except SystemExit as e:
                    self.assertEqual(e.code, None) # Expect successful exit

                # Assert that the client's get_secret_version method was called with the correct arguments.
                mock_client.return_value.get_secret_version.assert_called_once()

                # Assert that the to_dict method was called
                mock_to_dict.assert_called_once_with(mock_response)

                # Assert that the output was printed to stdout
                self.assertIn('{}', mock_stdout.getvalue())

    @patch('argparse.ArgumentParser.parse_args')
    def test_main_missing_env_var(self, mock_argparse):
        # Mock command line arguments and environment variables
        with patch.dict(os.environ, clear=True):
            # Configure mock command line arguments
            mock_argparse.return_value.secret_id = 'test-secret'
            mock_argparse.return_value.version_id = 'test-version'

            # Call the main part of the script and expect a ValueError
            with self.assertRaises(ValueError) as context:
                secret_version.main()

            self.assertEqual(str(context.exception), 'GCP_PROJECT_ID environment variable not set.')

    @patch('argparse.ArgumentParser.parse_args')
    def test_main_exception(self, mock_argparse):
        # Mock command line arguments and environment variables
        with patch.dict(os.environ, {'GOOGLE_CLOUD_PROJECT': 'test-project'})
, patch('google.cloud.secretmanager_v1.SecretManagerServiceClient') as mock_client:

            # Configure mock command line arguments
            mock_argparse.return_value.secret_id = 'test-secret'
            mock_argparse.return_value.version_id = 'test-version'

            # Configure the mock client to raise an exception.
            mock_client.return_value.get_secret_version.side_effect = Exception('API error')

            # Call the main part of the script and expect a SystemExit
            with self.assertRaises(SystemExit) as context, patch('sys.stdout') as mock_stdout:
                secret_version.main()

            self.assertEqual(context.exception.code, 1)
            self.assertIn('Failed to execute sample', mock_stdout.getvalue())

if __name__ == '__main__':
    unittest.main()
