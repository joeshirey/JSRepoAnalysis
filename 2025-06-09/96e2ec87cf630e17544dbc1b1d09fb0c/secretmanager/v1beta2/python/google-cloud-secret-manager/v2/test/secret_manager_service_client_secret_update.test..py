import os
import json
import unittest
from unittest.mock import patch, mock_open

from google.cloud import secretmanager_v1beta2
from google.cloud.secretmanager_v1beta2.types import Secret
from google.protobuf import field_mask_pb2
from google.protobuf import duration_pb2

import secret_manager_service_client_secret_update


class TestUpdateSecretSample(unittest.TestCase):

    PROJECT_ID = "test-project"
    SECRET_ID = "test-secret"

    @patch("secret_manager_service_client_secret_update.secretmanager_v1beta2.SecretManagerServiceClient")
    def test_update_secret_no_fields(self, mock_client):
        mock_client.return_value.update_secret.return_value = Secret(name=f"projects/{self.PROJECT_ID}/secrets/{self.SECRET_ID}")

        result = secret_manager_service_client_secret_update.update_secret_sample(
            project_id=self.PROJECT_ID,
            secret_id=self.SECRET_ID,
            new_labels_file=None,
            new_annotations_file=None,
            new_rotation_period_seconds=None,
            new_ttl_seconds=None,
        )

        self.assertIsNone(result)

    @patch("secret_manager_service_client_secret_update.secretmanager_v1beta2.SecretManagerServiceClient")
    def test_update_secret_labels(self, mock_client):
        mock_client.return_value.update_secret.return_value = Secret(name=f"projects/{self.PROJECT_ID}/secrets/{self.SECRET_ID}")
        labels_file_content = '{"key1": "value1", "key2": "value2"}'

        with patch("builtins.open", mock_open(read_data=labels_file_content)) as mock_file:
            result = secret_manager_service_client_secret_update.update_secret_sample(
                project_id=self.PROJECT_ID,
                secret_id=self.SECRET_ID,
                new_labels_file="labels.json",
                new_annotations_file=None,
                new_rotation_period_seconds=None,
                new_ttl_seconds=None,
            )

        self.assertIsNotNone(result)
        mock_client.return_value.update_secret.assert_called_once()

    @patch("secret_manager_service_client_secret_update.secretmanager_v1beta2.SecretManagerServiceClient")
    def test_update_secret_annotations(self, mock_client):
        mock_client.return_value.update_secret.return_value = Secret(name=f"projects/{self.PROJECT_ID}/secrets/{self.SECRET_ID}")
        annotations_file_content = '{"key1": "value1", "key2": "value2"}'

        with patch("builtins.open", mock_open(read_data=annotations_file_content)) as mock_file:
            result = secret_manager_service_client_secret_update.update_secret_sample(
                project_id=self.PROJECT_ID,
                secret_id=self.SECRET_ID,
                new_labels_file=None,
                new_annotations_file="annotations.json",
                new_rotation_period_seconds=None,
                new_ttl_seconds=None,
            )

        self.assertIsNotNone(result)
        mock_client.return_value.update_secret.assert_called_once()

    @patch("secret_manager_service_client_secret_update.secretmanager_v1beta2.SecretManagerServiceClient")
    def test_update_secret_rotation_period(self, mock_client):
        mock_client.return_value.update_secret.return_value = Secret(name=f"projects/{self.PROJECT_ID}/secrets/{self.SECRET_ID}")

        result = secret_manager_service_client_secret_update.update_secret_sample(
            project_id=self.PROJECT_ID,
            secret_id=self.SECRET_ID,
            new_labels_file=None,
            new_annotations_file=None,
            new_rotation_period_seconds=3600,
            new_ttl_seconds=None,
        )

        self.assertIsNotNone(result)
        mock_client.return_value.update_secret.assert_called_once()

    @patch("secret_manager_service_client_secret_update.secretmanager_v1beta2.SecretManagerServiceClient")
    def test_update_secret_ttl(self, mock_client):
        mock_client.return_value.update_secret.return_value = Secret(name=f"projects/{self.PROJECT_ID}/secrets/{self.SECRET_ID}")

        result = secret_manager_service_client_secret_update.update_secret_sample(
            project_id=self.PROJECT_ID,
            secret_id=self.SECRET_ID,
            new_labels_file=None,
            new_annotations_file=None,
            new_rotation_period_seconds=None,
            new_ttl_seconds=86400,
        )

        self.assertIsNotNone(result)
        mock_client.return_value.update_secret.assert_called_once()

    @patch("secret_manager_service_client_secret_update.secretmanager_v1beta2.SecretManagerServiceClient")
    def test_update_secret_all_fields(self, mock_client):
        mock_client.return_value.update_secret.return_value = Secret(name=f"projects/{self.PROJECT_ID}/secrets/{self.SECRET_ID}")
        labels_file_content = '{"key1": "value1", "key2": "value2"}'
        annotations_file_content = '{"key3": "value3", "key4": "value4"}'

        with patch("builtins.open", mock_open(read_data=labels_file_content)) as mock_labels_file, \
             patch("builtins.open", mock_open(read_data=annotations_file_content)) as mock_annotations_file:

            result = secret_manager_service_client_secret_update.update_secret_sample(
                project_id=self.PROJECT_ID,
                secret_id=self.SECRET_ID,
                new_labels_file="labels.json",
                new_annotations_file="annotations.json",
                new_rotation_period_seconds=3600,
                new_ttl_seconds=86400,
            )

        self.assertIsNotNone(result)
        mock_client.return_value.update_secret.assert_called_once()

    @patch("secret_manager_service_client_secret_update.secretmanager_v1beta2.SecretManagerServiceClient")
    def test_update_secret_invalid_labels_file(self, mock_client):
        mock_client.return_value.update_secret.return_value = Secret(name=f"projects/{self.PROJECT_ID}/secrets/{self.SECRET_ID}")
        labels_file_content = '["key1", "key2"]'

        with patch("builtins.open", mock_open(read_data=labels_file_content)):
            with self.assertRaises(ValueError):
                secret_manager_service_client_secret_update.update_secret_sample(
                    project_id=self.PROJECT_ID,
                    secret_id=self.SECRET_ID,
                    new_labels_file="labels.json",
                    new_annotations_file=None,
                    new_rotation_period_seconds=None,
                    new_ttl_seconds=None,
                )

    @patch("secret_manager_service_client_secret_update.secretmanager_v1beta2.SecretManagerServiceClient")
    def test_update_secret_invalid_annotations_file(self, mock_client):
        mock_client.return_value.update_secret.return_value = Secret(name=f"projects/{self.PROJECT_ID}/secrets/{self.SECRET_ID}")
        annotations_file_content = '["key1", "key2"]'

        with patch("builtins.open", mock_open(read_data=annotations_file_content)):
            with self.assertRaises(ValueError):
                secret_manager_service_client_secret_update.update_secret_sample(
                    project_id=self.PROJECT_ID,
                    secret_id=self.SECRET_ID,
                    new_labels_file=None,
                    new_annotations_file="annotations.json",
                    new_rotation_period_seconds=None,
                    new_ttl_seconds=None,
                )

    @patch("secret_manager_service_client_secret_update.secretmanager_v1beta2.SecretManagerServiceClient")
    def test_update_secret_labels_file_not_found(self, mock_client):
        mock_client.return_value.update_secret.return_value = Secret(name=f"projects/{self.PROJECT_ID}/secrets/{self.SECRET_ID}")

        with self.assertRaises(FileNotFoundError):
            secret_manager_service_client_secret_update.update_secret_sample(
                project_id=self.PROJECT_ID,
                secret_id=self.SECRET_ID,
                new_labels_file="nonexistent_labels.json",
                new_annotations_file=None,
                new_rotation_period_seconds=None,
                new_ttl_seconds=None,
            )

    @patch("secret_manager_service_client_secret_update.secretmanager_v1beta2.SecretManagerServiceClient")
    def test_update_secret_annotations_file_not_found(self, mock_client):
        mock_client.return_value.update_secret.return_value = Secret(name=f"projects/{self.PROJECT_ID}/secrets/{self.SECRET_ID}")

        with self.assertRaises(FileNotFoundError):
            secret_manager_service_client_secret_update.update_secret_sample(
                project_id=self.PROJECT_ID,
                secret_id=self.SECRET_ID,
                new_labels_file=None,
                new_annotations_file="nonexistent_annotations.json",
                new_rotation_period_seconds=None,
                new_ttl_seconds=None,
            )

    @patch("secret_manager_service_client_secret_update.secretmanager_v1beta2.SecretManagerServiceClient")
    def test_update_secret_labels_invalid_json(self, mock_client):
        mock_client.return_value.update_secret.return_value = Secret(name=f"projects/{self.PROJECT_ID}/secrets/{self.SECRET_ID}")
        labels_file_content = '{"key1": "value1", "key2": value2}'

        with patch("builtins.open", mock_open(read_data=labels_file_content)):
            with self.assertRaises(json.JSONDecodeError):
                secret_manager_service_client_secret_update.update_secret_sample(
                    project_id=self.PROJECT_ID,
                    secret_id=self.SECRET_ID,
                    new_labels_file="labels.json",
                    new_annotations_file=None,
                    new_rotation_period_seconds=None,
                    new_ttl_seconds=None,
                )

    @patch("secret_manager_service_client_secret_update.secretmanager_v1beta2.SecretManagerServiceClient")
    def test_update_secret_annotations_invalid_json(self, mock_client):
        mock_client.return_value.update_secret.return_value = Secret(name=f"projects/{self.PROJECT_ID}/secrets/{self.SECRET_ID}")
        annotations_file_content = '{"key1": "value1", "key2": value2}'

        with patch("builtins.open", mock_open(read_data=annotations_file_content)):
            with self.assertRaises(json.JSONDecodeError):
                secret_manager_service_client_secret_update.update_secret_sample(
                    project_id=self.PROJECT_ID,
                    secret_id=self.SECRET_ID,
                    new_labels_file=None,
                    new_annotations_file="annotations.json",
                    new_rotation_period_seconds=None,
                    new_ttl_seconds=None,
                )


if __name__ == "__main__":
    unittest.main()
