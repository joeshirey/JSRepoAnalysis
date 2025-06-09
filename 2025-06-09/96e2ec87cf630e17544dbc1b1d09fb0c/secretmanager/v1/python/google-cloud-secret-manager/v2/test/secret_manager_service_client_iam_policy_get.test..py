import os
import unittest
import argparse
import json
from unittest.mock import patch, MagicMock
from google.iam.v1 import policy_pb2
from google.cloud import secretmanager_v1

# Import the code to be tested
import secret_manager_service_client_iam_policy_get


class TestGetIamPolicySample(unittest.TestCase):

    @patch('secret_manager_service_client_iam_policy_get.secretmanager_v1.SecretManagerServiceClient')
    def test_get_iam_policy_sample_success(self, mock_client):
        # Mock the SecretManagerServiceClient and its methods
        mock_policy = policy_pb2.Policy(version=1, bindings=[], etag=b'test_etag')
        mock_client_instance = mock_client.return_value
        mock_client_instance.get_iam_policy.return_value = mock_policy

        # Call the function with a sample resource name
        resource_name = 'projects/test-project/secrets/test-secret'
        policy = secret_manager_service_client_iam_policy_get.get_iam_policy_sample(resource_name)

        # Assert that the client's get_iam_policy method was called with the correct arguments
        mock_client_instance.get_iam_policy.assert_called_once()

        # Assert that the returned policy is the mocked policy
        self.assertEqual(policy, mock_policy)

    @patch('secret_manager_service_client_iam_policy_get.secretmanager_v1.SecretManagerServiceClient')
    def test_get_iam_policy_sample_failure(self, mock_client):
        # Mock the SecretManagerServiceClient to raise an exception
        mock_client_instance = mock_client.return_value
        mock_client_instance.get_iam_policy.side_effect = Exception('Test error')

        # Call the function with a sample resource name and assert that it raises an exception
        resource_name = 'projects/test-project/secrets/test-secret'
        with self.assertRaises(Exception) as context:
            secret_manager_service_client_iam_policy_get.get_iam_policy_sample(resource_name)

        self.assertEqual(str(context.exception), 'Test error')

    @patch('secret_manager_service_client_iam_policy_get.secretmanager_v1.SecretManagerServiceClient')
    @patch('secret_manager_service_client_iam_policy_get.os.environ.get')
    @patch('secret_manager_service_client_iam_policy_get.argparse.ArgumentParser.parse_args')
    @patch('secret_manager_service_client_iam_policy_get.print')
    @patch('secret_manager_service_client_iam_policy_get.json.dumps')
    def test_main_success(self, mock_json_dumps, mock_print, mock_parse_args, mock_environ_get, mock_client):
        # Mock the environment variable and command-line arguments
        mock_environ_get.return_value = 'test-project'
        mock_args = argparse.Namespace(secret_id='test-secret')
        mock_parse_args.return_value = mock_args

        # Mock the SecretManagerServiceClient and its methods
        mock_policy = policy_pb2.Policy(version=1, bindings=[], etag=b'test_etag')
        mock_client_instance = mock_client.return_value
        mock_client_instance.get_iam_policy.return_value = mock_policy

        # Mock the get_iam_policy_sample function
        with patch('secret_manager_service_client_iam_policy_get.get_iam_policy_sample') as mock_get_iam_policy_sample:
            mock_get_iam_policy_sample.return_value = mock_policy

            # Call the main function
            secret_manager_service_client_iam_policy_get.main()

            # Assert that the get_iam_policy_sample function was called with the correct resource name
            mock_get_iam_policy_sample.assert_called_once_with('projects/test-project/secrets/test-secret')

            # Assert that json.dumps was called with the correct policy dictionary
            expected_policy_dict = {
                'version': 1,
                'bindings': [],
                'etag': 'test_etag'
            }
            mock_json_dumps.assert_called_once_with(expected_policy_dict, indent=2)

            # Assert that print was called with the JSON string
            mock_print.assert_called_once()


    @patch('secret_manager_service_client_iam_policy_get.os.environ.get')
    @patch('secret_manager_service_client_iam_policy_get.argparse.ArgumentParser.parse_args')
    @patch('secret_manager_service_client_iam_policy_get.print')
    def test_main_no_project_id(self, mock_print, mock_parse_args, mock_environ_get):
        # Mock the environment variable to return None
        mock_environ_get.return_value = None

        # Mock the command-line arguments
        mock_args = argparse.Namespace(secret_id='test-secret')
        mock_parse_args.return_value = mock_args

        # Call the main function and assert that it prints an error message and exits
        with self.assertRaises(SystemExit) as context:
            secret_manager_service_client_iam_policy_get.main()

        self.assertEqual(str(context.exception), '1')
        mock_print.assert_called_once_with('Error: GCP_PROJECT_ID environment variable not set.')


if __name__ == '__main__':
    unittest.main()
