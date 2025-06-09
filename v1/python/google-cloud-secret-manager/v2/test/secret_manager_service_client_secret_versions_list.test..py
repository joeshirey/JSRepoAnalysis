import os
import unittest
from unittest.mock import MagicMock
import sys
import json

from google.api_core import exceptions
from google.cloud import secretmanager_v1

# Assuming the code under test is in 'secret_manager_service_client_secret_versions_list.py'
sys.path.append(os.path.abspath('..'))
import secret_manager_service_client_secret_versions_list as secret_versions


class TestListSecretVersions(unittest.TestCase):

    def test_list_secret_versions_success(self):
        # Mock the SecretManagerServiceClient and its methods
        mock_client = MagicMock()
        mock_secret_path = MagicMock(return_value="projects/fake-project/secrets/fake-secret")
        mock_client.secret_path = mock_secret_path

        # Mock the list_secret_versions method to return a mock response
        mock_version = MagicMock()
        mock_version.name = "projects/fake-project/secrets/fake-secret/versions/1"
        mock_version.create_time = MagicMock(isoformat=MagicMock(return_value="2023-10-27T00:00:00Z"))
        mock_version.destroy_time = None
        mock_version.state = secretmanager_v1.SecretVersion.State.ENABLED

        mock_page_result = [mock_version]
        mock_client.list_secret_versions.return_value = mock_page_result

        # Patch the SecretManagerServiceClient to use the mock client
        secret_versions.secretmanager_v1.SecretManagerServiceClient = MagicMock(return_value=mock_client)

        # Call the function with test values
        project_id = "fake-project"
        secret_id = "fake-secret"
        versions = secret_versions.list_secret_versions(project_id, secret_id)

        # Assert that the function returns the expected result
        self.assertEqual(len(versions), 1)
        self.assertEqual(versions[0]["name"], "projects/fake-project/secrets/fake-secret/versions/1")
        self.assertEqual(versions[0]["create_time"], "2023-10-27T00:00:00Z")
        self.assertEqual(versions[0]["destroy_time"], None)
        self.assertEqual(versions[0]["state"], "ENABLED")

    def test_list_secret_versions_api_error(self):
        # Mock the SecretManagerServiceClient to raise an exception
        mock_client = MagicMock()
        mock_client.secret_path = MagicMock(return_value="projects/fake-project/secrets/fake-secret")
        mock_client.list_secret_versions.side_effect = exceptions.GoogleAPIError("API error")

        # Patch the SecretManagerServiceClient to use the mock client
        secret_versions.secretmanager_v1.SecretManagerServiceClient = MagicMock(return_value=mock_client)

        # Call the function and assert that it raises the expected exception
        with self.assertRaises(exceptions.GoogleAPIError):
            secret_versions.list_secret_versions("fake-project", "fake-secret")

    def test_main_no_project_id(self, capsys=None):
        # Mock sys.argv to simulate command-line arguments
        sys.argv = ["script_name", "--secret-id", "test-secret"]

        # Mock os.environ to remove the GCP_PROJECT_ID environment variable
        with unittest.mock.patch.dict(os.environ, {"GCP_PROJECT_ID": ""}):
            # Call the main function
            with self.assertRaises(SystemExit) as cm:
                secret_versions.main()
            self.assertEqual(cm.exception.code, 1)


    def test_main_success(self, capsys=None):
        # Mock sys.argv and os.environ
        sys.argv = ["script_name", "--project-id", "test-project", "--secret-id", "test-secret"]

        # Mock the list_secret_versions function
        mock_versions = [{"name": "version1"}, {"name": "version2"}]
        secret_versions.list_secret_versions = MagicMock(return_value=mock_versions)

        # Capture stdout
        captured_output = unittest.mock.StringIO()
        sys.stdout = captured_output

        # Call the main function
        secret_versions.main()

        # Restore stdout
        sys.stdout = sys.__stdout__

        # Assert that the output is as expected
        expected_output = json.dumps(mock_versions, indent=2) + "\n"
        self.assertEqual(captured_output.getvalue(), expected_output)

if __name__ == '__main__':
    unittest.main()
