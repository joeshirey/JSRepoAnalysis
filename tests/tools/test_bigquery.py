
import unittest
from unittest.mock import patch, MagicMock
from tools.bigquery import BigQueryRepository
from utils.exceptions import BigQueryError
from config import settings

class TestBigQueryRepository(unittest.TestCase):

    def setUp(self):
        self.settings = settings
        self.settings.GOOGLE_CLOUD_PROJECT = "test-project"
        self.settings.BIGQUERY_DATASET = "test-dataset"
        self.settings.BIGQUERY_TABLE = "test-table"

    @patch('google.cloud.bigquery.Client')
    def test_init_success(self, mock_bigquery_client):
        # Arrange
        mock_client_instance = mock_bigquery_client.return_value
        
        # Act
        repo = BigQueryRepository(self.settings)

        # Assert
        mock_bigquery_client.assert_called_once_with(project="test-project")
        self.assertEqual(repo.table_id, "test-project.test-dataset.test-table")

    @patch('google.cloud.bigquery.Client')
    def test_init_failure(self, mock_bigquery_client):
        # Arrange
        mock_bigquery_client.side_effect = Exception("Test Exception")

        # Act & Assert
        with self.assertRaises(BigQueryError):
            BigQueryRepository(self.settings)

    @patch('google.cloud.bigquery.Client')
    def test_create_success(self, mock_bigquery_client):
        # Arrange
        mock_client_instance = mock_bigquery_client.return_value
        mock_client_instance.insert_rows_json.return_value = []
        repo = BigQueryRepository(self.settings)
        
        # Act
        repo.create({"test": "data"})

        # Assert
        mock_client_instance.insert_rows_json.assert_called_once_with(repo.table_id, [{"test": "data"}])

    @patch('google.cloud.bigquery.Client')
    def test_create_failure(self, mock_bigquery_client):
        # Arrange
        mock_client_instance = mock_bigquery_client.return_value
        mock_client_instance.insert_rows_json.return_value = ["error"]
        repo = BigQueryRepository(self.settings)

        # Act & Assert
        with self.assertRaises(BigQueryError):
            repo.create({"test": "data"})

    @patch('google.cloud.bigquery.Client')
    def test_read_success_with_results(self, mock_bigquery_client):
        # Arrange
        mock_client_instance = mock_bigquery_client.return_value
        mock_query_job = MagicMock()
        
        # Create a mock row that can be converted to a dict
        mock_row = MagicMock()
        mock_row.keys.return_value = ['last_updated']
        mock_row.__getitem__.side_effect = lambda key: "2025-01-01"
        
        mock_query_job.__iter__.return_value = [mock_row]
        mock_client_instance.query.return_value = mock_query_job
        repo = BigQueryRepository(self.settings)

        # Act
        result = repo.read("some_link")

        # Assert
        self.assertIsNotNone(result)
        self.assertEqual(result, {'last_updated': '2025-01-01'})

    @patch('google.cloud.bigquery.Client')
    def test_read_success_no_results(self, mock_bigquery_client):
        # Arrange
        mock_client_instance = mock_bigquery_client.return_value
        mock_query_job = MagicMock()
        mock_query_job.result.return_value = []
        mock_client_instance.query.return_value = mock_query_job
        repo = BigQueryRepository(self.settings)

        # Act
        result = repo.read("some_link")

        # Assert
        self.assertIsNone(result)

    @patch('google.cloud.bigquery.Client')
    def test_delete_success(self, mock_bigquery_client):
        # Arrange
        mock_client_instance = mock_bigquery_client.return_value
        mock_query_job = MagicMock()
        mock_client_instance.query.return_value = mock_query_job
        repo = BigQueryRepository(self.settings)

        # Act
        repo.delete("some_link", "2025-01-01")

        # Assert
        mock_query_job.result.assert_called_once()

if __name__ == '__main__':
    unittest.main()
