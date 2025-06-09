import os
import unittest
from unittest import mock
from google.api_core import exceptions
from google.cloud import secretmanager_v1
from google.protobuf import empty_pb2
import io
import sys

# Replace 'your_module' with the actual name of your module
import secret_manager_service_client_secret_delete as target


class TestDeleteSecretSample(unittest.TestCase):

    @mock.patch('secret_manager_service_client_secret_delete.secretmanager_v1.SecretManagerServiceClient')
    def test_delete_secret_success(self, mock_client):
        # Configure the mock client
        mock_instance = mock_client.return_value
        mock_instance.delete_secret.return_value = empty_pb2.Empty()
        project_id = 'test-project'
        secret_id = 'test-secret'

        # Call the function
        result = target.delete_secret_sample(project_id, secret_id)

        # Assert that the client was called with the correct parameters
        mock_instance.delete_secret.assert_called_once()

        # Assert that the function returns the expected result
        self.assertIsInstance(result, empty_pb2.Empty)

    @mock.patch('secret_manager_service_client_secret_delete.secretmanager_v1.SecretManagerServiceClient')
    def test_delete_secret_not_found(self, mock_client):
        # Configure the mock client to raise a NotFound exception
        mock_instance = mock_client.return_value
        mock_instance.delete_secret.side_effect = exceptions.NotFound('Secret not found')
        project_id = 'test-project'
        secret_id = 'test-secret'

        # Call the function
        result = target.delete_secret_sample(project_id, secret_id)

        # Assert that the client was called with the correct parameters
        mock_instance.delete_secret.assert_called_once()

        # Assert that the function returns None
        self.assertIsNone(result)

    @mock.patch('secret_manager_service_client_secret_delete.secretmanager_v1.SecretManagerServiceClient')
    def test_delete_secret_api_error(self, mock_client):
        # Configure the mock client to raise a GoogleAPICallError exception
        mock_instance = mock_client.return_value
        mock_instance.delete_secret.side_effect = exceptions.InternalServerError('API error')
        project_id = 'test-project'
        secret_id = 'test-secret'

        # Call the function and assert that it raises the exception
        with self.assertRaises(exceptions.InternalServerError):
            target.delete_secret_sample(project_id, secret_id)

    @mock.patch('secret_manager_service_client_secret_delete.secretmanager_v1.SecretManagerServiceClient')
    def test_main_success(self, mock_client):
        mock_instance = mock_client.return_value
        mock_instance.delete_secret.return_value = empty_pb2.Empty()
        project_id = 'test-project'
        secret_id = 'test-secret'
        # Mock command line arguments
        with mock.patch('sys.argv', ['script_name', '--project_id', project_id, '--secret_id', secret_id]):
            # Capture stdout
            with mock.patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
                # Call the main function
                target.main()
                # Assert the output
                self.assertIn(f"Secret '{secret_id}' in project '{project_id}' deleted successfully.", mock_stdout.getvalue())

    @mock.patch('secret_manager_service_client_secret_delete.secretmanager_v1.SecretManagerServiceClient')
    def test_main_secret_not_found(self, mock_client):
        mock_instance = mock_client.return_value
        mock_instance.delete_secret.side_effect = exceptions.NotFound('Secret not found')
        project_id = 'test-project'
        secret_id = 'test-secret'
        # Mock command line arguments
        with mock.patch('sys.argv', ['script_name', '--project_id', project_id, '--secret_id', secret_id]):
            # Capture stdout
            with mock.patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
                # Call the main function
                target.main()
                # Assert the output
                self.assertIn(f"Secret '{secret_id}' not found in project '{project_id}'.", mock_stdout.getvalue())

    @mock.patch('secret_manager_service_client_secret_delete.secretmanager_v1.SecretManagerServiceClient')
    def test_main_api_error(self, mock_client):
        mock_instance = mock_client.return_value
        mock_instance.delete_secret.side_effect = exceptions.InternalServerError('API error')
        project_id = 'test-project'
        secret_id = 'test-secret'
        # Mock command line arguments
        with mock.patch('sys.argv', ['script_name', '--project_id', project_id, '--secret_id', secret_id]):
            # Capture stderr
            with mock.patch('sys.stderr', new_callable=io.StringIO) as mock_stderr:
                # Call the main function
                with self.assertRaises(SystemExit) as cm:
                    target.main()
                self.assertEqual(cm.exception.code, 1)
                # Assert the output
                self.assertIn("Error deleting secret:", mock_stderr.getvalue())


if __name__ == '__main__':
    unittest.main()
