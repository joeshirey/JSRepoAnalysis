import os
import unittest
from unittest.mock import MagicMock, patch
import json
import argparse
import sys

from google.api_core.exceptions import GoogleAPICallError
from google.iam.v1 import policy_pb2

# Assuming the code under test is in a file named
# 'secret_manager_service_client_iam_policy_get.py'
sys.path.append(os.path.abspath('../'))
import secret_manager_service_client_iam_policy_get as target


class TestGetIamPolicySample(unittest.TestCase):

    @patch('secret_manager_service_client_iam_policy_get.secretmanager_v1.SecretManagerServiceClient')
    def test_get_iam_policy_success(self, mock_client):
        # Mock the client and its methods
        mock_secret_path = mock_client.return_value.secret_path
        mock_secret_path.return_value = 'projects/test-project/secrets/test-secret'

        mock_get_iam_policy = mock_client.return_value.get_iam_policy
        mock_policy = policy_pb2.Policy()
        mock_policy.version = 3
        binding = mock_policy.bindings.add()
        binding.role = 'roles/viewer'
        binding.members.append('user:test@example.com')
        mock_policy.etag = b'test_etag'

        mock_get_iam_policy.return_value = mock_policy

        # Call the function
        policy = target.get_iam_policy_sample('test-project', 'test-secret')

        # Assertions
        self.assertEqual(policy.version, 3)
        self.assertEqual(len(policy.bindings), 1)
        self.assertEqual(policy.bindings[0].role, 'roles/viewer')
        self.assertEqual(policy.bindings[0].members[0], 'user:test@example.com')
        self.assertEqual(policy.etag, b'test_etag')

        # Verify that the client methods were called with the correct arguments
        mock_client.return_value.secret_path.assert_called_once_with('test-project', 'test-secret')
        mock_client.return_value.get_iam_policy.assert_called_once()
        mock_client.return_value.close.assert_called_once()

    @patch('secret_manager_service_client_iam_policy_get.secretmanager_v1.SecretManagerServiceClient')
    def test_get_iam_policy_failure(self, mock_client):
        # Mock the client to raise an exception
        mock_client.return_value.secret_path.return_value = 'projects/test-project/secrets/test-secret'
        mock_get_iam_policy = mock_client.return_value.get_iam_policy
        mock_get_iam_policy.side_effect = GoogleAPICallError('API error')

        # Call the function and assert that it raises the exception
        with self.assertRaises(GoogleAPICallError):
            target.get_iam_policy_sample('test-project', 'test-secret')

        mock_client.return_value.secret_path.assert_called_once_with('test-project', 'test-secret')
        mock_client.return_value.get_iam_policy.assert_called_once()
        mock_client.return_value.close.assert_called_once()

    @patch('secret_manager_service_client_iam_policy_get.secretmanager_v1.SecretManagerServiceClient')
    @patch('argparse.ArgumentParser.parse_args', return_value=argparse.Namespace(secret_id='test-secret'))
    @patch.dict(os.environ, {'GCP_PROJECT_ID': 'test-project'})  # Mock environment variable
    @patch('sys.stdout')
    def test_main_success(self, mock_stdout, mock_argparse, mock_client):
        # Mock the client and its methods
        mock_secret_path = mock_client.return_value.secret_path
        mock_secret_path.return_value = 'projects/test-project/secrets/test-secret'

        mock_get_iam_policy = mock_client.return_value.get_iam_policy
        mock_policy = policy_pb2.Policy()
        mock_policy.version = 3
        binding = mock_policy.bindings.add()
        binding.role = 'roles/viewer'
        binding.members.append('user:test@example.com')
        mock_policy.etag = b'test_etag'

        mock_get_iam_policy.return_value = mock_policy

        # Call the main function
        target.main()

        # Capture the output
        captured = mock_stdout.write.call_args[0][0]

        # Assertions
        self.assertIn('test-secret', captured)

        # Verify that the client methods were called with the correct arguments
        mock_client.return_value.secret_path.assert_called_once_with('test-project', 'test-secret')
        mock_client.return_value.get_iam_policy.assert_called_once()
        mock_client.return_value.close.assert_called_once()

    @patch('argparse.ArgumentParser.parse_args', return_value=argparse.Namespace(secret_id='test-secret'))
    @patch.dict(os.environ, {'GCP_PROJECT_ID': 'test-project'})  # Mock environment variable
    @patch('secret_manager_service_client_iam_policy_get.secretmanager_v1.SecretManagerServiceClient')
    @patch('sys.stderr')
    @patch('sys.exit')
    def test_main_failure(self, mock_exit, mock_stderr, mock_client, mock_argparse):
        # Mock the client to raise an exception
        mock_client.return_value.secret_path.return_value = 'projects/test-project/secrets/test-secret'
        mock_get_iam_policy = mock_client.return_value.get_iam_policy
        mock_get_iam_policy.side_effect = GoogleAPICallError('API error')

        # Call the main function
        target.main()

        # Assertions
        mock_exit.assert_called_once_with(1)

        mock_client.return_value.secret_path.assert_called_once_with('test-project', 'test-secret')
        mock_client.return_value.get_iam_policy.assert_called_once()
        mock_client.return_value.close.assert_called_once()

    @patch('argparse.ArgumentParser.parse_args', return_value=argparse.Namespace(secret_id='test-secret'))
    @patch.dict(os.environ, {})  # Mock environment variable
    @patch('sys.stderr')
    @patch('sys.exit')
    def test_main_no_project_id(self, mock_exit, mock_stderr, mock_argparse):
        # Call the main function
        target.main()

        # Assertions
        mock_exit.assert_called_once_with(1)

if __name__ == '__main__':
    unittest.main()
