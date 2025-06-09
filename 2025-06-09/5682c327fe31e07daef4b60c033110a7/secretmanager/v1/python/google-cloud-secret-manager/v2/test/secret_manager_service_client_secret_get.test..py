import os
import unittest
from unittest.mock import MagicMock, patch
import json

from google.api_core import exceptions

# Import the code that needs to be tested from the file
import secret_manager_service_client_secret_get


class TestSecretManager(unittest.TestCase):

    @patch('secret_manager_service_client_secret_get.secretmanager_v1.SecretManagerServiceClient')
    def test_get_secret_sample_success(self, mock_client):
        # Configure the mock client to return a sample secret
        mock_secret = MagicMock()
        mock_secret.to_dict.return_value = {"name": "test-secret"}
        mock_client.return_value.get_secret.return_value = mock_secret

        # Call the function with test arguments
        project_id = "test-project"
        secret_id = "test-secret"
        result = secret_manager_service_client_secret_get.get_secret_sample(project_id, secret_id)

        # Assert that the client was called with the correct arguments
        mock_client.return_value.get_secret.assert_called_once()

        # Assert that the function returns the expected result
        self.assertEqual(result, {"name": "test-secret"})

    @patch('secret_manager_service_client_secret_get.secretmanager_v1.SecretManagerServiceClient')
    def test_get_secret_sample_not_found(self, mock_client):
        # Configure the mock client to raise a NotFound exception
        mock_client.return_value.get_secret.side_effect = exceptions.NotFound("Secret not found")

        # Call the function with test arguments and assert that it raises a ValueError
        project_id = "test-project"
        secret_id = "test-secret"
        with self.assertRaises(ValueError):
            secret_manager_service_client_secret_get.get_secret_sample(project_id, secret_id)

    @patch('secret_manager_service_client_secret_get.secretmanager_v1.SecretManagerServiceClient')
    def test_get_secret_sample_other_exception(self, mock_client):
        # Configure the mock client to raise a generic exception
        mock_client.return_value.get_secret.side_effect = Exception("Some other error")

        # Call the function with test arguments and assert that it raises a RuntimeError
        project_id = "test-project"
        secret_id = "test-secret"
        with self.assertRaises(RuntimeError):
            secret_manager_service_client_secret_get.get_secret_sample(project_id, secret_id)

    @patch('secret_manager_service_client_secret_get.get_secret_sample')
    @patch('argparse.ArgumentParser.parse_args')
    @patch('os.environ.get')
    @patch('sys.stdout')
    def test_main_success(self, mock_stdout, mock_environ_get, mock_parse_args, mock_get_secret_sample):
        # Mock the arguments passed to main
        mock_args = MagicMock()
        mock_args.project_id = 'test-project'
        mock_args.secret_id = 'test-secret'
        mock_parse_args.return_value = mock_args

        # Mock the get_secret_sample function
        mock_get_secret_sample.return_value = {"name": "test-secret"}

        # Call the main function
        secret_manager_service_client_secret_get.main()

        # Assert that get_secret_sample was called with the correct arguments
        mock_get_secret_sample.assert_called_once_with('test-project', 'test-secret')

        # Assert that the output was printed to stdout
        mock_stdout.write.assert_called_once_with(json.dumps({"name": "test-secret"}, indent=2) + '\n')

    @patch('secret_manager_service_client_secret_get.get_secret_sample')
    @patch('argparse.ArgumentParser.parse_args')
    @patch('os.environ.get')
    @patch('sys.stderr')
    def test_main_value_error(self, mock_stderr, mock_environ_get, mock_parse_args, mock_get_secret_sample):
        # Mock the arguments passed to main
        mock_args = MagicMock()
        mock_args.project_id = 'test-project'
        mock_args.secret_id = 'test-secret'
        mock_parse_args.return_value = mock_args

        # Mock the get_secret_sample function to raise a ValueError
        mock_get_secret_sample.side_effect = ValueError("Test value error")

        with self.assertRaises(SystemExit) as cm:
            secret_manager_service_client_secret_get.main()

        self.assertEqual(cm.exception.code, 1)
        mock_stderr.write.assert_called_once_with('Error: Test value error\n')

    @patch('secret_manager_service_client_secret_get.get_secret_sample')
    @patch('argparse.ArgumentParser.parse_args')
    @patch('os.environ.get')
    @patch('sys.stderr')
    def test_main_no_project_id(self, mock_stderr, mock_environ_get, mock_parse_args, mock_get_secret_sample):
        # Mock the arguments passed to main
        mock_args = MagicMock()
        mock_args.project_id = None
        mock_args.secret_id = 'test-secret'
        mock_parse_args.return_value = mock_args

        # Mock the environment variable
        mock_environ_get.return_value = None

        # Mock the parser error
        mock_parser = MagicMock()
        mock_parse_args.return_value = mock_args
        mock_parse_args.side_effect = lambda: mock_parser.error("error message")

        # Call the main function
        with self.assertRaises(AttributeError):
            secret_manager_service_client_secret_get.main()

if __name__ == '__main__':
    unittest.main()
