import os
import unittest
from unittest.mock import MagicMock, patch
import sys
import json

# Assuming the code under test is in a file named 'secret_manager_service_client_secret_create.py'
sys.path.append('..')
import secret_manager_service_client_secret_create

class TestCreateSecret(unittest.TestCase):

    @patch('google.cloud.secretmanager_v1beta2.SecretManagerServiceClient')
    def test_create_secret_success(self, mock_client):
        # Mock the Secret object
        mock_secret = MagicMock()
        mock_secret.name = 'projects/fake-project/secrets/fake-secret'

        # Mock the client's create_secret method to return the mock secret
        mock_client_instance = mock_client.return_value
        mock_client_instance.create_secret.return_value = mock_secret

        # Call the function with test values
        project_id = 'fake-project'
        secret_id = 'fake-secret'
        created_secret = secret_manager_service_client_secret_create.create_secret_sample(project_id, secret_id)

        # Assert that the client's create_secret method was called with the correct arguments
        mock_client_instance.create_secret.assert_called_once()
        args, kwargs = mock_client_instance.create_secret.call_args
        self.assertEqual(kwargs['parent'], f'projects/{project_id}')
        self.assertEqual(kwargs['secret_id'], secret_id)
        self.assertIsNotNone(kwargs['secret'])

        # Assert that the function returns the mock secret
        self.assertEqual(created_secret, mock_secret)

    @patch('google.cloud.secretmanager_v1beta2.SecretManagerServiceClient')
    def test_create_secret_failure(self, mock_client):
        # Mock the client's create_secret method to raise an exception
        mock_client_instance = mock_client.return_value
        mock_client_instance.create_secret.side_effect = Exception('API error')

        # Call the function with test values and assert that it raises an exception
        project_id = 'fake-project'
        secret_id = 'fake-secret'
        with self.assertRaises(Exception) as context:
            secret_manager_service_client_secret_create.create_secret_sample(project_id, secret_id)

        self.assertEqual(str(context.exception), 'API error')

    @patch('secret_manager_service_client_secret_create.create_secret_sample')
    @patch('os.environ.get')
    @patch('argparse.ArgumentParser.parse_args')
    @patch('sys.exit')
    @patch('json.dumps')
    def test_main_success(self, mock_json_dumps, mock_sys_exit, mock_parse_args, mock_os_environ_get, mock_create_secret_sample):
        # Mock the command-line arguments
        mock_args = MagicMock()
        mock_args.secret_id = 'test-secret'
        mock_parse_args.return_value = mock_args

        # Mock the environment variable
        mock_os_environ_get.return_value = 'test-project'

        # Mock the create_secret_sample function
        mock_secret = MagicMock()
        mock_secret._pb = MagicMock()
        mock_create_secret_sample.return_value = mock_secret

        # Call the main function
        secret_manager_service_client_secret_create.main()

        # Assert that the create_secret_sample function was called with the correct arguments
        mock_create_secret_sample.assert_called_once_with('test-project', 'test-secret')

        # Assert that json.dumps was called
        mock_json_dumps.assert_called_once()

        # Assert that sys.exit was not called
        mock_sys_exit.assert_not_called()

    @patch('os.environ.get')
    @patch('argparse.ArgumentParser.parse_args')
    @patch('sys.exit')
    def test_main_no_project_id(self, mock_sys_exit, mock_parse_args, mock_os_environ_get):
        # Mock the environment variable to return None
        mock_os_environ_get.return_value = None

        # Mock the command-line arguments
        mock_args = MagicMock()
        mock_args.secret_id = 'test-secret'
        mock_parse_args.return_value = mock_args

        # Call the main function
        secret_manager_service_client_secret_create.main()

        # Assert that sys.exit was called with an error code
        mock_sys_exit.assert_called_once_with(1)

    @patch('secret_manager_service_client_secret_create.create_secret_sample')
    @patch('os.environ.get')
    @patch('argparse.ArgumentParser.parse_args')
    @patch('sys.exit')
    def test_main_create_secret_error(self, mock_sys_exit, mock_parse_args, mock_os_environ_get, mock_create_secret_sample):
        # Mock the command-line arguments
        mock_args = MagicMock()
        mock_args.secret_id = 'test-secret'
        mock_parse_args.return_value = mock_args

        # Mock the environment variable
        mock_os_environ_get.return_value = 'test-project'

        # Mock the create_secret_sample function to raise an exception
        mock_create_secret_sample.side_effect = Exception('Create secret error')

        # Call the main function
        secret_manager_service_client_secret_create.main()

        # Assert that sys.exit was called with an error code
        mock_sys_exit.assert_called_once_with(1)

if __name__ == '__main__':
    unittest.main()
