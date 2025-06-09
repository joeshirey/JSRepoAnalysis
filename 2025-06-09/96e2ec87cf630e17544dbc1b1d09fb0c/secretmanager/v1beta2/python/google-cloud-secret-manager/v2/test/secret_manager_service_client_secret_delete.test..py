import os
import unittest
from unittest import mock
from google.api_core import exceptions

# Assuming the code under test is in 'secret_manager_service_client_secret_delete.py'
import secret_manager_service_client_secret_delete as secret_delete


class TestDeleteSecret(unittest.TestCase):

    @mock.patch('secret_manager_service_client_secret_delete.secretmanager_v1beta2.SecretManagerServiceClient')
    def test_delete_secret_success(self, mock_client):
        # Configure the mock client to simulate a successful deletion.
        mock_instance = mock_client.return_value
        mock_instance.delete_secret.return_value = None  # delete_secret returns None on success

        project_id = 'test-project'
        secret_id = 'test-secret'

        # Call the function under test.
        deleted = secret_delete.delete_secret_sample(project_id, secret_id)

        # Assert that the client's delete_secret method was called with the correct name.
        mock_instance.delete_secret.assert_called_once()
        args, kwargs = mock_instance.delete_secret.call_args
        self.assertEqual(kwargs['name'], f'projects/{project_id}/secrets/{secret_id}')

        # Assert that the function returns True on success.
        self.assertTrue(deleted)

    @mock.patch('secret_manager_service_client_secret_delete.secretmanager_v1beta2.SecretManagerServiceClient')
    def test_delete_secret_not_found(self, mock_client):
        # Configure the mock client to simulate a NotFound error.
        mock_instance = mock_client.return_value
        mock_instance.delete_secret.side_effect = exceptions.NotFound('Secret not found')

        project_id = 'test-project'
        secret_id = 'test-secret'

        # Call the function under test.
        deleted = secret_delete.delete_secret_sample(project_id, secret_id)

        # Assert that the client's delete_secret method was called with the correct name.
        mock_instance.delete_secret.assert_called_once()
        args, kwargs = mock_instance.delete_secret.call_args
        self.assertEqual(kwargs['name'], f'projects/{project_id}/secrets/{secret_id}')

        # Assert that the function returns False when the secret is not found.
        self.assertFalse(deleted)

    @mock.patch('secret_manager_service_client_secret_delete.secretmanager_v1beta2.SecretManagerServiceClient')
    def test_delete_secret_other_error(self, mock_client):
        # Configure the mock client to simulate a different API error.
        mock_instance = mock_client.return_value
        mock_instance.delete_secret.side_effect = exceptions.PermissionDenied('Permission denied')

        project_id = 'test-project'
        secret_id = 'test-secret'

        # Call the function under test and assert that it raises the exception.
        with self.assertRaises(exceptions.PermissionDenied):
            secret_delete.delete_secret_sample(project_id, secret_id)

        # Assert that the client's delete_secret method was called with the correct name.
        mock_instance.delete_secret.assert_called_once()
        args, kwargs = mock_instance.delete_secret.call_args
        self.assertEqual(kwargs['name'], f'projects/{project_id}/secrets/{secret_id}')

    @mock.patch('secret_manager_service_client_secret_delete.secretmanager_v1beta2.SecretManagerServiceClient')
    def test_delete_secret_does_not_crash_with_valid_arguments(self, mock_client):
        mock_instance = mock_client.return_value
        mock_instance.delete_secret.return_value = None

        project_id = 'test-project'
        secret_id = 'test-secret'

        try:
            secret_delete.delete_secret_sample(project_id, secret_id)
        except Exception as e:
            self.fail(f"delete_secret_sample raised Exception unexpectedly: {e}")


if __name__ == '__main__':
    unittest.main()
