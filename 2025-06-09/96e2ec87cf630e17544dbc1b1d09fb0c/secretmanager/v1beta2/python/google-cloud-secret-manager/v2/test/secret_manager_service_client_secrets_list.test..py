import os
import unittest
from unittest import mock
import json

from google.api_core import exceptions
from google.cloud import secretmanager_v1beta2

# Replace 'your_module' with the actual name of your module
import secret_manager_service_client_secrets_list


class TestListSecretsSample(unittest.TestCase):

    @mock.patch('secret_manager_service_client_secrets_list.secretmanager_v1beta2.SecretManagerServiceClient')
    def test_list_secrets_success_no_location(self, mock_client):
        # Mock the client and its methods
        mock_secret = mock.Mock()
        mock_secret.name = 'projects/test-project/secrets/test-secret'
        mock_secret.create_time = mock.Mock()
        mock_secret.create_time.isoformat.return_value = '2023-10-26T00:00:00Z'
        mock_secret.replication.automatic = mock.Mock()

        mock_list_secrets = mock.Mock()
        mock_list_secrets.return_value = [mock_secret]
        mock_client.return_value.list_secrets = mock_list_secrets

        # Call the function
        project_id = 'test-project'
        secrets = secret_manager_service_client_secrets_list.list_secrets_sample(project_id)

        # Assertions
        self.assertEqual(len(secrets), 1)
        self.assertEqual(secrets[0]['name'], 'projects/test-project/secrets/test-secret')
        self.assertEqual(secrets[0]['create_time'], '2023-10-26T00:00:00Z')
        self.assertTrue(secrets[0]['replication']['automatic'])

        # Verify that the client's list_secrets method was called with the correct parent
        mock_client.return_value.list_secrets.assert_called_once_with(parent='projects/test-project')

    @mock.patch('secret_manager_service_client_secrets_list.secretmanager_v1beta2.SecretManagerServiceClient')
    def test_list_secrets_success_with_location(self, mock_client):
        # Mock the client and its methods
        mock_secret = mock.Mock()
        mock_secret.name = 'projects/test-project/secrets/test-secret'
        mock_secret.create_time = mock.Mock()
        mock_secret.create_time.isoformat.return_value = '2023-10-26T00:00:00Z'
        mock_secret.replication.automatic = mock.Mock()

        mock_list_secrets = mock.Mock()
        mock_list_secrets.return_value = [mock_secret]
        mock_client.return_value.list_secrets = mock_list_secrets

        # Call the function
        project_id = 'test-project'
        location_id = 'us-central1'
        secrets = secret_manager_service_client_secrets_list.list_secrets_sample(project_id, location_id)

        # Assertions
        self.assertEqual(len(secrets), 1)
        self.assertEqual(secrets[0]['name'], 'projects/test-project/secrets/test-secret')
        self.assertEqual(secrets[0]['create_time'], '2023-10-26T00:00:00Z')
        self.assertTrue(secrets[0]['replication']['automatic'])

        # Verify that the client's list_secrets method was called with the correct parent
        mock_client.return_value.list_secrets.assert_called_once_with(parent='projects/test-project/locations/us-central1')

    @mock.patch('secret_manager_service_client_secrets_list.secretmanager_v1beta2.SecretManagerServiceClient')
    def test_list_secrets_error(self, mock_client):
        # Mock the client to raise an exception
        mock_client.return_value.list_secrets.side_effect = exceptions.PermissionDenied('permission denied')

        # Call the function
        project_id = 'test-project'
        secrets = secret_manager_service_client_secrets_list.list_secrets_sample(project_id)

        # Assertions
        self.assertEqual(secrets, [])

    @mock.patch('secret_manager_service_client_secrets_list.secretmanager_v1beta2.SecretManagerServiceClient')
    def test_main_no_project_id(self, mock_client):
        # Mock os.environ.get to return None, simulating no project ID
        with mock.patch.dict(os.environ, clear=True):
            with self.assertRaises(SystemExit) as cm:
                secret_manager_service_client_secrets_list.main()
            self.assertEqual(cm.exception.code, 1)

    @mock.patch('secret_manager_service_client_secrets_list.secretmanager_v1beta2.SecretManagerServiceClient')
    @mock.patch('secret_manager_service_client_secrets_list.list_secrets_sample')
    @mock.patch('argparse.ArgumentParser.parse_args')
    @mock.patch.dict(os.environ, {'GCP_PROJECT_ID': 'test-project'})  # Set project ID
    def test_main_success(self, mock_parse_args, mock_list_secrets_sample, mock_client):
        # Mock the return value of parse_args
        mock_args = mock.Mock()
        mock_args.location_id = None
        mock_parse_args.return_value = mock_args

        # Mock the return value of list_secrets_sample
        mock_list_secrets_sample.return_value = [{'name': 'test-secret'}]

        # Mock print to capture the output
        with mock.patch('builtins.print') as mock_print:
            secret_manager_service_client_secrets_list.main()

        # Assert that list_secrets_sample was called with the correct arguments
        mock_list_secrets_sample.assert_called_once_with('test-project', None)

        # Assert that print was called with the JSON representation of the secrets
        mock_print.assert_called_once_with(json.dumps([{'name': 'test-secret'}], indent=2))


if __name__ == '__main__':
    unittest.main()
