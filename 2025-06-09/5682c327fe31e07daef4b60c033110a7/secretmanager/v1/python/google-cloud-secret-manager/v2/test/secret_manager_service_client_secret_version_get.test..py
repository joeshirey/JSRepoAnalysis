import os
import unittest
from unittest.mock import patch, MagicMock
import json
from io import StringIO
import contextlib

# Assuming the code under test is in a file named 'secret_manager_service_client_secret_version_get.py'
import secret_manager_service_client_secret_version_get


class TestGetSecretVersion(unittest.TestCase):

    @patch('secret_manager_service_client_secret_version_get.secretmanager_v1.SecretManagerServiceClient')
    def test_get_secret_version_success(self, MockClient):
        # Mock the client and its methods
        mock_client = MockClient.return_value
        mock_response = MagicMock()
        mock_response.name = 'projects/test-project/secrets/test-secret/versions/1'
        mock_client.get_secret_version.return_value = mock_response
        mock_client.secret_version_path.return_value = 'projects/test-project/secrets/test-secret/versions/1'

        # Call the function
        response = secret_manager_service_client_secret_version_get.get_secret_version_sample(
            project_id='test-project', secret_id='test-secret', version_id='1'
        )

        # Assert that the client was called correctly
        mock_client.get_secret_version.assert_called_once_with(name='projects/test-project/secrets/test-secret/versions/1')

        # Assert that the response is as expected
        self.assertEqual(response.name, 'projects/test-project/secrets/test-secret/versions/1')

    @patch('secret_manager_service_client_secret_version_get.secretmanager_v1.SecretManagerServiceClient')
    def test_get_secret_version_failure(self, MockClient):
        # Mock the client to raise an exception
        mock_client = MockClient.return_value
        mock_client.get_secret_version.side_effect = Exception('API Error')
        mock_client.secret_version_path.return_value = 'projects/test-project/secrets/test-secret/versions/1'

        # Call the function and assert that it raises an exception
        with self.assertRaises(Exception) as context:
            secret_manager_service_client_secret_version_get.get_secret_version_sample(
                project_id='test-project', secret_id='test-secret', version_id='1'
            )

        # Assert that the exception message is as expected
        self.assertEqual(str(context.exception), 'API Error')

    @patch('secret_manager_service_client_secret_version_get.secretmanager_v1.SecretManagerServiceClient')
    def test_main_success(self, MockClient):
        # Mock environment variables and arguments
        os.environ['GCP_PROJECT_ID'] = 'test-project'
        mock_client = MockClient.return_value
        mock_response = MagicMock()
        mock_response.name = 'projects/test-project/secrets/test-secret/versions/1'
        mock_client.get_secret_version.return_value = mock_response
        mock_client.secret_version_path.return_value = 'projects/test-project/secrets/test-secret/versions/1'

        # Mock arguments
        with patch('sys.argv', ['script_name', '--secret_id', 'test-secret', '--version_id', '1']):
            # Capture stdout
            with contextlib.redirect_stdout(StringIO()) as stdout:
                # Call main function
                secret_manager_service_client_secret_version_get.main()

            # Assert that the output is as expected
            output = stdout.getvalue().strip()
            self.assertIn('projects/test-project/secrets/test-secret/versions/1', output)

    @patch('secret_manager_service_client_secret_version_get.secretmanager_v1.SecretManagerServiceClient')
    def test_main_failure(self, MockClient):
        # Mock environment variables and arguments
        os.environ['GCP_PROJECT_ID'] = 'test-project'
        mock_client = MockClient.return_value
        mock_client.get_secret_version.side_effect = Exception('API Error')
        mock_client.secret_version_path.return_value = 'projects/test-project/secrets/test-secret/versions/1'

        # Mock arguments
        with patch('sys.argv', ['script_name', '--secret_id', 'test-secret', '--version_id', '1']):
            # Capture stdout
            with contextlib.redirect_stdout(StringIO()) as stdout:
                # Call main function
                with self.assertRaises(SystemExit) as cm:
                    secret_manager_service_client_secret_version_get.main()

                # Assert that the exit code is 1
                self.assertEqual(cm.exception.code, 1)

            # Assert that the error message is printed
            output = stdout.getvalue().strip()
            self.assertIn('An error occurred: API Error', output)

    def test_main_no_project_id(self):
        # Unset the environment variable
        if 'GCP_PROJECT_ID' in os.environ:
            del os.environ['GCP_PROJECT_ID']

        # Mock arguments
        with patch('sys.argv', ['script_name', '--secret_id', 'test-secret', '--version_id', '1']):
            # Capture stdout
            with contextlib.redirect_stdout(StringIO()) as stdout:
                # Call main function
                with self.assertRaises(SystemExit) as cm:
                    secret_manager_service_client_secret_version_get.main()

                # Assert that the exit code is 1
                self.assertEqual(cm.exception.code, 1)

            # Assert that the error message is printed
            output = stdout.getvalue().strip()
            self.assertIn('Error: GCP_PROJECT_ID environment variable not set.', output)


if __name__ == '__main__':
    unittest.main()
