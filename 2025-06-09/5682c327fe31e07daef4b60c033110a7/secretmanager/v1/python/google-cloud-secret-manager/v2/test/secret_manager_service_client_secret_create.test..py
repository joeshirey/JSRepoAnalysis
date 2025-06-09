import os
import unittest
from unittest.mock import MagicMock, patch
import json
import argparse

from google.api_core import exceptions
from google.cloud import secretmanager_v1

# Assuming the code under test is in 'secret_manager_service_client_secret_create.py'
import secret_manager_service_client_secret_create as secret_create


class TestCreateSecret(unittest.TestCase):

    @patch('secret_manager_service_client_secret_create.secretmanager_v1.SecretManagerServiceClient')
    def test_create_secret_success(self, MockClient):
        # Mock the SecretManagerServiceClient and its methods
        mock_client = MagicMock()
        MockClient.return_value = mock_client
        mock_secret = MagicMock()
        mock_secret.name = 'projects/test-project/secrets/test-secret'
        mock_secret.secret_id = 'test-secret'
        mock_secret.labels = {}
        mock_client.create_secret.return_value = mock_secret

        # Call the function with test values
        project_id = 'test-project'
        secret_id = 'test-secret'
        labels = {'env': 'test'}

        # Mock the CreateSecretRequest object
        mock_request = MagicMock()
        mock_client.create_secret.return_value = mock_secret

        # Call the function
        result = secret_create.create_secret_sample(project_id, secret_id, labels)

        # Assert that the client was called with the correct arguments
        MockClient.assert_called_once()
        mock_client.create_secret.assert_called_once()

        # Assert that the function returns the mock secret
        self.assertEqual(result, mock_secret)

    @patch('secret_manager_service_client_secret_create.secretmanager_v1.SecretManagerServiceClient')
    def test_create_secret_api_error(self, MockClient):
        # Mock the SecretManagerServiceClient to raise an exception
        mock_client = MagicMock()
        MockClient.return_value = mock_client
        mock_client.create_secret.side_effect = exceptions.PermissionDenied('Permission denied')

        # Call the function with test values
        project_id = 'test-project'
        secret_id = 'test-secret'
        labels = {'env': 'test'}

        # Assert that the function raises the expected exception
        with self.assertRaises(exceptions.GoogleAPIError):
            secret_create.create_secret_sample(project_id, secret_id, labels)

    @patch('secret_manager_service_client_secret_create.secretmanager_v1.SecretManagerServiceClient')
    def test_create_secret_no_labels(self, MockClient):
        # Mock the SecretManagerServiceClient and its methods
        mock_client = MagicMock()
        MockClient.return_value = mock_client
        mock_secret = MagicMock()
        mock_secret.name = 'projects/test-project/secrets/test-secret'
        mock_secret.secret_id = 'test-secret'
        mock_secret.labels = {}
        mock_client.create_secret.return_value = mock_secret

        # Call the function with test values
        project_id = 'test-project'
        secret_id = 'test-secret'
        labels = None

        # Mock the CreateSecretRequest object
        mock_request = MagicMock()
        mock_client.create_secret.return_value = mock_secret

        # Call the function
        result = secret_create.create_secret_sample(project_id, secret_id, labels)

        # Assert that the client was called with the correct arguments
        MockClient.assert_called_once()
        mock_client.create_secret.assert_called_once()

        # Assert that the function returns the mock secret
        self.assertEqual(result, mock_secret)

    @patch('secret_manager_service_client_secret_create.os.environ.get')
    @patch('secret_manager_service_client_secret_create.create_secret_sample')
    @patch('secret_manager_service_client_secret_create.argparse.ArgumentParser.parse_args')
    @patch('secret_manager_service_client_secret_create.open', new_callable=unittest.mock.mock_open, create=True)
    @patch('secret_manager_service_client_secret_create.json.dumps')
    def test_main_success_with_labels_file(self, mock_json_dumps, mock_open, mock_parse_args, mock_create_secret_sample, mock_os_environ_get, capsys):
        # Mock the environment variable
        mock_os_environ_get.return_value = 'test-project'

        # Mock the command-line arguments
        mock_args = argparse.Namespace(secret_id='test-secret', labels_file='labels.json')
        mock_parse_args.return_value = mock_args

        # Mock the labels file content
        mock_open.return_value.read.return_value = '{"env": "test"}'

        # Mock the create_secret_sample function
        mock_secret = MagicMock()
        mock_secret.name = 'projects/test-project/secrets/test-secret'
        mock_secret.secret_id = 'test-secret'
        mock_secret.labels = {}
        mock_create_secret_sample.return_value = mock_secret

        # Mock json.dumps
        mock_json_dumps.return_value = '{"secret_name": "projects/test-project/secrets/test-secret", "secret_id": "test-secret", "labels": {}}'

        # Call the main function
        secret_create.main()

        # Assert that create_secret_sample was called with the correct arguments
        mock_create_secret_sample.assert_called_once_with(project_id='test-project', secret_id='test-secret', labels={'env': 'test'})

        # Capture stdout and assert the expected output
        captured = capsys.readouterr()
        self.assertEqual(captured.out.strip(), '{"secret_name": "projects/test-project/secrets/test-secret", "secret_id": "test-secret", "labels": {}}')

    @patch('secret_manager_service_client_secret_create.os.environ.get')
    @patch('secret_manager_service_client_secret_create.create_secret_sample')
    @patch('secret_manager_service_client_secret_create.argparse.ArgumentParser.parse_args')
    @patch('secret_manager_service_client_secret_create.open', new_callable=unittest.mock.mock_open, create=True)
    @patch('secret_manager_service_client_secret_create.json.dumps')
    def test_main_success_without_labels_file(self, mock_json_dumps, mock_open, mock_parse_args, mock_create_secret_sample, mock_os_environ_get, capsys):
        # Mock the environment variable
        mock_os_environ_get.return_value = 'test-project'

        # Mock the command-line arguments
        mock_args = argparse.Namespace(secret_id='test-secret', labels_file=None)
        mock_parse_args.return_value = mock_args

        # Mock the create_secret_sample function
        mock_secret = MagicMock()
        mock_secret.name = 'projects/test-project/secrets/test-secret'
        mock_secret.secret_id = 'test-secret'
        mock_secret.labels = {}
        mock_create_secret_sample.return_value = mock_secret

        # Mock json.dumps
        mock_json_dumps.return_value = '{"secret_name": "projects/test-project/secrets/test-secret", "secret_id": "test-secret", "labels": {}}'

        # Call the main function
        secret_create.main()

        # Assert that create_secret_sample was called with the correct arguments
        mock_create_secret_sample.assert_called_once_with(project_id='test-project', secret_id='test-secret', labels=None)

        # Capture stdout and assert the expected output
        captured = capsys.readouterr()
        self.assertEqual(captured.out.strip(), '{"secret_name": "projects/test-project/secrets/test-secret", "secret_id": "test-secret", "labels": {}}')

    @patch('secret_manager_service_client_secret_create.os.environ.get')
    @patch('secret_manager_service_client_secret_create.argparse.ArgumentParser.parse_args')
    def test_main_missing_project_id(self, mock_parse_args, mock_os_environ_get, capsys):
        # Mock the environment variable to return None (missing project ID)
        mock_os_environ_get.return_value = None

        # Mock the command-line arguments
        mock_args = argparse.Namespace(secret_id='test-secret', labels_file=None)
        mock_parse_args.return_value = mock_args

        # Call the main function and assert that it raises a ValueError
        with self.assertRaises(ValueError) as context:
            secret_create.main()

        self.assertEqual(str(context.exception), "Environment variable GCP_PROJECT_ID must be set.")


if __name__ == '__main__':
    unittest.main()
