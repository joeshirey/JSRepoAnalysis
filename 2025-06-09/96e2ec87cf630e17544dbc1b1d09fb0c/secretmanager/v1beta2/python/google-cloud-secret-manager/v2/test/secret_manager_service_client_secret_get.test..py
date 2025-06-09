import os
import unittest
from unittest.mock import patch
from google.api_core import exceptions
from google.cloud import secretmanager_v1beta2

# Assuming your code is in a file named 'secret_manager_service_client_secret_get.py'
import secret_manager_service_client_secret_get as target


class TestGetSecretSample(unittest.TestCase):

    @patch('secret_manager_service_client_secret_get.secretmanager_v1beta2.SecretManagerServiceClient')
    def test_get_secret_success(self, mock_client):
        # Configure the mock client to return a mock secret.
        mock_secret = secretmanager_v1beta2.types.Secret(name='projects/test-project/secrets/test-secret')
        mock_client.return_value.get_secret.return_value = mock_secret

        # Call the function.
        secret = target.get_secret_sample('test-project', 'test-secret')

        # Assert that the client was called correctly.
        mock_client.return_value.get_secret.assert_called_once()

        # Assert that the function returns the secret.
        self.assertEqual(secret, mock_secret)

    @patch('secret_manager_service_client_secret_get.secretmanager_v1beta2.SecretManagerServiceClient')
    def test_get_secret_not_found(self, mock_client):
        # Configure the mock client to raise a NotFound exception.
        mock_client.return_value.get_secret.side_effect = exceptions.NotFound('Secret not found')

        # Call the function.
        secret = target.get_secret_sample('test-project', 'test-secret')

        # Assert that the client was called correctly.
        mock_client.return_value.get_secret.assert_called_once()

        # Assert that the function returns None.
        self.assertIsNone(secret)

    @patch('secret_manager_service_client_secret_get.secretmanager_v1beta2.SecretManagerServiceClient')
    def test_get_secret_other_exception(self, mock_client):
        # Configure the mock client to raise a generic exception.
        mock_client.return_value.get_secret.side_effect = Exception('Some other error')

        # Call the function.
        secret = target.get_secret_sample('test-project', 'test-secret')

        # Assert that the client was called correctly.
        mock_client.return_value.get_secret.assert_called_once()

        # Assert that the function returns None.
        self.assertIsNone(secret)

    @patch('secret_manager_service_client_secret_get.secretmanager_v1beta2.SecretManagerServiceClient')
    @patch('secret_manager_service_client_secret_get.os.environ.get')
    @patch('secret_manager_service_client_secret_get.argparse.ArgumentParser.parse_args')
    @patch('secret_manager_service_client_secret_get.print')
    def test_main_success(self, mock_print, mock_parse_args, mock_environ_get, mock_client):
        # Mock the environment variable and command line arguments
        mock_environ_get.return_value = 'test-project'
        mock_parse_args.return_value.secret_id = 'test-secret'

        # Mock the SecretManagerServiceClient and its get_secret method
        mock_secret = secretmanager_v1beta2.types.Secret(name='projects/test-project/secrets/test-secret')
        mock_client.return_value.get_secret.return_value = mock_secret

        # Call the main function
        target.main()

        # Assert that print was called with the JSON representation of the secret
        mock_print.assert_called()
        printed_value = mock_print.call_args[0][0]
        self.assertIn('test-secret', printed_value)


    @patch('secret_manager_service_client_secret_get.os.environ.get')
    @patch('secret_manager_service_client_secret_get.print')
    def test_main_no_project_id(self, mock_print, mock_environ_get):
        # Mock the environment variable to return None, simulating no project ID
        mock_environ_get.return_value = None

        # Call the main function
        with self.assertRaises(SystemExit) as context:
            target.main()

        # Assert that the program exited with code 1
        self.assertEqual(context.exception.code, 1)

        # Assert that the error message was printed
        mock_print.assert_called()
        printed_value = mock_print.call_args[0][0]
        self.assertIn('Error: GCP_PROJECT_ID environment variable not set.', printed_value)


if __name__ == '__main__':
    unittest.main()
