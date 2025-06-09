import os
import unittest
from unittest.mock import MagicMock, patch
import json

from google.api_core import exceptions
from google.cloud import secretmanager_v1beta1

# Assuming your script is named 'secret_manager_service_client_secret_get.py'
import secret_manager_service_client_secret_get


class TestGetSecretSample(unittest.TestCase):

    @patch('secret_manager_service_client_secret_get.secretmanager_v1beta1.SecretManagerServiceClient')
    def test_get_secret_success(self, mock_client):
        # Mock the SecretManagerServiceClient and its methods
        mock_secret = MagicMock()
        mock_secret.name = 'projects/test-project/secrets/test-secret'
        mock_client_instance = mock_client.return_value
        mock_client_instance.get_secret.return_value = mock_secret

        # Call the function with test values
        project_id = 'test-project'
        secret_id = 'test-secret'
        result = secret_manager_service_client_secret_get.get_secret_sample(project_id, secret_id)

        # Assert that the client's get_secret method was called with the correct name
        mock_client_instance.get_secret.assert_called_once_with(name='projects/test-project/secrets/test-secret')

        # Assert that the function returns the mock secret
        self.assertEqual(result, mock_secret)

    @patch('secret_manager_service_client_secret_get.secretmanager_v1beta1.SecretManagerServiceClient')
    def test_get_secret_not_found(self, mock_client):
        # Mock the SecretManagerServiceClient to raise a NotFound exception
        mock_client_instance = mock_client.return_value
        mock_client_instance.get_secret.side_effect = exceptions.NotFound('Secret not found')

        # Call the function with test values
        project_id = 'test-project'
        secret_id = 'test-secret'
        result = secret_manager_service_client_secret_get.get_secret_sample(project_id, secret_id)

        # Assert that the function returns None
        self.assertIsNone(result)

    @patch('secret_manager_service_client_secret_get.secretmanager_v1beta1.SecretManagerServiceClient')
    def test_get_secret_other_exception(self, mock_client):
        # Mock the SecretManagerServiceClient to raise a generic exception
        mock_client_instance = mock_client.return_value
        mock_client_instance.get_secret.side_effect = Exception('Some other error')

        # Call the function with test values
        project_id = 'test-project'
        secret_id = 'test-secret'
        result = secret_manager_service_client_secret_get.get_secret_sample(project_id, secret_id)

        # Assert that the function returns None
        self.assertIsNone(result)


class TestMain(unittest.TestCase):

    @patch('secret_manager_service_client_secret_get.get_secret_sample')
    @patch('argparse.ArgumentParser.parse_args', return_value=unittest.mock.MagicMock(secret_id='test-secret'))
    @patch.dict(os.environ, {'GCP_PROJECT_ID': 'test-project'})  # Mock environment variable
    @patch('builtins.print')  # Capture print output
    @patch('secret_manager_service_client_secret_get.MessageToDict')
    @patch('json.dumps')
    def test_main_success(self, mock_json_dumps, mock_message_to_dict, mock_print, mock_parse_args, mock_get_secret_sample):
        # Mock successful secret retrieval
        mock_secret = MagicMock()
        mock_get_secret_sample.return_value = mock_secret
        mock_message_to_dict.return_value = {'test': 'data'}
        mock_json_dumps.return_value = '{"test": "data"}'

        # Call main function
        secret_manager_service_client_secret_get.main()

        # Assert that get_secret_sample was called with correct arguments
        mock_get_secret_sample.assert_called_once_with('test-project', 'test-secret')

        # Assert that print was called with the JSON output
        mock_print.assert_called_once_with('{\