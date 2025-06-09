import os
import unittest
from unittest import mock
import json
from io import StringIO
import sys

# Import the module containing the function to test.
# Assuming the file is named 'secret_manager_service_client_secret_delete.py'
import secret_manager_service_client_secret_delete


class TestDeleteSecret(unittest.TestCase):

    @mock.patch('google.cloud.secretmanager_v1.SecretManagerServiceClient')
    def test_delete_secret_success(self, mock_client):
        # Configure the mock client to return None (success) when delete_secret is called.
        mock_client_instance = mock_client.return_value
        mock_client_instance.delete_secret.return_value = None

        project_id = "test-project"
        secret_id = "test-secret"

        # Call the function.
        secret_manager_service_client_secret_delete.delete_secret_sample(project_id, secret_id)

        # Assert that the delete_secret method was called with the correct arguments.
        mock_client_instance.delete_secret.assert_called_once()
        args, kwargs = mock_client_instance.delete_secret.call_args
        self.assertEqual(kwargs['request']['name'], f"projects/{project_id}/secrets/{secret_id}")

    @mock.patch('google.cloud.secretmanager_v1.SecretManagerServiceClient')
    def test_delete_secret_not_found(self, mock_client):
        # Configure the mock client to raise a NotFound exception.
        mock_client_instance = mock_client.return_value
        mock_client_instance.delete_secret.side_effect = Exception("NotFound")

        project_id = "test-project"
        secret_id = "test-secret"

        # Call the function and assert that it raises a ValueError.
        with self.assertRaises(RuntimeError) as context:
            secret_manager_service_client_secret_delete.delete_secret_sample(project_id, secret_id)

        self.assertTrue(f"Failed to delete secret '{secret_id}'" in str(context.exception))

    @mock.patch('google.cloud.secretmanager_v1.SecretManagerServiceClient')
    def test_delete_secret_other_error(self, mock_client):
        # Configure the mock client to raise a generic exception.
        mock_client_instance = mock_client.return_value
        mock_client_instance.delete_secret.side_effect = Exception("Some other error")

        project_id = "test-project"
        secret_id = "test-secret"

        # Call the function and assert that it raises a RuntimeError.
        with self.assertRaises(RuntimeError) as context:
            secret_manager_service_client_secret_delete.delete_secret_sample(project_id, secret_id)

        self.assertTrue(f"Failed to delete secret '{secret_id}'" in str(context.exception))

    @mock.patch('argparse.ArgumentParser.parse_args', return_value=mock.Mock(project_id='test-project', secret_id='test-secret'))
    @mock.patch('secret_manager_service_client_secret_delete.delete_secret_sample')
    def test_main_success(self, mock_delete_secret_sample, mock_parse_args):
        # Mock the delete_secret_sample function to prevent actual deletion
        mock_delete_secret_sample.return_value = None

        # Capture stdout
        captured_output = StringIO()
        sys.stdout = captured_output

        # Call main
        secret_manager_service_client_secret_delete.main()

        # Restore stdout
        sys.stdout = sys.__stdout__

        # Assert the output
        expected_output = json.dumps({"status": "success", "secret_id": "test-secret", "message": "Secret 'test-secret' deleted successfully."})
        self.assertEqual(captured_output.getvalue().strip(), expected_output)

    @mock.patch('argparse.ArgumentParser.parse_args', return_value=mock.Mock(project_id='test-project', secret_id='test-secret'))
    @mock.patch('secret_manager_service_client_secret_delete.delete_secret_sample')
    def test_main_value_error(self, mock_delete_secret_sample, mock_parse_args):
        # Mock the delete_secret_sample function to raise a ValueError
        mock_delete_secret_sample.side_effect = ValueError("Test Value Error")

        # Capture stdout
        captured_output = StringIO()
        sys.stdout = captured_output

        # Call main
        secret_manager_service_client_secret_delete.main()

        # Restore stdout
        sys.stdout = sys.__stdout__

        # Assert the output
        expected_output = json.dumps({"status": "error", "secret_id": "test-secret", "message": "Test Value Error"})
        self.assertEqual(captured_output.getvalue().strip(), expected_output)

    @mock.patch('argparse.ArgumentParser.parse_args', return_value=mock.Mock(project_id='test-project', secret_id='test-secret'))
    @mock.patch('secret_manager_service_client_secret_delete.delete_secret_sample')
    def test_main_runtime_error(self, mock_delete_secret_sample, mock_parse_args):
        # Mock the delete_secret_sample function to raise a RuntimeError
        mock_delete_secret_sample.side_effect = RuntimeError("Test Runtime Error")

        # Capture stdout
        captured_output = StringIO()
        sys.stdout = captured_output

        # Call main
        secret_manager_service_client_secret_delete.main()

        # Restore stdout
        sys.stdout = sys.__stdout__

        # Assert the output
        expected_output = json.dumps({"status": "error", "secret_id": "test-secret", "message": "Test Runtime Error"})
        self.assertEqual(captured_output.getvalue().strip(), expected_output)

    @mock.patch('argparse.ArgumentParser.parse_args', return_value=mock.Mock(project_id='test-project', secret_id='test-secret'))
    @mock.patch('secret_manager_service_client_secret_delete.delete_secret_sample')
    def test_main_exception(self, mock_delete_secret_sample, mock_parse_args):
        # Mock the delete_secret_sample function to raise a generic Exception
        mock_delete_secret_sample.side_effect = Exception("Test Exception")

        # Capture stdout
        captured_output = StringIO()
        sys.stdout = captured_output

        # Call main
        secret_manager_service_client_secret_delete.main()

        # Restore stdout
        sys.stdout = sys.__stdout__

        # Assert the output
        expected_output = json.dumps({"status": "error", "secret_id": "test-secret", "message": "An unexpected error occurred: Test Exception"})
        self.assertEqual(captured_output.getvalue().strip(), expected_output)

    @mock.patch('argparse.ArgumentParser.parse_args', return_value=mock.Mock(project_id=None, secret_id='test-secret'))
    def test_main_no_project_id(self, mock_parse_args):
        # Capture stdout
        captured_output = StringIO()
        sys.stdout = captured_output

        # Call main
        with self.assertRaises(SystemExit) as cm:
            secret_manager_service_client_secret_delete.main()

        self.assertEqual(cm.exception.code, 1)

        # Restore stdout
        sys.stdout = sys.__stdout__
        expected_output = json.dumps({"status": "error", "message": "Error: --project_id or GCP_PROJECT_ID environment variable must be set."})
        self.assertEqual(captured_output.getvalue().strip(), expected_output)


if __name__ == '__main__':
    unittest.main()
