import os
import unittest
from unittest.mock import MagicMock, patch
import argparse
import json

from google.api_core import exceptions
from google.cloud import secretmanager_v1
from google.protobuf.json_format import MessageToDict

# Import the code to be tested
import secret_manager_service_client_secret_get


class TestGetSecretSample(unittest.TestCase):

    @patch('secret_manager_service_client_secret_get.secretmanager_v1.SecretManagerServiceClient')
    def test_get_secret_success(self, mock_client):
        # Configure the mock client
        mock_secret = MagicMock()
        mock_secret.name = 'projects/test-project/secrets/test-secret'
        mock_client.return_value.get_secret.return_value = mock_secret

        # Call the function
        secret = secret_manager_service_client_secret_get.get_secret_sample('test-project', 'test-secret')

        # Assert that the client was called correctly
        mock_client.return_value.get_secret.assert_called_once_with(name='projects/test-project/secrets/test-secret')

        # Assert that the secret is returned
        self.assertEqual(secret, mock_secret)

    @patch('secret_manager_service_client_secret_get.secretmanager_v1.SecretManagerServiceClient')
    def test_get_secret_not_found(self, mock_client):
        # Configure the mock client to raise a NotFound exception
        mock_client.return_value.get_secret.side_effect = exceptions.NotFound('Secret not found')

        # Capture stdout
        with patch('sys.stdout') as mock_stdout:
            # Call the function
            secret = secret_manager_service_client_secret_get.get_secret_sample('test-project', 'test-secret')

            # Assert that the client was called correctly
            mock_client.return_value.get_secret.assert_called_once_with(name='projects/test-project/secrets/test-secret')

            # Assert that the function returns None
            self.assertIsNone(secret)

            # Assert that the correct message was printed to stdout
            mock_stdout.write.assert_called_with("Secret 'projects/test-project/secrets/test-secret' not found.\n")

    @patch('secret_manager_service_client_secret_get.secretmanager_v1.SecretManagerServiceClient')
    def test_get_secret_error(self, mock_client):
        # Configure the mock client to raise an exception
        mock_client.return_value.get_secret.side_effect = Exception('An error occurred')

        # Capture stdout
        with patch('sys.stdout') as mock_stdout:
            # Call the function
            secret = secret_manager_service_client_secret_get.get_secret_sample('test-project', 'test-secret')

            # Assert that the client was called correctly
            mock_client.return_value.get_secret.assert_called_once_with(name='projects/test-project/secrets/test-secret')

            # Assert that the function returns None
            self.assertIsNone(secret)

            # Assert that the correct message was printed to stdout
            mock_stdout.write.assert_called_with("An error occurred: An error occurred\n")


class TestMain(unittest.TestCase):

    @patch('secret_manager_service_client_secret_get.get_secret_sample')
    @patch('argparse.ArgumentParser.parse_args', return_value=argparse.Namespace(project_id='test-project', secret_id='test-secret'))
    @patch('secret_manager_service_client_secret_get.MessageToDict')
    @patch('sys.stdout')
    def test_main_success(self, mock_stdout, mock_message_to_dict, mock_parse_args, mock_get_secret_sample):
        # Configure mocks
        mock_secret = MagicMock()
        mock_get_secret_sample.return_value = mock_secret
        mock_message_to_dict.return_value = {'name': 'test-secret'}

        # Call main function
        secret_manager_service_client_secret_get.main()

        # Assertions
        mock_get_secret_sample.assert_called_once_with('test-project', 'test-secret')
        mock_message_to_dict.assert_called_once_with(mock_secret, preserving_proto_field_name=True)
        mock_stdout.write.assert_called_once()
        call_args = mock_stdout.write.call_args
        self.assertTrue('test-secret' in call_args[0][0])

    @patch('argparse.ArgumentParser.parse_args', return_value=argparse.Namespace(project_id='test-project', secret_id='test-secret'))
    @patch('secret_manager_service_client_secret_get.get_secret_sample')
    def test_main_secret_not_found(self, mock_get_secret_sample, mock_parse_args):
        # Configure mocks
        mock_get_secret_sample.return_value = None

        # Call main function and assert that SystemExit is raised
        with self.assertRaises(SystemExit) as context:
            secret_manager_service_client_secret_get.main()

        # Assert that the exit code is 1
        self.assertEqual(context.exception.code, 1)

    @patch('argparse.ArgumentParser.parse_args', return_value=argparse.Namespace(project_id=None, secret_id='test-secret'))
    def test_main_no_project_id(self, mock_parse_args):
        # Unset the environment variable if it exists to ensure the test fails if it relies on it.
        if 'GCP_PROJECT_ID' in os.environ:
            del os.environ['GCP_PROJECT_ID']

        # Call main function and assert that ValueError is raised
        with self.assertRaises(ValueError) as context:
            secret_manager_service_client_secret_get.main()

        # Assert that the correct error message is raised
        self.assertEqual(str(context.exception), 'Project ID must be provided either via --project_id or the GCP_PROJECT_ID environment variable.')


if __name__ == '__main__':
    unittest.main()
