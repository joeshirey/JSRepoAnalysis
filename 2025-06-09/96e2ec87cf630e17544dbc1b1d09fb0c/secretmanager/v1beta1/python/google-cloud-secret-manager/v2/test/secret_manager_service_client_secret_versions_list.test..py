import os
import unittest
from unittest.mock import MagicMock, patch
import json

# Assuming the code under test is in 'secret_manager_service_client_secret_versions_list.py'
import secret_manager_service_client_secret_versions_list as secret_versions
from google.cloud import secretmanager_v1beta1


class TestListSecretVersions(unittest.TestCase):

    @patch('secret_manager_service_client_secret_versions_list.secretmanager_v1beta1.SecretManagerServiceClient')
    def test_list_secret_versions_success(self, mock_client):
        # Mock the SecretManagerServiceClient and its methods
        mock_secret_versions = [
            MagicMock(name='version1', state=MagicMock(name='ENABLED'), create_time=MagicMock(isoformat=lambda: '2023-01-01T00:00:00'), destroy_time=None),
            MagicMock(name='version2', state=MagicMock(name='DISABLED'), create_time=MagicMock(isoformat=lambda: '2023-01-02T00:00:00'), destroy_time=MagicMock(isoformat=lambda: '2024-01-01T00:00:00'))
        ]

        mock_list_secret_versions = MagicMock(return_value=mock_secret_versions)
        mock_client.return_value.list_secret_versions = mock_list_secret_versions

        # Set environment variables and arguments
        project_id = 'test-project'
        secret_id = 'test-secret'

        # Call the function
        result = secret_versions.list_secret_versions_sample(project_id, secret_id)

        # Assert that the client was called with the correct parameters
        mock_client.return_value.list_secret_versions.assert_called_once_with(request={'parent': f'projects/{project_id}/secrets/{secret_id}'})

        # Assert that the result is as expected
        expected_result = [
            {
                'name': 'version1',
                'state': 'ENABLED',
                'create_time': '2023-01-01T00:00:00',
                'destroy_time': None
            },
            {
                'name': 'version2',
                'state': 'DISABLED',
                'create_time': '2023-01-02T00:00:00',
                'destroy_time': '2024-01-01T00:00:00'
            }
        ]
        self.assertEqual(result, expected_result)

    @patch('secret_manager_service_client_secret_versions_list.secretmanager_v1beta1.SecretManagerServiceClient')
    def test_list_secret_versions_exception(self, mock_client):
        # Mock the SecretManagerServiceClient to raise an exception
        mock_client.return_value.list_secret_versions.side_effect = Exception('API error')

        # Set environment variables and arguments
        project_id = 'test-project'
        secret_id = 'test-secret'

        # Call the function and assert that it raises the exception
        with self.assertRaises(Exception) as context:
            secret_versions.list_secret_versions_sample(project_id, secret_id)

        self.assertEqual(str(context.exception), 'API error')


if __name__ == '__main__':
    unittest.main()
