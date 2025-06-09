import unittest
import os
import json
from unittest.mock import MagicMock, patch
from google.cloud import secretmanager_v1
from google.cloud.secretmanager_v1.services import secret_manager_service

# Import the code under test
import secret_manager_service_client_secret_create

class TestCreateSecretSample(unittest.TestCase):

    @patch.object(secret_manager_service.SecretManagerServiceAsyncClient, 'create_secret', new_callable=MagicMock)    
    def test_create_secret_success(self, mock_create_secret):
        # Mock the SecretManagerServiceClient
        mock_client = MagicMock()

        # Define test data
        project_id = "test-project"
        secret_id = "test-secret"
        secret_config = {"replication": {"automatic": {}}}

        # Configure the mock to return a sample secret
        expected_secret = secretmanager_v1.Secret()
        mock_create_secret.return_value = expected_secret

        # Call the function
        created_secret = secret_manager_service_client_secret_create.create_secret_sample(
            project_id, secret_id, secret_config
        )

        # Assert that the client's create_secret method was called with the correct arguments
        mock_create_secret.assert_called_once()

        # Assert that the function returns the expected secret
        self.assertEqual(created_secret, expected_secret)

    @patch.object(secret_manager_service.SecretManagerServiceAsyncClient, 'create_secret', new_callable=MagicMock)
    def test_create_secret_failure(self, mock_create_secret):
        # Mock the SecretManagerServiceClient
        mock_client = MagicMock()

        # Define test data
        project_id = "test-project"
        secret_id = "test-secret"
        secret_config = {"replication": {"automatic": {}}}

        # Configure the mock to raise an exception
        mock_create_secret.side_effect = Exception("Failed to create secret")

        # Call the function and assert that it raises an exception
        with self.assertRaises(Exception) as context:
            secret_manager_service_client_secret_create.create_secret_sample(
                project_id, secret_id, secret_config
            )

        self.assertEqual(str(context.exception), "Failed to create secret")


if __name__ == '__main__':
    unittest.main()
