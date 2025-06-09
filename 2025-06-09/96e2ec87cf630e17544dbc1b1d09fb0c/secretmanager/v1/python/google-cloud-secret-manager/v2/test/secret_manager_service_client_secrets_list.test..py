import os
import json
import unittest
from unittest.mock import MagicMock, patch

from google.api_core import exceptions

# Import the code to be tested
import secret_manager_service_client_secrets_list


class TestListSecretsSample(unittest.TestCase):

    @patch('secret_manager_service_client_secrets_list.secretmanager_v1.SecretManagerServiceClient')
    def test_list_secrets_success(self, mock_client):
        # Mock the SecretManagerServiceClient and its methods
        mock_secret = MagicMock()
        mock_secret.name = 'projects/test-project/secrets/test-secret'
        mock_secret.create_time = MagicMock()
        mock_secret.create_time.isoformat.return_value = '2023-10-26T00:00:00Z'
        mock_secret.labels = {'label1': 'value1', 'label2': 'value2'}
        mock_secret.replication.automatic = True
        mock_secret.replication.user_managed = None

        mock_list_secrets = MagicMock(return_value=[mock_secret])
        mock_client.return_value.list_secrets = mock_list_secrets

        # Call the function
        with patch('sys.stdout') as mock_stdout:
            secret_manager_service_client_secrets_list.list_secrets_sample('test-project')

        # Assert that the client was called with the correct parent
        mock_list_secrets.assert_called_once_with(request={"parent": 'projects/test-project'})

        # Assert that the output contains the secret name
        expected_output = '[{
  "name": "projects/test-project/secrets/test-secret",
  "create_time": "2023-10-26T00:00:00Z",
  "labels": {
    "label1": "value1",
    "label2": "value2"
  },
  "replication": {
    "automatic": true
  }
}]'
        self.assertEqual(mock_stdout.write.call_args[0][0].strip(), expected_output.strip())

        # Assert that the client was closed
        mock_client.return_value.close.assert_called_once()

    @patch('secret_manager_service_client_secrets_list.secretmanager_v1.SecretManagerServiceClient')
    def test_list_secrets_user_managed_replication(self, mock_client):
        # Mock the SecretManagerServiceClient and its methods
        mock_secret = MagicMock()
        mock_secret.name = 'projects/test-project/secrets/test-secret'
        mock_secret.create_time = MagicMock()
        mock_secret.create_time.isoformat.return_value = '2023-10-26T00:00:00Z'
        mock_secret.labels = {'label1': 'value1', 'label2': 'value2'}
        mock_secret.replication.automatic = False
        mock_secret.replication.user_managed = MagicMock()
        mock_replica = MagicMock()
        mock_replica.location = 'us-central1'
        mock_replica.customer_managed_encryption = MagicMock()
        mock_replica.customer_managed_encryption.kms_key_name = 'kms-key'
        mock_secret.replication.user_managed.replicas = [mock_replica]

        mock_list_secrets = MagicMock(return_value=[mock_secret])
        mock_client.return_value.list_secrets = mock_list_secrets

        # Call the function
        with patch('sys.stdout') as mock_stdout:
            secret_manager_service_client_secrets_list.list_secrets_sample('test-project')

        # Assert that the client was called with the correct parent
        mock_list_secrets.assert_called_once_with(request={"parent": 'projects/test-project'})

        # Assert that the output contains the secret name
        expected_output_contains = '"user_managed": [{
    "replica": {
      "location": "us-central1",
      "customer_managed_encryption": {
        "kms_key_name": "kms-key"
      }
    }
  }]'
        self.assertTrue(expected_output_contains in mock_stdout.write.call_args[0][0])

        # Assert that the client was closed
        mock_client.return_value.close.assert_called_once()


    @patch('secret_manager_service_client_secrets_list.secretmanager_v1.SecretManagerServiceClient')
    def test_list_secrets_failure(self, mock_client):
        # Mock the SecretManagerServiceClient to raise an exception
        mock_client.return_value.list_secrets.side_effect = exceptions.PermissionDenied('Permission denied')

        # Call the function and assert that it raises the exception
        with self.assertRaises(exceptions.PermissionDenied):
            secret_manager_service_client_secrets_list.list_secrets_sample('test-project')

        # Assert that the client was closed
        mock_client.return_value.close.assert_called_once()


    @patch('secret_manager_service_client_secrets_list.secretmanager_v1.SecretManagerServiceClient')
    def test_list_secrets_no_secrets(self, mock_client):
        # Mock the SecretManagerServiceClient to return an empty list of secrets
        mock_list_secrets = MagicMock(return_value=[])
        mock_client.return_value.list_secrets = mock_list_secrets

        # Call the function
        with patch('sys.stdout') as mock_stdout:
            secret_manager_service_client_secrets_list.list_secrets_sample('test-project')

        # Assert that the client was called with the correct parent
        mock_list_secrets.assert_called_once_with(request={"parent": 'projects/test-project'})

        # Assert that the output is an empty list
        self.assertEqual(mock_stdout.write.call_args[0][0].strip(), '[]')

        # Assert that the client was closed
        mock_client.return_value.close.assert_called_once()


if __name__ == '__main__':
    unittest.main()
