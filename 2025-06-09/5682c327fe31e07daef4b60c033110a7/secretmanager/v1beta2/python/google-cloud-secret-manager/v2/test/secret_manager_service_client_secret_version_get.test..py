import os
import unittest
from unittest.mock import patch
import json

from google.api_core import exceptions
from google.cloud import secretmanager_v1beta2
from google.cloud.secretmanager_v1beta2 import services

# Assuming the code under test is in 'secret_manager_service_client_secret_version_get.py'
import secret_manager_service_client_secret_version_get as secret_manager


class TestGetSecretVersionSample(unittest.TestCase):

    PROJECT_ID = "test-project"
    SECRET_ID = "test-secret"
    VERSION_ID = "1"

    def test_get_secret_version_success(self):
        # Mock the SecretManagerServiceClient and its methods
        mock_client = unittest.mock.MagicMock()
        mock_secret_version = secretmanager_v1beta2.SecretVersion()
        mock_secret_version.name = f"projects/{self.PROJECT_ID}/secrets/{self.SECRET_ID}/versions/{self.VERSION_ID}"
        mock_client.get_secret_version.return_value = mock_secret_version

        with patch("secret_manager_service_client_secret_version_get.secretmanager_v1beta2.SecretManagerServiceClient", return_value=mock_client):
            secret_version = secret_manager.get_secret_version_sample(
                self.PROJECT_ID, self.SECRET_ID, self.VERSION_ID
            )

        self.assertIsNotNone(secret_version)
        self.assertEqual(secret_version.name, f"projects/{self.PROJECT_ID}/secrets/{self.SECRET_ID}/versions/{self.VERSION_ID}")
        mock_client.get_secret_version.assert_called_once()

    def test_get_secret_version_not_found(self, capsys=None):
        # Mock the SecretManagerServiceClient to raise a NotFound exception
        mock_client = unittest.mock.MagicMock()
        mock_client.get_secret_version.side_effect = exceptions.NotFound("Secret version not found")

        with patch("secret_manager_service_client_secret_version_get.secretmanager_v1beta2.SecretManagerServiceClient", return_value=mock_client):
            secret_version = secret_manager.get_secret_version_sample(
                self.PROJECT_ID, self.SECRET_ID, self.VERSION_ID
            )

        self.assertIsNone(secret_version)
        mock_client.get_secret_version.assert_called_once()

    def test_get_secret_version_permission_denied(self, capsys=None):
        # Mock the SecretManagerServiceClient to raise a PermissionDenied exception
        mock_client = unittest.mock.MagicMock()
        mock_client.get_secret_version.side_effect = exceptions.PermissionDenied("Permission denied")

        with patch("secret_manager_service_client_secret_version_get.secretmanager_v1beta2.SecretManagerServiceClient", return_value=mock_client):
            secret_version = secret_manager.get_secret_version_sample(
                self.PROJECT_ID, self.SECRET_ID, self.VERSION_ID
            )

        self.assertIsNone(secret_version)
        mock_client.get_secret_version.assert_called_once()

    def test_get_secret_version_unexpected_error(self, capsys=None):
        # Mock the SecretManagerServiceClient to raise an unexpected exception
        mock_client = unittest.mock.MagicMock()
        mock_client.get_secret_version.side_effect = ValueError("Unexpected error")

        with patch("secret_manager_service_client_secret_version_get.secretmanager_v1beta2.SecretManagerServiceClient", return_value=mock_client):
            secret_version = secret_manager.get_secret_version_sample(
                self.PROJECT_ID, self.SECRET_ID, self.VERSION_ID
            )

        self.assertIsNone(secret_version)
        mock_client.get_secret_version.assert_called_once()

    def test_main_no_project_id(self, capsys=None):
        # Test the main function when GCP_PROJECT_ID is not set
        with patch.dict(os.environ, {"GCP_PROJECT_ID": ""}):
            with patch("argparse.ArgumentParser.parse_args", return_value=unittest.mock.MagicMock(secret_id=self.SECRET_ID, version_id=self.VERSION_ID)):
                with patch("secret_manager_service_client_secret_version_get.get_secret_version_sample") as mock_get_secret:
                    secret_manager.main()
                    mock_get_secret.assert_not_called()

    def test_main_success(self, capsys=None):
        # Test the main function with a valid project ID
        mock_secret_version = unittest.mock.MagicMock()
        mock_secret_version.name = f"projects/{self.PROJECT_ID}/secrets/{self.SECRET_ID}/versions/{self.VERSION_ID}"
        mock_secret_version.create_time = None
        mock_secret_version.destroy_time = None
        mock_secret_version.state = 1
        mock_secret_version.etag = "test_etag"
        mock_secret_version.client_specified_payload_checksum = None
        mock_secret_version.scheduled_destroy_time = None
        mock_secret_version.HasField.return_value = False

        with patch.dict(os.environ, {"GCP_PROJECT_ID": self.PROJECT_ID}):
            with patch("argparse.ArgumentParser.parse_args", return_value=unittest.mock.MagicMock(secret_id=self.SECRET_ID, version_id=self.VERSION_ID)):
                with patch("secret_manager_service_client_secret_version_get.get_secret_version_sample", return_value=mock_secret_version):
                    with patch("json.dumps") as mock_json_dumps:
                        secret_manager.main()
                        mock_json_dumps.assert_called_once()


if __name__ == "__main__":
    unittest.main()
