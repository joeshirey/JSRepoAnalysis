import os
from google.cloud import bigquery
from typing import Dict, Any
from utils.logger import logger
from utils.exceptions import BigQueryError

class BigQueryRepository:
    def __init__(self, config):
        self.config = config
        try:
            self._db = bigquery.Client(project=self.config.GOOGLE_CLOUD_PROJECT)
            self.table_id = f"{self.config.GOOGLE_CLOUD_PROJECT}.{self.config.BIGQUERY_DATASET}.{self.config.BIGQUERY_TABLE}"
            logger.info("BigQuery connection opened.")
        except Exception as e:
            raise BigQueryError(f"Error initializing BigQuery client: {e}")

    def create(self, row_payload: Dict[str, Any]):
        """
        Writes a row to the BigQuery table.
        """
        try:
            errors = self._db.insert_rows_json(self.table_id, [row_payload])
            if not errors:
                logger.info(f"Successfully wrote document to BigQuery table '{self.table_id}'.")
            else:
                raise BigQueryError(f"Error writing document to BigQuery: {errors}")
        except Exception as e:
            raise BigQueryError(f"Error writing document to BigQuery: {e}")

    def read(self, github_link: str) -> Dict[str, Any]:
        """
        Reads the latest record from BigQuery for a given GitHub link.
        """
        try:
            query = f"""
                SELECT last_updated
                FROM `{self.table_id}`
                WHERE github_link = @github_link
                ORDER BY evaluation_date DESC
                LIMIT 1
            """
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("github_link", "STRING", github_link),
                ]
            )
            query_job = self._db.query(query, job_config=job_config)
            rows = list(query_job)
            if rows:
                return dict(rows[0])
            return None
        except Exception as e:
            raise BigQueryError(f"Error reading from BigQuery: {e}")

    def delete(self, github_link: str, last_updated: str):
        """
        Deletes a specific record for a given GitHub link and last_updated date.
        """
        try:
            query = f"""
                DELETE FROM `{self.table_id}`
                WHERE github_link = @github_link AND last_updated = @last_updated
            """
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("github_link", "STRING", github_link),
                    bigquery.ScalarQueryParameter("last_updated", "DATE", last_updated),
                ]
            )
            query_job = self._db.query(query, job_config=job_config)
            query_job.result()  # Wait for the job to complete
            logger.info(f"Successfully deleted record for '{github_link}' with last_updated date '{last_updated}' from BigQuery.")
        except Exception as e:
            raise BigQueryError(f"Error deleting from BigQuery: {e}")

    def close(self):
        # BigQuery client doesn't have an explicit close method.
        logger.info("BigQuery connection conceptually closed.")
