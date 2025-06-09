import os
import unittest
from unittest.mock import MagicMock, patch
import json

from google.iam.v1 import policy_pb2

# Assuming your code is in 'secret_manager_service_client_iam_policy_get.py'
import secret_manager_service_client_iam_policy_get as target

class TestGetIamPolicySample(unittest.TestCase):

    @patch('secret_manager_service_client_iam_policy_get.secretmanager_v1.SecretManagerServiceClient')
    def test_get_iam_policy_sample_success(self, mock_client):
        # Mock the SecretManagerServiceClient and its methods
        mock_secret_manager_client = mock_client.return_value
        mock_secret_manager_client.secret_path.return_value = 'projects/test-project/secrets/test-secret'

        # Create a mock policy object
        mock_policy = policy_pb2.Policy()
        mock_policy.version = 3
        binding = mock_policy.bindings.add()
        binding.role = 'roles/test.role'
        binding.members.append('user:test@example.com')
        binding.condition.expression = 'test == value'
        binding.condition.title = 'test_title'
        binding.condition.description = 'test_description'
        mock_policy.etag = b'test_etag'

        mock_secret_manager_client.get_iam_policy.return_value = mock_policy

        # Call the function
        policy = target.get_iam_policy_sample('test-project', 'test-secret')

        # Assert the client methods were called with the correct arguments
        mock_secret_manager_client.secret_path.assert_called_with('test-project', 'test-secret')
        mock_secret_manager_client.get_iam_policy.assert_called_once()

        # Assert the returned policy is correct
        self.assertEqual(policy.version, 3)
        self.assertEqual(policy.bindings[0].role, 'roles/test.role')
        self.assertEqual(policy.bindings[0].members[0], 'user:test@example.com')
        self.assertEqual(policy.bindings[0].condition.expression, 'test == value')
        self.assertEqual(policy.bindings[0].condition.title, 'test_title')
        self.assertEqual(policy.bindings[0].condition.description, 'test_description')
        self.assertEqual(policy.etag, b'test_etag')

        # Assert the client was closed
        mock_secret_manager_client.close.assert_called_once()

    @patch('secret_manager_service_client_iam_policy_get.secretmanager_v1.SecretManagerServiceClient')
    def test_get_iam_policy_sample_exception(self, mock_client):
        # Mock the SecretManagerServiceClient to raise an exception
        mock_secret_manager_client = mock_client.return_value
        mock_secret_manager_client.secret_path.return_value = 'projects/test-project/secrets/test-secret'
        mock_secret_manager_client.get_iam_policy.side_effect = Exception('Test exception')

        # Call the function and assert it raises the exception
        with self.assertRaises(Exception) as context:
            target.get_iam_policy_sample('test-project', 'test-secret')

        self.assertEqual(str(context.exception), 'Test exception')

        # Assert the client was closed
        mock_secret_manager_client.close.assert_called_once()

    @patch('secret_manager_service_client_iam_policy_get.os.environ.get')
    @patch('secret_manager_service_client_iam_policy_get.get_iam_policy_sample')
    @patch('secret_manager_service_client_iam_policy_get.argparse.ArgumentParser.parse_args')
    @patch('secret_manager_service_client_iam_policy_get.json.dumps')
    @patch('builtins.print')
    def test_main_success(self, mock_print, mock_json_dumps, mock_parse_args, mock_get_iam_policy_sample, mock_os_environ_get):
        # Mock the environment variable
        mock_os_environ_get.return_value = 'test-project'

        # Mock the command line arguments
        mock_args = MagicMock()
        mock_args.secret_id = 'test-secret'
        mock_parse_args.return_value = mock_args

        # Mock the get_iam_policy_sample function
        mock_policy = policy_pb2.Policy()
        mock_policy.version = 3
        binding = mock_policy.bindings.add()
        binding.role = 'roles/test.role'
        binding.members.append('user:test@example.com')
        binding.condition.expression = 'test == value'
        binding.condition.title = 'test_title'
        binding.condition.description = 'test_description'
        mock_policy.etag = b'test_etag'

        mock_get_iam_policy_sample.return_value = mock_policy

        # Mock json.dumps
        mock_json_dumps.return_value = '{"test": "json"}'

        # Call the main function
        target.main()

        # Assert the functions were called with the correct arguments
        mock_os_environ_get.assert_called_with('GCP_PROJECT_ID')
        mock_parse_args.assert_called_once()
        mock_get_iam_policy_sample.assert_called_with('test-project', 'test-secret')
        mock_json_dumps.assert_called()
        mock_print.assert_called_with('{"test": "json"}')

    @patch('secret_manager_service_client_iam_policy_get.os.environ.get')
    @patch('secret_manager_service_client_iam_policy_get.get_iam_policy_sample')
    @patch('secret_manager_service_client_iam_policy_get.argparse.ArgumentParser.parse_args')
    @patch('builtins.print')
    def test_main_exception(self, mock_print, mock_parse_args, mock_get_iam_policy_sample, mock_os_environ_get):
        # Mock the environment variable
        mock_os_environ_get.return_value = 'test-project'

        # Mock the command line arguments
        mock_args = MagicMock()
        mock_args.secret_id = 'test-secret'
        mock_parse_args.return_value = mock_args

        # Mock the get_iam_policy_sample function to raise an exception
        mock_get_iam_policy_sample.side_effect = Exception('Test exception')

        # Call the main function
        with self.assertRaises(SystemExit) as cm:
            target.main()

        # Assert the functions were called with the correct arguments
        mock_os_environ_get.assert_called_with('GCP_PROJECT_ID')
        mock_parse_args.assert_called_once()
        mock_get_iam_policy_sample.assert_called_with('test-project', 'test-secret')
        mock_print.assert_called()

        self.assertEqual(cm.exception.code, 1)

    @patch('secret_manager_service_client_iam_policy_get.os.environ.get')
    @patch('builtins.print')
    def test_main_no_project_id(self, mock_print, mock_os_environ_get):
        # Mock the environment variable to return None
        mock_os_environ_get.return_value = None

        # Call the main function
        with self.assertRaises(SystemExit) as cm:
            target.main()

        # Assert the functions were called with the correct arguments
        mock_os_environ_get.assert_called_with('GCP_PROJECT_ID')
        mock_print.assert_called_with('Error: GCP_PROJECT_ID environment variable not set.')

        self.assertEqual(cm.exception.code, 1)

if __name__ == '__main__':
    unittest.main()
