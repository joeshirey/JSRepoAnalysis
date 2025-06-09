import unittest
import os
from unittest.mock import patch, MagicMock
from google.api_core import exceptions

# Import the code to be tested
import secret_manager_service_client_secret_delete


class TestDeleteSecretSample(unittest.TestCase):

    @patch('secret_manager_service_client_secret_delete.secretmanager_v1beta2.SecretManagerServiceClient')
    def test_delete_secret_success(self, mock_client):
        # Configure the mock client
        mock_instance = mock_client.return_value
        mock_instance.delete_secret.return_value = None  # Simulate successful deletion

        project_id = 'test-project'
        secret_id = 'test-secret'

        # Call the function
        result = secret_manager_service_client_secret_delete.delete_secret_sample(project_id, secret_id)

        # Assertions
        self.assertEqual(result['status'], 'success')
        self.assertIn(secret_id, result['message'])
        mock_instance.delete_secret.assert_called_once()

    @patch('secret_manager_service_client_secret_delete.secretmanager_v1beta2.SecretManagerServiceClient')
    def test_delete_secret_not_found(self, mock_client):
        # Configure the mock client to raise a NotFound exception
        mock_instance = mock_client.return_value
        mock_instance.delete_secret.side_effect = exceptions.NotFound('Secret not found')

        project_id = 'test-project'
        secret_id = 'test-secret'

        # Call the function
        result = secret_manager_service_client_secret_delete.delete_secret_sample(project_id, secret_id)

        # Assertions
        self.assertEqual(result['status'], 'error')
        self.assertIn(secret_id, result['message'])
        self.assertIn(project_id, result['message'])
        mock_instance.delete_secret.assert_called_once()

    @patch('secret_manager_service_client_secret_delete.secretmanager_v1beta2.SecretManagerServiceClient')
    def test_delete_secret_api_error(self, mock_client):
        # Configure the mock client to raise a GoogleAPIError exception
        mock_instance = mock_client.return_value
        mock_instance.delete_secret.side_effect = exceptions.GoogleAPICallError('API error')

        project_id = 'test-project'
        secret_id = 'test-secret'

        # Call the function
        result = secret_manager_service_client_secret_delete.delete_secret_sample(project_id, secret_id)

        # Assertions
        self.assertEqual(result['status'], 'error')
        self.assertIn('API error', result['message'])
        mock_instance.delete_secret.assert_called_once()

    @patch('secret_manager_service_client_secret_delete.secretmanager_v1beta2.SecretManagerServiceClient')
    def test_delete_secret_unexpected_error(self, mock_client):
        # Configure the mock client to raise an unexpected exception
        mock_instance = mock_client.return_value
        mock_instance.delete_secret.side_effect = Exception('Unexpected error')

        project_id = 'test-project'
        secret_id = 'test-secret'

        # Call the function
        result = secret_manager_service_client_secret_delete.delete_secret_sample(project_id, secret_id)

        # Assertions
        self.assertEqual(result['status'], 'error')
        self.assertIn('Unexpected error', result['message'])
        mock_instance.delete_secret.assert_called_once()


if __name__ == '__main__':
    unittest.main()
