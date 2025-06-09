import os
import unittest
from unittest.mock import MagicMock, patch
import json
import sys

# Assuming the code under test is in 'secret_manager_service_client_secret_create.py'
sys.path.append('..')
import secret_manager_service_client_secret_create


class TestCreateSecretSample(unittest.TestCase):

    @patch('google.cloud.secretmanager_v1beta2.SecretManagerServiceClient')
    def test_create_secret_sample_no_config(self, mock_client):
        # Mock the client and its methods
        mock_secret = MagicMock()
        mock_client_instance = mock_client.return_value
        mock_client_instance.create_secret.return_value = mock_secret
        mock_secret.name = 'test-secret'

        # Call the function with a project ID and secret ID
        project_id = 'test-project'
        secret_id = 'test-secret-id'
        created_secret = secret_manager_service_client_secret_create.create_secret_sample(
            project_id, secret_id
        )

        # Assert that the client's create_secret method was called with the correct arguments
        mock_client_instance.create_secret.assert_called_once()
        call_args = mock_client_instance.create_secret.call_args
        self.assertEqual(call_args[1]['request']['parent'], f'projects/{project_id}')
        self.assertEqual(call_args[1]['request']['secret_id'], secret_id)
        self.assertIsNotNone(call_args[1]['request']['secret'])

        # Assert that the function returns the created secret
        self.assertEqual(created_secret, mock_secret)

    @patch('google.cloud.secretmanager_v1beta2.SecretManagerServiceClient')
    def test_create_secret_sample_with_config(self, mock_client):
        # Mock the client and its methods
        mock_secret = MagicMock()
        mock_client_instance = mock_client.return_value
        mock_client_instance.create_secret.return_value = mock_secret
        mock_secret.name = 'test-secret'

        # Create a dummy secret config file
        secret_config = {
            'replication': {
                'automatic': {}
            }
        }
        config_file_path = 'test_secret_config.json'
        with open(config_file_path, 'w') as f:
            json.dump(secret_config, f)

        # Call the function with a project ID, secret ID, and config file path
        project_id = 'test-project'
        secret_id = 'test-secret-id'
        created_secret = secret_manager_service_client_secret_create.create_secret_sample(
            project_id, secret_id, config_file_path
        )

        # Assert that the client's create_secret method was called with the correct arguments
        mock_client_instance.create_secret.assert_called_once()
        call_args = mock_client_instance.create_secret.call_args
        self.assertEqual(call_args[1]['request']['parent'], f'projects/{project_id}')
        self.assertEqual(call_args[1]['request']['secret_id'], secret_id)
        self.assertIsNotNone(call_args[1]['request']['secret'])

        # Assert that the function returns the created secret
        self.assertEqual(created_secret, mock_secret)

        # Clean up the dummy config file
        os.remove(config_file_path)

    @patch('google.cloud.secretmanager_v1beta2.SecretManagerServiceClient')
    def test_create_secret_sample_with_invalid_config(self, mock_client):
        # Create a dummy invalid secret config file (e.g., with syntax errors)
        invalid_secret_config = '{\n    "replication": {\n        "automatic": {\n            "foo": }  # Syntax error\n        }\n    }\n}'
        config_file_path = 'invalid_secret_config.json'
        with open(config_file_path, 'w') as f:
            f.write(invalid_secret_config)

        # Call the function with the invalid config file path
        project_id = 'test-project'
        secret_id = 'test-secret-id'

        with self.assertRaises(SystemExit) as context:
            secret_manager_service_client_secret_create.create_secret_sample(
                project_id, secret_id, config_file_path
            )
        self.assertEqual(context.exception.code, 1)

        # Clean up the dummy config file
        os.remove(config_file_path)

    @patch('google.cloud.secretmanager_v1beta2.SecretManagerServiceClient')
    def test_create_secret_sample_prints_resource_name(self, mock_client):
        # Mock the client and its methods
        mock_secret = MagicMock()
        mock_client_instance = mock_client.return_value
        mock_client_instance.create_secret.return_value = mock_secret
        mock_secret.name = 'test-secret-resource-name'

        project_id = 'test-project'
        secret_id = 'test-secret-id'

        created_secret = secret_manager_service_client_secret_create.create_secret_sample(
            project_id, secret_id
        )

        self.assertEqual(created_secret.name, 'test-secret-resource-name')

if __name__ == '__main__':
    unittest.main()
