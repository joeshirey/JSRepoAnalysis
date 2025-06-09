import unittest
import os
import json
from unittest.mock import patch, mock_open
from google.api_core import exceptions

# Assuming the code under test is in 'secret_manager_service_client_secret_update.py'
import secret_manager_service_client_secret_update


class TestUpdateSecretSample(unittest.TestCase):

    PROJECT_ID = "test-project"
    SECRET_ID = "test-secret"

    def setUp(self):
        # Create dummy files for testing
        self.labels_file = "test_labels.json"
        self.replication_file = "test_replication.json"

        with open(self.labels_file, "w") as f:
            json.dump({"env": "test", "team": "testing"}, f)

        with open(self.replication_file, "w") as f:
            json.dump({"automatic": {}}, f)

        # Set environment variable for testing
        os.environ["GOOGLE_CLOUD_PROJECT"] = self.PROJECT_ID

    def tearDown(self):
        # Remove dummy files after testing
        if os.path.exists(self.labels_file):
            os.remove(self.labels_file)
        if os.path.exists(self.replication_file):
            os.remove(self.replication_file)

        # Remove environment variable after testing
        if "GOOGLE_CLOUD_PROJECT" in os.environ:
            del os.environ["GOOGLE_CLOUD_PROJECT"]

    @patch("secret_manager_service_client_secret_update.secretmanager_v1.SecretManagerServiceClient")
    def test_update_secret_success(self, mock_client):
        # Mock the client and its methods
        mock_secret = mock_client.return_value.update_secret.return_value
        mock_secret.name = f"projects/{self.PROJECT_ID}/secrets/{self.SECRET_ID}"

        # Call the function with the dummy files
        result = secret_manager_service_client_secret_update.update_secret_sample(
            project_id=self.PROJECT_ID,
            secret_id=self.SECRET_ID,
            new_labels_file=self.labels_file,
            new_replication_policy_file=self.replication_file,
        )

        # Assert that the client's update_secret method was called with the correct arguments
        mock_client.return_value.update_secret.assert_called_once()
        self.assertEqual(result.name, mock_secret.name)

    @patch("secret_manager_service_client_secret_update.secretmanager_v1.SecretManagerServiceClient")
    def test_update_secret_labels_only(self, mock_client):
        # Mock the client and its methods
        mock_secret = mock_client.return_value.update_secret.return_value
        mock_secret.name = f"projects/{self.PROJECT_ID}/secrets/{self.SECRET_ID}"

        # Call the function with only the labels file
        result = secret_manager_service_client_secret_update.update_secret_sample(
            project_id=self.PROJECT_ID,
            secret_id=self.SECRET_ID,
            new_labels_file=self.labels_file,
        )

        # Assert that the client's update_secret method was called with the correct arguments
        mock_client.return_value.update_secret.assert_called_once()
        self.assertEqual(result.name, mock_secret.name)

    @patch("secret_manager_service_client_secret_update.secretmanager_v1.SecretManagerServiceClient")
    def test_update_secret_replication_only(self, mock_client):
        # Mock the client and its methods
        mock_secret = mock_client.return_value.update_secret.return_value
        mock_secret.name = f"projects/{self.PROJECT_ID}/secrets/{self.SECRET_ID}"

        # Call the function with only the replication file
        result = secret_manager_service_client_secret_update.update_secret_sample(
            project_id=self.PROJECT_ID,
            secret_id=self.SECRET_ID,
            new_replication_policy_file=self.replication_file,
        )

        # Assert that the client's update_secret method was called with the correct arguments
        mock_client.return_value.update_secret.assert_called_once()
        self.assertEqual(result.name, mock_secret.name)

    def test_update_secret_no_update_files(self):
        with self.assertRaises(ValueError):
            secret_manager_service_client_secret_update.update_secret_sample(
                project_id=self.PROJECT_ID,
                secret_id=self.SECRET_ID,
            )

    def test_update_secret_invalid_labels_file(self):
        with self.assertRaises(FileNotFoundError):
            secret_manager_service_client_secret_update.update_secret_sample(
                project_id=self.PROJECT_ID,
                secret_id=self.SECRET_ID,
                new_labels_file="nonexistent_file.json",
            )

    def test_update_secret_invalid_replication_file(self):
        with self.assertRaises(FileNotFoundError):
            secret_manager_service_client_secret_update.update_secret_sample(
                project_id=self.PROJECT_ID,
                secret_id=self.SECRET_ID,
                new_replication_policy_file="nonexistent_file.json",
            )


if __name__ == "__main__":
    unittest.main()
