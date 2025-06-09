import os
import unittest
from unittest.mock import patch
import sys
import json

from google.api_core import exceptions
from google.cloud import secretmanager_v1beta2

# Import the code to be tested
sys.path.append('..')
import secret_manager_service_client_secret_get


class TestGetSecretSample(unittest.TestCase):

    @patch('secret_manager_service_client_secret_get.secretmanager_v1beta2.SecretManagerServiceClient')
    def test_get_secret_success(self, mock_client):
        # Configure the mock client
        mock_secret = secretmanager_v1beta2.Secret()
        mock_secret.name = 'projects/fake-project/secrets/fake-secret'
        mock_instance = mock_client.return_value
        mock_instance.get_secret.return_value = mock_secret

        # Call the function
        secret = secret_manager_service_client_secret_get.get_secret_sample('fake-project', 'fake-secret')

        # Assert that the client was called correctly
        mock_instance.get_secret.assert_called_once()

        # Assert that the function returns the secret
        self.assertEqual(secret, mock_secret)

    @patch('secret_manager_service_client_secret_get.secretmanager_v1beta2.SecretManagerServiceClient')
    def test_get_secret_not_found(self, mock_client):
        # Configure the mock client to raise a NotFound exception
        mock_instance = mock_client.return_value
        mock_instance.get_secret.side_effect = exceptions.NotFound('Secret not found')

        # Capture stdout
        captured_output = sys.stdout = open('test_output.txt', 'w')

        # Call the function
        secret = secret_manager_service_client_secret_get.get_secret_sample('fake-project', 'fake-secret')

        # Restore stdout
        sys.stdout = sys.__stdout__
        captured_output.close()

        # Read the captured output
        with open('test_output.txt', 'r') as f:
            output = f.read()
        os.remove('test_output.txt')

        # Assert that the client was called correctly
        mock_instance.get_secret.assert_called_once()

        # Assert that the function returns None
        self.assertIsNone(secret)

        # Assert that the correct message was printed to stderr
        self.assertIn("Secret 'projects/fake-project/secrets/fake-secret' not found.", output)

    @patch('secret_manager_service_client_secret_get.secretmanager_v1beta2.SecretManagerServiceClient')
    def test_get_secret_other_exception(self, mock_client):
        # Configure the mock client to raise an exception
        mock_instance = mock_client.return_value
        mock_instance.get_secret.side_effect = Exception('Something went wrong')

        # Capture stdout
        captured_output = sys.stdout = open('test_output.txt', 'w')

        # Call the function
        secret = secret_manager_service_client_secret_get.get_secret_sample('fake-project', 'fake-secret')

        # Restore stdout
        sys.stdout = sys.__stdout__
        captured_output.close()

        # Read the captured output
        with open('test_output.txt', 'r') as f:
            output = f.read()
        os.remove('test_output.txt')

        # Assert that the client was called correctly
        mock_instance.get_secret.assert_called_once()

        # Assert that the function returns None
        self.assertIsNone(secret)

        # Assert that the correct message was printed to stderr
        self.assertIn("An error occurred: Something went wrong", output)

    @patch('secret_manager_service_client_secret_get.os.environ.get')
    @patch('secret_manager_service_client_secret_get.get_secret_sample')
    @patch('secret_manager_service_client_secret_get.secretmanager_v1beta2.Secret.to_json')
    @patch('secret_manager_service_client_secret_get.json.dumps')
    @patch('secret_manager_service_client_secret_get.json.loads')
    @patch('argparse.ArgumentParser.parse_args')
    def test_main_success(self, mock_parse_args, mock_loads, mock_dumps, mock_to_json, mock_get_secret_sample, mock_os_environ_get):
        # Mock the arguments
        mock_parse_args.return_value.secret_id = 'test-secret'
        mock_os_environ_get.return_value = 'test-project'
        mock_secret = secretmanager_v1beta2.Secret()
        mock_get_secret_sample.return_value = mock_secret
        mock_to_json.return_value = '{"test": "json"}'
        mock_loads.return_value = {"test": "json"}
        mock_dumps.return_value = '{\n  "test": "json"\n}'

        # Capture stdout
        captured_output = sys.stdout = open('test_output.txt', 'w')

        # Call main function
        secret_manager_service_client_secret_get.main()

        # Restore stdout
        sys.stdout = sys.__stdout__
        captured_output.close()

        # Read the captured output
        with open('test_output.txt', 'r') as f:
            output = f.read()
        os.remove('test_output.txt')

        # Assertions
        mock_get_secret_sample.assert_called_once_with('test-project', 'test-secret')
        mock_to_json.assert_called_once_with(mock_secret)
        mock_dumps.assert_called_once_with({"test": "json"}, indent=2)
        self.assertEqual('{\n  "test": "json"\n}', output)

    @patch('secret_manager_service_client_secret_get.os.environ.get')
    @patch('secret_manager_service_client_secret_get.get_secret_sample')
    @patch('argparse.ArgumentParser.parse_args')
    def test_main_secret_none(self, mock_parse_args, mock_get_secret_sample, mock_os_environ_get):
        # Mock the arguments
        mock_parse_args.return_value.secret_id = 'test-secret'
        mock_os_environ_get.return_value = 'test-project'
        mock_get_secret_sample.return_value = None

        # Capture stderr
        captured_error = sys.stderr = open('test_error.txt', 'w')

        # Call main function
        with self.assertRaises(SystemExit) as cm:
            secret_manager_service_client_secret_get.main()

        # Restore stderr
        sys.stderr = sys.__stderr__
        captured_error.close()

        # Read the captured output
        with open('test_error.txt', 'r') as f:
            output = f.read()
        os.remove('test_error.txt')

        # Assertions
        mock_get_secret_sample.assert_called_once_with('test-project', 'test-secret')
        self.assertEqual(cm.exception.code, 1)
        self.assertEqual(output, '')

    @patch('secret_manager_service_client_secret_get.os.environ.get')
    @patch('argparse.ArgumentParser.parse_args')
    def test_main_no_project_id(self, mock_parse_args, mock_os_environ_get):
        # Mock the arguments
        mock_parse_args.return_value.secret_id = 'test-secret'
        mock_os_environ_get.return_value = None

        # Capture stderr
        captured_error = sys.stderr = open('test_error.txt', 'w')

        # Call main function
        with self.assertRaises(SystemExit) as cm:
            secret_manager_service_client_secret_get.main()

        # Restore stderr
        sys.stderr = sys.__stderr__
        captured_error.close()

        # Read the captured output
        with open('test_error.txt', 'r') as f:
            output = f.read()
        os.remove('test_error.txt')

        # Assertions
        self.assertEqual(cm.exception.code, 1)
        self.assertEqual(output, 'Error: GCP_PROJECT_ID environment variable not set.\n')

if __name__ == '__main__':
    unittest.main()
