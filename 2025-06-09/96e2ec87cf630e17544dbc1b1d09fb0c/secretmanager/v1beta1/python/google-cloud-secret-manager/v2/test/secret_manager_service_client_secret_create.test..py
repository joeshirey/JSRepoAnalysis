import os
import unittest
from unittest.mock import patch
import sys
import json

# Assuming the code under test is in 'secret_manager_service_client_secret_create.py'
sys.path.append('..')
import secret_manager_service_client_secret_create


class TestCreateSecret(unittest.TestCase):

    @patch('google.cloud.secretmanager_v1beta1.SecretManagerServiceClient')
    def test_create_secret_success(self, mock_client):
        # Mock the client's create_secret method
        mock_secret = mock_client.return_value.create_secret.return_value
        mock_secret.name = 'projects/test-project/secrets/test-secret'

        # Call the function
        project_id = 'test-project'
        secret_id = 'test-secret'
        created_secret = secret_manager_service_client_secret_create.create_secret_sample(project_id, secret_id)

        # Assert that the client's create_secret method was called with the correct arguments
        mock_client.return_value.create_secret.assert_called_once()
        args, kwargs = mock_client.return_value.create_secret.call_args
        self.assertEqual(kwargs['parent'], f'projects/{project_id}')
        self.assertEqual(kwargs['secret_id'], secret_id)

        # Assert that the function returns the mock secret
        self.assertEqual(created_secret, mock_secret)
        self.assertIn(secret_id, created_secret.name)

    @patch('google.cloud.secretmanager_v1beta1.SecretManagerServiceClient')
    def test_create_secret_with_labels(self, mock_client):
        # Mock the client's create_secret method
        mock_secret = mock_client.return_value.create_secret.return_value
        mock_secret.name = 'projects/test-project/secrets/test-secret'

        # Call the function with labels
        project_id = 'test-project'
        secret_id = 'test-secret'
        labels = {'env': 'dev', 'owner': 'team-a'}
        created_secret = secret_manager_service_client_secret_create.create_secret_sample(project_id, secret_id, labels=labels)

        # Assert that the client's create_secret method was called with the correct arguments
        mock_client.return_value.create_secret.assert_called_once()
        args, kwargs = mock_client.return_value.create_secret.call_args
        self.assertEqual(kwargs['parent'], f'projects/{project_id}')
        self.assertEqual(kwargs['secret_id'], secret_id)
        self.assertEqual(kwargs['secret'].labels, labels)

        # Assert that the function returns the mock secret
        self.assertEqual(created_secret, mock_secret)
        self.assertIn(secret_id, created_secret.name)

    @patch('google.cloud.secretmanager_v1beta1.SecretManagerServiceClient')
    def test_create_secret_exception(self, mock_client):
        # Mock the client's create_secret method to raise an exception
        mock_client.return_value.create_secret.side_effect = Exception('API error')

        # Call the function and assert that it raises the exception
        project_id = 'test-project'
        secret_id = 'test-secret'
        with self.assertRaises(Exception) as context:
            secret_manager_service_client_secret_create.create_secret_sample(project_id, secret_id)

        self.assertEqual(str(context.exception), 'API error')


if __name__ == '__main__':
    unittest.main()
