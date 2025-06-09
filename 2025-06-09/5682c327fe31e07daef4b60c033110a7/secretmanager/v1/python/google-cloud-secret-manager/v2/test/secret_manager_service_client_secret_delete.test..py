import os
import unittest
from unittest import mock
from google.api_core import exceptions

# Import the module containing the function to test
import secret_manager_service_client_secret_delete


class TestDeleteSecret(unittest.TestCase):

    @mock.patch('secret_manager_service_client_secret_delete.secretmanager_v1.SecretManagerServiceClient')
    def test_delete_secret_success(self, mock_client):
        # Configure the mock client to return successfully
        mock_instance = mock_client.return_value
        mock_instance.secret_path.return_value = 'projects/test-project/secrets/test-secret'
        mock_instance.delete_secret.return_value = None  # Simulate successful deletion

        # Call the function with test values
        result = secret_manager_service_client_secret_delete.delete_secret_sample(
            'test-project', 'test-secret'
        )

        # Assert that the function returns the success message
        self.assertEqual(result, "Secret 'test-secret' deleted successfully.")

        # Assert that the client's delete_secret method was called with the correct arguments
        mock_instance.delete_secret.assert_called_once()

    @mock.patch('secret_manager_service_client_secret_delete.secretmanager_v1.SecretManagerServiceClient')
    def test_delete_secret_not_found(self, mock_client):
        # Configure the mock client to raise a NotFound exception
        mock_instance = mock_client.return_value
        mock_instance.secret_path.return_value = 'projects/test-project/secrets/test-secret'
        mock_instance.delete_secret.side_effect = exceptions.NotFound('Secret not found')

        # Call the function with test values
        result = secret_manager_service_client_secret_delete.delete_secret_sample(
            'test-project', 'test-secret'
        )

        # Assert that the function returns the not found message
        self.assertEqual(result, "Secret 'test-secret' not found.")

        # Assert that the client's delete_secret method was called
        mock_instance.delete_secret.assert_called_once()

    @mock.patch('secret_manager_service_client_secret_delete.secretmanager_v1.SecretManagerServiceClient')
    def test_delete_secret_failed_precondition(self, mock_client):
        # Configure the mock client to raise a FailedPrecondition exception
        mock_instance = mock_client.return_value
        mock_instance.secret_path.return_value = 'projects/test-project/secrets/test-secret'
        mock_instance.delete_secret.side_effect = exceptions.FailedPrecondition('Failed precondition')

        # Call the function with test values
        result = secret_manager_service_client_secret_delete.delete_secret_sample(
            'test-project', 'test-secret'
        )

        # Assert that the function returns the failed precondition message
        self.assertTrue(result.startswith("Failed to delete secret 'test-secret'"))

        # Assert that the client's delete_secret method was called
        mock_instance.delete_secret.assert_called_once()

    @mock.patch('secret_manager_service_client_secret_delete.secretmanager_v1.SecretManagerServiceClient')
    def test_delete_secret_unexpected_error(self, mock_client):
        # Configure the mock client to raise an unexpected exception
        mock_instance = mock_client.return_value
        mock_instance.secret_path.return_value = 'projects/test-project/secrets/test-secret'
        mock_instance.delete_secret.side_effect = Exception('Unexpected error')

        # Call the function with test values
        result = secret_manager_service_client_secret_delete.delete_secret_sample(
            'test-project', 'test-secret'
        )

        # Assert that the function returns the unexpected error message
        self.assertTrue(result.startswith("An unexpected error occurred"))

        # Assert that the client's delete_secret method was called
        mock_instance.delete_secret.assert_called_once()


if __name__ == '__main__':
    unittest.main()
