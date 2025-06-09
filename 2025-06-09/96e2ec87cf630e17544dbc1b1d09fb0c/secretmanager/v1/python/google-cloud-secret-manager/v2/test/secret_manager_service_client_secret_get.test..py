import unittest
import os
from unittest.mock import MagicMock, patch
import json

# Assuming the code under test is in 'secret_manager_service_client_secret_get.py'
import secret_manager_service_client_secret_get
from google.api_core import exceptions
from google.cloud import secretmanager_v1


class TestGetSecretSample(unittest.TestCase):

    @patch('secret_manager_service_client_secret_get.secretmanager_v1.SecretManagerServiceClient')
    def test_get_secret_success(self, MockClient):
        # Mock the SecretManagerServiceClient and its methods
        mock_client = MockClient.return_value
        mock_secret = secretmanager_v1.Secret()
        mock_secret.name = 'projects/test-project/secrets/test-secret'
        mock_client.get_secret.return_value = mock_secret

        # Call the function with test values
        project_id = 'test-project'
        secret_id = 'test-secret'
        result = secret_manager_service_client_secret_get.get_secret_sample(project_id, secret_id)

        # Assert that the client's get_secret method was called with the correct name
        mock_client.get_secret.assert_called_once()
        args, kwargs = mock_client.get_secret.call_args
        self.assertEqual(kwargs['name'], 'projects/test-project/secrets/test-secret')

        # Assert that the function returns the mock secret
        self.assertEqual(result, mock_secret)

    @patch('secret_manager_service_client_secret_get.secretmanager_v1.SecretManagerServiceClient')
    def test_get_secret_not_found(self, MockClient):
        # Mock the SecretManagerServiceClient to raise a NotFound exception
        mock_client = MockClient.return_value
        mock_client.get_secret.side_effect = exceptions.NotFound('Secret not found')

        # Call the function with test values
        project_id = 'test-project'
        secret_id = 'test-secret'
        result = secret_manager_service_client_secret_get.get_secret_sample(project_id, secret_id)

        # Assert that the function returns None
        self.assertIsNone(result)

    @patch('secret_manager_service_client_secret_get.secretmanager_v1.SecretManagerServiceClient')
    def test_get_secret_other_exception(self, MockClient):
        # Mock the SecretManagerServiceClient to raise a generic exception
        mock_client = MockClient.return_value
        mock_client.get_secret.side_effect = Exception('Some other error')

        # Call the function with test values
        project_id = 'test-project'
        secret_id = 'test-secret'
        result = secret_manager_service_client_secret_get.get_secret_sample(project_id, secret_id)

        # Assert that the function returns None
        self.assertIsNone(result)


class TestMain(unittest.TestCase):

    @patch('secret_manager_service_client_secret_get.get_secret_sample')
    @patch('argparse.ArgumentParser.parse_args', return_value=argparse.Namespace(secret_id='test-secret'))
    @patch.dict(os.environ, {'GCP_PROJECT_ID': 'test-project'})  # Mock the environment variable
    @patch('sys.stdout')
    def test_main_success(self, mock_stdout, mock_argparse, mock_get_secret_sample):
        # Mock the get_secret_sample function to return a mock secret
        mock_secret = MagicMock()
        mock_secret.name = 'projects/test-project/secrets/test-secret'
        mock_get_secret_sample.return_value = mock_secret

        # Call the main function
        secret_manager_service_client_secret_get.main()

        # Assert that get_secret_sample was called with the correct arguments
        mock_get_secret_sample.assert_called_once_with('test-project', 'test-secret')

        # Assert that the secret was printed to stdout
        expected_output = json.dumps({'name': 'projects/test-project/secrets/test-secret'}, indent=2)
        self.assertIn(expected_output, mock_stdout.getvalue())

    @patch('argparse.ArgumentParser.parse_args', return_value=argparse.Namespace(secret_id='test-secret'))
    @patch.dict(os.environ, {})  # Ensure the environment variable is not set
    def test_main_no_project_id(self, mock_argparse):
        # Assert that main raises a ValueError if GCP_PROJECT_ID is not set
        with self.assertRaises(ValueError):
            secret_manager_service_client_secret_get.main()


if __name__ == '__main__':
    unittest.main()
