import os
import json
import unittest
from unittest.mock import patch, mock_open
from google.cloud import secretmanager_v1beta2
from google.cloud.secretmanager_v1beta2.types import Secret
from google.protobuf import field_mask_pb2

# Assuming the code under test is in a file named 'secret_manager_service_client_secret_update.py'
import secret_manager_service_client_secret_update


class TestUpdateSecret(unittest.TestCase):

    @patch('secret_manager_service_client_secret_update.secretmanager_v1beta2.SecretManagerServiceClient')
    def test_update_secret_no_files(self, mock_client):
        # Test that the function raises an error when no files are provided
        project_id = 'test-project'
        secret_id = 'test-secret'
        with self.assertRaises(ValueError) as context:
            secret_manager_service_client_secret_update.update_secret_sample(project_id, secret_id)
        self.assertEqual(str(context.exception),
                         "No fields specified for update. Provide --new_labels_file or --new_annotations_file.")
        mock_client.return_value.close.assert_called_once()

    @patch('secret_manager_service_client_secret_update.secretmanager_v1beta2.SecretManagerServiceClient')
    def test_update_secret_with_labels(self, mock_client):
        # Test that the function updates the secret with labels from a file
        project_id = 'test-project'
        secret_id = 'test-secret'
        labels_file = 'test_labels.json'
        labels = {"key1": "value1", "key2": "value2"}

        # Mock the file opening and reading
        with patch('builtins.open', mock_open(read_data=json.dumps(labels))) as mock_file:
            # Configure the mock client
            mock_secret = Secret(name=f"projects/{project_id}/secrets/{secret_id}", labels=labels)
            mock_client.return_value.update_secret.return_value = mock_secret

            # Call the function
            result = secret_manager_service_client_secret_update.update_secret_sample(
                project_id, secret_id, new_labels_file=labels_file
            )

            # Assertions
            self.assertEqual(result.name, f"projects/{project_id}/secrets/{secret_id}")
            self.assertEqual(result.labels, labels)
            mock_client.return_value.update_secret.assert_called_once()
            mock_client.return_value.close.assert_called_once()

    @patch('secret_manager_service_client_secret_update.secretmanager_v1beta2.SecretManagerServiceClient')
    def test_update_secret_with_annotations(self, mock_client):
        # Test that the function updates the secret with annotations from a file
        project_id = 'test-project'
        secret_id = 'test-secret'
        annotations_file = 'test_annotations.json'
        annotations = {"key1": "value1", "key2": "value2"}

        # Mock the file opening and reading
        with patch('builtins.open', mock_open(read_data=json.dumps(annotations))) as mock_file:
            # Configure the mock client
            mock_secret = Secret(name=f"projects/{project_id}/secrets/{secret_id}", annotations=annotations)
            mock_client.return_value.update_secret.return_value = mock_secret

            # Call the function
            result = secret_manager_service_client_secret_update.update_secret_sample(
                project_id, secret_id, new_annotations_file=annotations_file
            )

            # Assertions
            self.assertEqual(result.name, f"projects/{project_id}/secrets/{secret_id}")
            self.assertEqual(result.annotations, annotations)
            mock_client.return_value.update_secret.assert_called_once()
            mock_client.return_value.close.assert_called_once()

    @patch('secret_manager_service_client_secret_update.secretmanager_v1beta2.SecretManagerServiceClient')
    def test_update_secret_invalid_labels_file(self, mock_client):
        # Test that the function raises an error when the labels file is not a valid JSON
        project_id = 'test-project'
        secret_id = 'test-secret'
        labels_file = 'test_labels.json'

        # Mock the file opening and reading to return invalid JSON
        with patch('builtins.open', mock_open(read_data='invalid json')):
            with self.assertRaises(json.JSONDecodeError):
                secret_manager_service_client_secret_update.update_secret_sample(
                    project_id, secret_id, new_labels_file=labels_file
                )
        mock_client.return_value.close.assert_called_once()

    @patch('secret_manager_service_client_secret_update.secretmanager_v1beta2.SecretManagerServiceClient')
    def test_update_secret_invalid_annotations_file(self, mock_client):
        # Test that the function raises an error when the annotations file is not a valid JSON
        project_id = 'test-project'
        secret_id = 'test-secret'
        annotations_file = 'test_annotations.json'

        # Mock the file opening and reading to return invalid JSON
        with patch('builtins.open', mock_open(read_data='invalid json')):
            with self.assertRaises(json.JSONDecodeError):
                secret_manager_service_client_secret_update.update_secret_sample(
                    project_id, secret_id, new_annotations_file=annotations_file
                )
        mock_client.return_value.close.assert_called_once()

    @patch('secret_manager_service_client_secret_update.secretmanager_v1beta2.SecretManagerServiceClient')
    def test_update_secret_labels_file_not_found(self, mock_client):
        # Test that the function raises an error when the labels file is not found
        project_id = 'test-project'
        secret_id = 'test-secret'
        labels_file = 'nonexistent_labels.json'

        with self.assertRaises(FileNotFoundError):
            secret_manager_service_client_secret_update.update_secret_sample(
                project_id, secret_id, new_labels_file=labels_file
            )
        mock_client.return_value.close.assert_called_once()

    @patch('secret_manager_service_client_secret_update.secretmanager_v1beta2.SecretManagerServiceClient')
    def test_update_secret_annotations_file_not_found(self, mock_client):
        # Test that the function raises an error when the annotations file is not found
        project_id = 'test-project'
        secret_id = 'test-secret'
        annotations_file = 'nonexistent_annotations.json'

        with self.assertRaises(FileNotFoundError):
            secret_manager_service_client_secret_update.update_secret_sample(
                project_id, secret_id, new_annotations_file=annotations_file
            )
        mock_client.return_value.close.assert_called_once()


if __name__ == '__main__':
    unittest.main()
