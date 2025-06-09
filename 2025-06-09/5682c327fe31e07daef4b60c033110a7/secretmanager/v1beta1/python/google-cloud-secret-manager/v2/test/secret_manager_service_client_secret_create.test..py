import os
import json
import unittest
from unittest.mock import patch, mock_open
from google.api_core.exceptions import GoogleAPICallError
from google.cloud import secretmanager_v1beta1

# Assuming the code under test is in 'secret_manager_service_client_secret_create.py'
import secret_manager_service_client_secret_create


class TestCreateSecretSample(unittest.TestCase):

    @patch('secret_manager_service_client_secret_create.secretmanager_v1beta1.SecretManagerServiceClient')
    def test_create_secret_success(self, mock_client):
        # Mock the SecretManagerServiceClient and its create_secret method
        mock_secret = secretmanager_v1beta1.types.Secret(name='test-secret')
        mock_client.return_value.create_secret.return_value = mock_secret

        project_id = 'test-project'
        secret_id = 'test-secret-id'

        # Call the function
        created_secret = secret_manager_service_client_secret_create.create_secret_sample(
            project_id=project_id, secret_id=secret_id
        )

        # Assert that the client's create_secret method was called with the correct arguments
        mock_client.return_value.create_secret.assert_called_once()
        args, kwargs = mock_client.return_value.create_secret.call_args
        request = kwargs['request']
        self.assertEqual(request.parent, f'projects/{project_id}')
        self.assertEqual(request.secret_id, secret_id)
        self.assertIsInstance(request.secret, secretmanager_v1beta1.types.Secret)

        # Assert that the function returns the mock secret
        self.assertEqual(created_secret, mock_secret)

    @patch('secret_manager_service_client_secret_create.secretmanager_v1beta1.SecretManagerServiceClient')
    def test_create_secret_with_labels(self, mock_client):
        # Mock the SecretManagerServiceClient and its create_secret method
        mock_secret = secretmanager_v1beta1.types.Secret(name='test-secret')
        mock_client.return_value.create_secret.return_value = mock_secret

        project_id = 'test-project'
        secret_id = 'test-secret-id'
        labels_file_path = 'test_labels.json'
        labels = {"environment": "dev", "owner": "team-a"}

        # Create a mock labels file
        with patch('builtins.open', mock_open(read_data=json.dumps(labels))) as mock_file:
            # Call the function
            created_secret = secret_manager_service_client_secret_create.create_secret_sample(
                project_id=project_id, secret_id=secret_id, labels_file_path=labels_file_path
            )

        # Assert that the client's create_secret method was called with the correct arguments
        mock_client.return_value.create_secret.assert_called_once()
        args, kwargs = mock_client.return_value.create_secret.call_args
        request = kwargs['request']
        self.assertEqual(request.parent, f'projects/{project_id}')
        self.assertEqual(request.secret_id, secret_id)
        self.assertIsInstance(request.secret, secretmanager_v1beta1.types.Secret)
        self.assertEqual(request.secret.labels, labels)

        # Assert that the function returns the mock secret
        self.assertEqual(created_secret, mock_secret)

    @patch('secret_manager_service_client_secret_create.secretmanager_v1beta1.SecretManagerServiceClient')
    def test_create_secret_api_error(self, mock_client):
        # Mock the SecretManagerServiceClient to raise an exception
        mock_client.return_value.create_secret.side_effect = GoogleAPICallError('API error')

        project_id = 'test-project'
        secret_id = 'test-secret-id'

        # Call the function and assert that it raises the same exception
        with self.assertRaises(GoogleAPICallError):
            secret_manager_service_client_secret_create.create_secret_sample(
                project_id=project_id, secret_id=secret_id
            )

    def test_create_secret_invalid_labels_file(self):
        project_id = 'test-project'
        secret_id = 'test-secret-id'
        labels_file_path = 'invalid_labels.json'

        # Test case 1: Invalid JSON
        with patch('builtins.open', mock_open(read_data='invalid json')) as mock_file,
                self.assertRaises(json.JSONDecodeError):
            secret_manager_service_client_secret_create.create_secret_sample(
                project_id=project_id, secret_id=secret_id, labels_file_path=labels_file_path
            )

        # Test case 2: Labels are not a dictionary
        with patch('builtins.open', mock_open(read_data='["not", "a", "dict"]')) as mock_file,
                self.assertRaises(ValueError):
            secret_manager_service_client_secret_create.create_secret_sample(
                project_id=project_id, secret_id=secret_id, labels_file_path=labels_file_path
            )

        # Test case 3: Labels have non-string keys
        with patch('builtins.open', mock_open(read_data='{1: "not a string key"}')) as mock_file,
                self.assertRaises(ValueError):
            secret_manager_service_client_secret_create.create_secret_sample(
                project_id=project_id, secret_id=secret_id, labels_file_path=labels_file_path
            )

        # Test case 4: Labels have non-string values
        with patch('builtins.open', mock_open(read_data='{"key": 123}')) as mock_file,
                self.assertRaises(ValueError):
            secret_manager_service_client_secret_create.create_secret_sample(
                project_id=project_id, secret_id=secret_id, labels_file_path=labels_file_path
            )

    def test_create_secret_labels_file_not_found(self):
        project_id = 'test-project'
        secret_id = 'test-secret-id'
        labels_file_path = 'nonexistent_labels.json'

        with self.assertRaises(FileNotFoundError):
            secret_manager_service_client_secret_create.create_secret_sample(
                project_id=project_id, secret_id=secret_id, labels_file_path=labels_file_path
            )


if __name__ == '__main__':
    unittest.main()
