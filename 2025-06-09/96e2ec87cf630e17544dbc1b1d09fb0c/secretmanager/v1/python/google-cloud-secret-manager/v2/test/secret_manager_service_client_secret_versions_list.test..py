import os
import unittest
from unittest.mock import MagicMock, patch
import json

# Assuming the code under test is in a file named 'secret_manager_service_client_secret_versions_list.py'
from secret_manager_service_client_secret_versions_list import list_secret_versions_sample


class TestSecretManager(unittest.TestCase):

    @patch('secret_manager_service_client_secret_versions_list.secretmanager_v1.SecretManagerServiceClient')
    def test_list_secret_versions_success(self, mock_client):
        # Mock the SecretManagerServiceClient and its methods.
        mock_secret_manager_client = mock_client.return_value
        mock_list_secret_versions = mock_secret_manager_client.list_secret_versions

        # Create a mock response that simulates the iterator.
        mock_version1 = MagicMock(name='mock_version1')
        mock_version1.name = 'projects/test-project/secrets/test-secret/versions/1'
        mock_version1.state = 1  # Enabled state
        mock_version1.create_time = MagicMock()
        mock_version1.create_time.isoformat.return_value = '2023-10-26T10:00:00Z'
        mock_version1.destroy_time = None

        mock_version2 = MagicMock(name='mock_version2')
        mock_version2.name = 'projects/test-project/secrets/test-secret/versions/2'
        mock_version2.state = 2  # Disabled state
        mock_version2.create_time = MagicMock()
        mock_version2.create_time.isoformat.return_value = '2023-10-27T10:00:00Z'
        mock_version2.destroy_time = MagicMock()
        mock_version2.destroy_time.isoformat.return_value = '2023-10-28T10:00:00Z'

        mock_list_secret_versions.return_value = [mock_version1, mock_version2]

        # Call the function under test.
        project_id = 'test-project'
        secret_id = 'test-secret'
        versions = list_secret_versions_sample(project_id, secret_id)

        # Assert that the client was called with the correct parameters.
        mock_client.return_value.secret_path.assert_called_once_with(project_id, secret_id)

        # Assert that the response is correctly parsed.
        self.assertEqual(len(versions), 2)
        self.assertEqual(versions[0]['name'], 'projects/test-project/secrets/test-secret/versions/1')
        self.assertEqual(versions[0]['state'], 'ENABLED')
        self.assertEqual(versions[0]['create_time'], '2023-10-26T10:00:00Z')
        self.assertIsNone(versions[0]['destroy_time'])

        self.assertEqual(versions[1]['name'], 'projects/test-project/secrets/test-secret/versions/2')
        self.assertEqual(versions[1]['state'], 'DISABLED')
        self.assertEqual(versions[1]['create_time'], '2023-10-27T10:00:00Z')
        self.assertEqual(versions[1]['destroy_time'], '2023-10-28T10:00:00Z')

    @patch('secret_manager_service_client_secret_versions_list.secretmanager_v1.SecretManagerServiceClient')
    def test_list_secret_versions_exception(self, mock_client):
        # Mock the SecretManagerServiceClient to raise an exception.
        mock_secret_manager_client = mock_client.return_value
        mock_list_secret_versions = mock_secret_manager_client.list_secret_versions
        mock_list_secret_versions.side_effect = Exception('API error')

        # Call the function under test and assert that it raises an exception.
        project_id = 'test-project'
        secret_id = 'test-secret'

        with self.assertRaises(Exception) as context:
            list_secret_versions_sample(project_id, secret_id)

        self.assertEqual(str(context.exception), 'API error')


if __name__ == '__main__':
    unittest.main()
