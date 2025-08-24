import json
import requests
from datetime import datetime
from tools.git_file_processor import GitFileProcessor
from tools.bigquery import BigQueryRepository
from tools.evaluate_code_file import CodeEvaluator
from utils.logger import logger
from utils.exceptions import (
    GitRepositoryError,
    APIError,
)


class CodeProcessor:
    """
    Orchestrates the analysis of a single code file.

    This class is responsible for coordinating the entire analysis process for a
    given file. It fetches Git metadata, calls an external API for a detailed
    code evaluation, and then writes the combined results to a BigQuery table.
    """

    def __init__(self, settings, client, prompts):
        """
        Initializes the CodeProcessor.

        Args:
            settings: A configuration object with application settings.
            client: An initialized genai.Client instance.
            prompts: A dictionary containing pre-loaded prompt templates.
        """
        self.settings = settings
        self._bigquery_repo = None
        self.git_processor = GitFileProcessor()
        self.api_url = settings.API_URL
        self.evaluator = CodeEvaluator(
            config=settings,
            client=client,
            system_instructions=prompts["system_instructions"],
            consolidated_eval_prompt=prompts["consolidated_eval"],
            json_conversion_prompt=prompts["json_conversion"],
        )

    @property
    def bigquery_repo(self):
        if self._bigquery_repo is None:
            self._bigquery_repo = BigQueryRepository(self.settings)
        return self._bigquery_repo

    def process_file(self, file_path, regen=False):
        git_info = self._get_git_info(file_path)

        if regen:
            logger.info(
                f"Regen is true, deleting existing records for {git_info['github_link']}"
            )
            self.bigquery_repo.delete(git_info["github_link"], git_info["last_updated"])
        elif self._is_already_processed(git_info):
            logger.info(f"{file_path} already processed and up-to-date, skipping.")
            return "skipped"

        code = self._read_raw_code(file_path)
        if "Error reading file" in code:
            logger.error(f"Could not read file {file_path}, skipping.")
            return "skipped"

        analysis_result = self._analyze_file(file_path, git_info, code)

        if analysis_result is None:
            return "skipped"

        bigquery_row = self._build_bigquery_row(analysis_result, file_path, code)
        self._save_result(bigquery_row)
        return "processed"

    def _is_already_processed(self, git_info):
        github_link = git_info["github_link"]
        last_updated = git_info.get("last_updated")
        return self.bigquery_repo.record_exists(github_link, last_updated)

    def _get_git_info(self, file_path):
        git_info = self.git_processor.execute(file_path)
        if "github_link" not in git_info:
            raise GitRepositoryError(f"File not in git repository: {file_path}")
        return git_info

    def _call_analysis_api(self, github_link, code):
        """Calls the analysis API and returns the JSON response."""
        headers = {"Content-Type": "application/json"}
        data = {"github_link": github_link, "code": code}
        try:
            response = requests.post(self.api_url, headers=headers, json=data)
            response.raise_for_status()  # Raises an HTTPError for bad responses (4xx or 5xx)
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API call failed for {github_link}: {e}")
            raise APIError(f"API call failed for {github_link}: {e}")

    def _build_bigquery_row(self, analysis_result, file_path, code):
        git_info = analysis_result.get("git_info", {})
        api_analysis = analysis_result.get("analysis", {})
        assessment_data = api_analysis.get("assessment", {})

        if not assessment_data:
            raise APIError(
                f"API response for {git_info.get('github_link')} is missing the 'assessment' object."
            )

        return {
            "github_link": git_info.get("github_link"),
            "file_path": file_path,
            "github_owner": git_info.get("github_owner"),
            "github_repo": git_info.get("github_repo"),
            "product_category": api_analysis.get("product_category"),
            "product_name": api_analysis.get("product_name"),
            "language": api_analysis.get("language"),
            "overall_compliance_score": assessment_data.get(
                "overall_compliance_score"
            ),
            "evaluation_data": json.dumps(assessment_data),
            "region_tags": api_analysis.get("region_tags"),
            "raw_code": code,
            "evaluation_date": datetime.now().isoformat(),
            "last_updated": git_info.get("last_updated"),
            "branch_name": git_info.get("branch_name"),
            "commit_history": json.dumps(git_info.get("commit_history")),
            "metadata": json.dumps(git_info.get("metadata")),
            "validation_details": json.dumps(
                analysis_result.get("validation_history")
            ),
        }

    def _analyze_file(self, file_path, git_info, code):
        github_link = git_info["github_link"]
        api_response = self._call_analysis_api(github_link, code)

        # Check for an error message from the API and skip the file if present.
        if "analysis" in api_response and "error" in api_response["analysis"]:
            error_message = api_response["analysis"]["error"]
            logger.info(f"Skipping file {github_link}: {error_message}")
            return None

        # Combine git_info with the API response to pass to build_bigquery_row
        combined_result = {"git_info": git_info, **api_response}
        return combined_result

    def _read_raw_code(self, file_path):
        try:
            with open(file_path, "r") as f:
                return f.read()
        except Exception as e:
            return f"Error reading file: {e}"

    def _save_result(self, row):
        self.bigquery_repo.create(row)

    def close(self):
        if self._bigquery_repo:
            self._bigquery_repo.close()

    def analyze_file_only(self, file_path):
        """
        Analyzes a single file without any database interaction, returning the full API response.
        """
        git_info = self._get_git_info(file_path)
        github_link = git_info["github_link"]
        code = self._read_raw_code(file_path)
        if "Error reading file" in code:
            logger.error(f"Could not read file {file_path} for analysis.")
            return None
        return self._call_analysis_api(github_link, code)

    def categorize_file_only(self, file_path):
        """
        Analyzes a single file for product categorization only.
        """
        git_info = self._get_git_info(file_path)
        github_link = git_info["github_link"]
        code = self._read_raw_code(file_path)
        if "Error reading file" in code:
            logger.error(f"Could not read file {file_path} for categorization.")
            return None
        api_response = self._call_analysis_api(github_link, code)

        api_analysis = api_response.get("analysis", {})

        return {
            "indexed_source_url": github_link,
            "region_tag": api_analysis.get("region_tags", [None])[0],
            "repository_name": git_info.get("github_repo"),
            "product_category": api_analysis.get("product_category"),
            "product_name": api_analysis.get("product_name"),
            "llm_determined": True,  # This is now always determined by the API
        }
