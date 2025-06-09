import os
import unittest
from unittest import mock
from google.api_core import exceptions

# Import the module containing the function to be tested
import secret_manager_service_client_secret_delete


class TestDeleteSecretSample(unittest.TestCase):

    @mock.patch('secret_manager_service_client_secret_delete.secretmanager_v1beta1.SecretManagerServiceClient')
    def test_delete_secret_success(self, mock_client):
        # Configure the mock client to return None (success) when delete_secret is called
        mock_instance = mock_client.return_value
        mock_instance.delete_secret.return_value = None

        project_id = 'test-project'
        secret_id = 'test-secret'

        # Call the function
        secret_manager_service_client_secret_delete.delete_secret_sample(project_id, secret_id)

        # Assert that the client's delete_secret method was called with the correct arguments
        mock_instance.delete_secret.assert_called_once_with(name=f'projects/{project_id}/secrets/{secret_id}')

    @mock.patch('secret_manager_service_client_secret_delete.secretmanager_v1beta1.SecretManagerServiceClient')
    def test_delete_secret_not_found(self, mock_client):
        # Configure the mock client to raise a NotFound exception
        mock_instance = mock_client.return_value
        mock_instance.delete_secret.side_effect = exceptions.NotFound('Secret not found')

        project_id = 'test-project'
        secret_id = 'test-secret'

        # Call the function and assert that it raises a NotFound exception
        with self.assertRaises(exceptions.NotFound) as context:
            secret_manager_service_client_secret_delete.delete_secret_sample(project_id, secret_id)

        self.assertEqual(str(context.exception), f'Secret projects/{project_id}/secrets/{secret_id} not found.')

        # Assert that the client's delete_secret method was called with the correct arguments
        mock_instance.delete_secret.assert_called_once_with(name=f'projects/{project_id}/secrets/{secret_id}')

    @mock.patch('secret_manager_service_client_secret_delete.secretmanager_v1beta1.SecretManagerServiceClient')
    def test_delete_secret_failed_precondition(self, mock_client):
        # Configure the mock client to raise a FailedPrecondition exception
        mock_instance = mock_client.return_value
        mock_instance.delete_secret.side_effect = exceptions.FailedPrecondition('Failed precondition')

        project_id = 'test-project'
        secret_id = 'test-secret'

        # Call the function and assert that it raises a FailedPrecondition exception
        with self.assertRaises(exceptions.FailedPrecondition) as context:
            secret_manager_service_client_secret_delete.delete_secret_sample(project_id, secret_id)

        self.assertTrue(str(context.exception).startswith(f'Secret projects/{project_id}/secrets/{secret_id} could not be deleted'))
        # Assert that the client's delete_secret method was called with the correct arguments
        mock_instance.delete_secret.assert_called_once_with(name=f'projects/{project_id}/secrets/{secret_id}')

    @mock.patch('secret_manager_service_client_secret_delete.secretmanager_v1beta1.SecretManagerServiceClient')
    def test_delete_secret_unexpected_error(self, mock_client):
        # Configure the mock client to raise an unexpected exception
        mock_instance = mock_client.return_value
        mock_instance.delete_secret.side_effect = Exception('Unexpected error')

        project_id = 'test-project'
        secret_id = 'test-secret'

        # Call the function and assert that it raises the exception
        with self.assertRaises(Exception) as context:
            secret_manager_service_client_secret_delete.delete_secret_sample(project_id, secret_id)

        self.assertTrue(str(context.exception).startswith(f'An unexpected error occurred while deleting secret projects/{project_id}/secrets/{secret_id}'))

        # Assert that the client's delete_secret method was called with the correct arguments
        mock_instance.delete_secret.assert_called_once_with(name=f'projects/{project_id}/secrets/{secret_id}')


if __name__ == '__main__':
    unittest.main()
