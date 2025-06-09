import os
import unittest
from unittest.mock import MagicMock, patch
import json

from google.api_core import exceptions
from google.cloud import secretmanager_v1beta2

# Assuming the code under test is in 'secret_manager_service_client_secret_versions_list.py'
import secret_manager_service_client_secret_versions_list as sm


class TestListSecretVersions(unittest.TestCase):

    @patch('secret_manager_service_client_secret_versions_list.secretmanager_v1beta2.SecretManagerServiceClient')
    def test_list_secret_versions_success(self, mock_client):
        # Mock the SecretManagerServiceClient and its methods
        mock_version = MagicMock()
        mock_version.name = 'projects/test-project/secrets/test-secret/versions/1'
        mock_version.state = secretmanager_v1beta2.SecretVersion.State.ENABLED
        mock_version.create_time = None
        mock_version.destroy_time = None
        mock_version.etag = 'test-etag'
        mock_version.client_managed = False

        mock_list_secret_versions = MagicMock(return_value=[mock_version])
        mock_client.return_value.list_secret_versions = mock_list_secret_versions
        mock_client.return_value.secret_path.return_value = 'projects/test-project/secrets/test-secret'

        # Call the function under test
        project_id = 'test-project'
        secret_id = 'test-secret'
        versions = sm.list_secret_versions(project_id, secret_id)

        # Assertions
        self.assertEqual(len(versions), 1)
        self.assertEqual(versions[0].name, 'projects/test-project/secrets/test-secret/versions/1')
        mock_client.return_value.list_secret_versions.assert_called_once()

    @patch('secret_manager_service_client_secret_versions_list.secretmanager_v1beta2.SecretManagerServiceClient')
    def test_list_secret_versions_not_found(self, mock_client):
        # Mock the SecretManagerServiceClient to raise a NotFound exception
        mock_client.return_value.list_secret_versions.side_effect = exceptions.NotFound('Secret not found')
        mock_client.return_value.secret_path.return_value = 'projects/test-project/secrets/test-secret'

        # Call the function under test
        project_id = 'test-project'
        secret_id = 'test-secret'

        # Capture stdout
        import io
        import sys
        captured_output = io.StringIO()
        sys.stderr = captured_output

        versions = sm.list_secret_versions(project_id, secret_id)

        sys.stderr = sys.__stderr__
        # Assertions
        self.assertEqual(len(versions), 0)
        self.assertIn(f"Error: Secret '{secret_id}' not found in project '{project_id}'", captured_output.getvalue())

    @patch('secret_manager_service_client_secret_versions_list.secretmanager_v1beta2.SecretManagerServiceClient')
    def test_list_secret_versions_permission_denied(self, mock_client):
        # Mock the SecretManagerServiceClient to raise a PermissionDenied exception
        mock_client.return_value.list_secret_versions.side_effect = exceptions.PermissionDenied('Permission denied')
        mock_client.return_value.secret_path.return_value = 'projects/test-project/secrets/test-secret'

        # Call the function under test
        project_id = 'test-project'
        secret_id = 'test-secret'

        # Capture stdout
        import io
        import sys
        captured_output = io.StringIO()
        sys.stderr = captured_output

        versions = sm.list_secret_versions(project_id, secret_id)

        sys.stderr = sys.__stderr__

        # Assertions
        self.assertEqual(len(versions), 0)
        self.assertIn(f"Error: Permission denied to access secret '{secret_id}' in project '{project_id}'", captured_output.getvalue())

    @patch('secret_manager_service_client_secret_versions_list.secretmanager_v1beta2.SecretManagerServiceClient')
    def test_list_secret_versions_api_error(self, mock_client):
        # Mock the SecretManagerServiceClient to raise a GoogleAPICallError exception
        mock_client.return_value.list_secret_versions.side_effect = exceptions.GoogleAPICallError('API Error')
        mock_client.return_value.secret_path.return_value = 'projects/test-project/secrets/test-secret'

        # Call the function under test
        project_id = 'test-project'
        secret_id = 'test-secret'

        # Capture stdout
        import io
        import sys
        captured_output = io.StringIO()
        sys.stderr = captured_output

        versions = sm.list_secret_versions(project_id, secret_id)

        sys.stderr = sys.__stderr__

        # Assertions
        self.assertEqual(len(versions), 0)
        self.assertIn("An API error occurred: API Error", captured_output.getvalue())

    @patch('secret_manager_service_client_secret_versions_list.secretmanager_v1beta2.SecretManagerServiceClient')
    def test_list_secret_versions_unexpected_error(self, mock_client):
        # Mock the SecretManagerServiceClient to raise an unexpected exception
        mock_client.return_value.list_secret_versions.side_effect = Exception('Unexpected Error')
        mock_client.return_value.secret_path.return_value = 'projects/test-project/secrets/test-secret'

        # Call the function under test
        project_id = 'test-project'
        secret_id = 'test-secret'

        # Capture stdout
        import io
        import sys
        captured_output = io.StringIO()
        sys.stderr = captured_output

        versions = sm.list_secret_versions(project_id, secret_id)

        sys.stderr = sys.__stderr__

        # Assertions
        self.assertEqual(len(versions), 0)
        self.assertIn("An unexpected error occurred: Unexpected Error", captured_output.getvalue())


    @patch('secret_manager_service_client_secret_versions_list.os.environ.get')
    @patch('secret_manager_service_client_secret_versions_list.sm.list_secret_versions')
    @patch('secret_manager_service_client_secret_versions_list.argparse.ArgumentParser.parse_args')
    def test_main_success(self, mock_parse_args, mock_list_secret_versions, mock_environ_get):
        # Mock the environment variable and command line arguments
        mock_environ_get.return_value = 'test-project'
        mock_args = MagicMock()
        mock_args.secret_id = 'test-secret'
        mock_parse_args.return_value = mock_args

        # Mock the list_secret_versions function
        mock_version = MagicMock()
        mock_version.name = 'projects/test-project/secrets/test-secret/versions/1'
        mock_version.state = secretmanager_v1beta2.SecretVersion.State.ENABLED
        mock_version.create_time = None
        mock_version.destroy_time = None
        mock_version.etag = 'test-etag'
        mock_version.client_managed = False
        mock_list_secret_versions.return_value = [mock_version]

        # Capture stdout
        import io
        import sys
        captured_output = io.StringIO()
        sys.stdout = captured_output

        # Call the main function
        sm.main()

        # Restore stdout
        sys.stdout = sys.__stdout__

        # Assertions
        expected_output = json.dumps([
            {
                "name": mock_version.name,
                "state": "ENABLED",
                "create_time": None,
                "destroy_time": None,
                "etag": mock_version.etag,
                "client_managed": mock_version.client_managed
            }
        ], indent=2)
        self.assertEqual(captured_output.getvalue().strip(), expected_output)


    @patch('secret_manager_service_client_secret_versions_list.os.environ.get')
    def test_main_no_project_id(self, mock_environ_get):
        # Mock the environment variable to return None (project ID not set)
        mock_environ_get.return_value = None

        # Capture stderr and prevent the program from exiting
        import io
        import sys
        captured_output = io.StringIO()
        sys.stderr = captured_output

        with self.assertRaises(SystemExit) as context:
            sm.main()

        sys.stderr = sys.__stderr__

        # Assertions
        self.assertIn("Error: GCP_PROJECT_ID environment variable not set", captured_output.getvalue())
        self.assertEqual(context.exception.code, 1)


if __name__ == '__main__':
    unittest.main()
